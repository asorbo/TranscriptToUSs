import os
import llm
from prompts import *
import asyncio
import json
import logging
import statistics
import uuid
import queue


async def segment_transcript(transcript, n_runs=10):
    instructions = SEGMENT_TRANSCRIPT_PROMPT
    #Prompt the llm to segment the transcript multiple times (run n_runs full segmentations)

    async def safe_generate():
        try:
            log_handler.logger.info("Started a segmentation prompt")
            return await gemini.generate(instructions + transcript, jsonOnly=True)
        except json.JSONDecodeError as e:
            log_handler.logger.error(f"JSONDecodeError: {e}")
            return None

    tasks = [safe_generate() for _ in range(n_runs)]
    results = await asyncio.gather(*tasks)
    runs = [r for r in results if r is not None]
    log_handler.logger.info("obtained " + str(len(runs)) + " segmentations.")
    return runs

def get_runs_with_same_amount_topics(runs):
    amounts = [len(run) for run in runs]
    mode_amount = statistics.mode(amounts)
    runs_with_same_amount_topics = []
    for run in runs:
        if len(run) == mode_amount:
            runs_with_same_amount_topics.append(run)
    len(runs_with_same_amount_topics)
    return runs_with_same_amount_topics


async def get_topic_texts(topic_list, transcript):
    batch_size = 5

    async def getAllTopicTexts_batch(batch):
        prompt = GET_TOPIC_TEXTS_PROMPT.format(batch=str(batch), transcript=transcript)
        return await gemini.generate(prompt, jsonOnly=True)

    # Create batches of topics
    batches = [topic_list[i:i + batch_size] for i in range(0, len(topic_list), batch_size)]
    # Run all batches in parallel
    tasks = [getAllTopicTexts_batch(batch) for batch in batches]
    topic_list_with_texts = await asyncio.gather(*tasks)
    # Flatten the results
    topic_texts = {}
    for batch in topic_list_with_texts:
        if isinstance(batch, list):
            for topic in batch:
                if isinstance(topic, dict) and "topic_id" in topic:
                    topic_texts[topic["topic_id"]] = topic
    return topic_texts
    
async def identify_roles(transcript):
    instructions = IDENTIFY_ROLES_PROMPT
    return await gemini.generate(instructions + transcript)

async def extract_requirements(topic_texts, roles):
    instructions = EXTRACT_REQUIREMENTS_PROMPT + str(roles) + '''
    Given text:
    '''
    async def process_batches():
        for topic in topic_texts.values():
            try:
                llm_output = await gemini.generate(instructions + topic['text'], jsonOnly=True)
                topic['requirements'] = (llm_output)
            except json.JSONDecodeError as e:
                log_handler.logger.error(f"JSONDecodeError: {e}\n" + str(llm_output))
    await process_batches()

    codes = set()
    def generate_uuid():
        code = uuid.uuid4().hex[:8]
        while code in codes:
            code = uuid.uuid4().hex[:8]
        codes.add(code)
        return code

    for topic in topic_texts.values():
        requirements = topic.get('requirements')
        if not requirements or requirements == [{}]:
            continue
        for req in requirements:
            req['requirement_id'] = generate_uuid()
            req['topic_id'] = topic['topic_id']

    return topic_texts

async def infer_missing_roles(topic_texts, roles):
    instructions = INFER_MISSING_ROLES_PROMPT + str(roles) + '''
    Given text:
    '''
    # Collect all requirements with 'unidentified-role'
    reqs_to_infer = []
    for topic in topic_texts.values():
        if 'requirements' in topic:
            for req in topic['requirements']:
                if req.get('role') == 'unidentified-role':
                    reqs_to_infer.append({
                        'topic_id': topic['topic_id'],
                        'requirement_id': req.get('requirement_id'),
                        'requirement': req.get('requirement'),
                        'role': req.get('role'),
                        'rationale': req.get('rationale')
                    })

    inferred_roles = []

    async def safe_generate_inferred_role(req_info):
        try:
            result = await gemini.generate(instructions + str(req_info), jsonOnly=True)
            # LLM may return a dict or a list
            if isinstance(result, list):
                inferred_roles.extend(result)
            elif isinstance(result, dict):
                inferred_roles.append(result)
            else:
                log_handler.logger.error(f"Unexpected LLM output: {result}")
        except json.JSONDecodeError as e:
            log_handler.logger.error(f"JSONDecodeError: {e}")
        except Exception as e:
            log_handler.logger.error(e)

    await asyncio.gather(*[safe_generate_inferred_role(req) for req in reqs_to_infer])
    # Map topic_id to topic in topic_texts (topic_id is a string key)
    for change in inferred_roles:
        try:
            topic = topic_texts[int(change['topic_id'])]
            for requirement in topic.get('requirements', []):
                if requirement and requirement['requirement_id'] == change['requirement_id'] and requirement.get('role') == "unidentified-role":
                    requirement['role'] = change.get('inferred_role', requirement['role'])
                    requirement['inferred_role_reason'] = change.get('inferred_role_reason', '')
                    requirement['is_role_inferred'] = True
        except Exception as e:
            log_handler.logger.error(f"The requirement_id included in a change generated by the LLM is incorrect and does not match any requirement. The following change could not be applied:\n{str(change)}\nException: {e}")
            continue

    return topic_texts

async def infer_missing_rationales(topic_texts, roles):
    role_map = {role_entry['role'].lower(): role_entry for role_entry in roles}
    prompts = []
    for topic in topic_texts.values():
        if 'requirements' not in topic:
            continue
        for requirement in topic['requirements']:
            if requirement and 'role' in requirement and requirement['role'] != "unidentified-role" and requirement.get('rationale') == "unidentified-rationale":
                role = role_map[requirement['role'].lower()]
                role_prompt = INFER_MISSING_RATIONALES_PROMPT + f"\nI am a {role['role']}, {role['description']}\nA {role['role']} is {role['description']}\n\nAs a {role['role']}, {requirement['requirement']}, so that ...\n\nOutput: {{\n    \"topic_id\": \"{topic['topic_id']}\" (DO NOT change this number),\n    \"requirement_id\": \"{requirement['requirement_id']}\" (DO NOT change this number),\n    \"inferred_rationale\": \"so that I ...\" (the continuation in one concise, grammatically and syntactically correct full sentence i.e. the rationale; if the subject is {role['role']} then speak in first person),\n    \"inferred_rationale_reason\": an explanation for the given rationale\n}}"
                prompts.append(role_prompt)

    inferred_rationales = []

    async def safe_generate_inferred_rationale(instructions):
        try:
            inferred = await gemini.generate(instructions, jsonOnly=True)
            inferred_rationales.append(inferred)
        except json.JSONDecodeError as e:
            log_handler.logger.error(f"JSONDecodeError: {e}")
        except Exception as e:
            log_handler.logger.error(e)

    async def process_batches():
        await asyncio.gather(*[safe_generate_inferred_rationale(prompt) for prompt in prompts])

    await process_batches()

    for change in inferred_rationales:
        topic_id = int(change['topic_id'])
        topic = topic_texts[topic_id]
        requirement = next((r for r in topic.get('requirements', []) if r.get('requirement_id') == change['requirement_id']), None)
        try:
            if requirement and requirement.get('rationale') == "unidentified-rationale":
                requirement['rationale'] = change['inferred_rationale']
                requirement['inferred_rationale_reason'] = change['inferred_rationale_reason']
                requirement['is_rationale_inferred'] = True
        except TypeError:
            log_handler.logger.error("Error: the requirement_id included in a change generated by the LLM is incorrect and does not match any requirement. The following change could not be applied:\n" + str(change))
            continue

    return topic_texts

class Requirement:
    def __init__(self, requirement_id, topic_id, requirement, role, rationale,
                 is_role_inferred=False, is_rationale_inferred=False,
                 inferred_rationale_reason='', inferred_role_reason=''):
        self.requirement_id = requirement_id
        self.topic_id = topic_id
        self.requirement = requirement
        self.role = role
        self.rationale = rationale
        self.is_role_inferred = is_role_inferred
        self.is_rationale_inferred = is_rationale_inferred
        self.inferred_rationale_reason = inferred_rationale_reason
        self.inferred_role_reason = inferred_role_reason
        self.user_story = f"As a {role}, {requirement}, {rationale}."
        self.criteria_violations = [] 

    def to_dict(self):
        return {
            'requirement_id': self.requirement_id,
            'requirement': self.requirement,
            'role': self.role,
            'rationale': self.rationale,
            'is_role_inferred': self.is_role_inferred,
            'is_rationale_inferred': self.is_rationale_inferred,
            'inferred_rationale_reason': self.inferred_rationale_reason,
            'inferred_role_reason': self.inferred_role_reason,
            'user_story': self.user_story,
            'topic_id': self.topic_id
        }

async def check_criteria_violations(requirements_set: list[Requirement]):

    instructions = CHECK_CRITERIA_VIOLATIONS_PROMPT
    # requirements_set is a list of Requirement objects
    for req in requirements_set:
        user_story = req.user_story
        if user_story:
            try:
                req.criteria_violations = await gemini.generate(instructions + " Input: " + str(user_story), jsonOnly=True)
            except Exception as e:
                log_handler.logger.error(f"Error in the generation for {req.requirement_id}: {e}")
    return requirements_set

def build_requirements_set(topic_texts_with_inferred_rationales) -> list[Requirement]:
    requirements_set = []
    for topic in topic_texts_with_inferred_rationales.values():
        if 'requirements' in topic:
            for req in topic['requirements']:
                if 'role' in req and 'rationale' in req:
                    requirement_obj = Requirement(
                        requirement_id=req.get('requirement_id'),
                        topic_id=req.get('topic_id'),
                        requirement=req.get('requirement'),
                        role=req.get('role'),
                        rationale=req.get('rationale'),
                        is_role_inferred=req.get('is_role_inferred', False),
                        is_rationale_inferred=req.get('is_rationale_inferred', False),
                        inferred_rationale_reason=req.get('inferred_rationale_reason', ''),
                        inferred_role_reason=req.get('inferred_role_reason', '')
                    )
                    requirements_set.append(requirement_obj)
    return requirements_set

async def check_set_level_violations(requirements_set):
    set_level_violations = []
    set_level_violations_prompts = SET_LEVEL_VIOLATIONS_PROMPTS

    requirements_dicts = [r.to_dict() for r in requirements_set]

    async def check_violations_async(criteria, prompt):
        try:
            result = await gemini.generate(prompt, jsonOnly=True)
            set_level_violations.extend(result)
            #TO-DO: convert the set in a map. generate an id for each violation and use it as key
            #TO-DO: for each us in the map, access the user story and include the id of the violation in a list of set-level violations
        except Exception as e:
            log_handler.logger.error(f"Error checking {criteria}: {e}")

    async def process_criteria():
        await asyncio.gather(*[
            check_violations_async(criteria, set_level_violations_prompts[criteria] + str(requirements_dicts))
            for criteria in set_level_violations_prompts
        ])

    await process_criteria()
    if set_level_violations:
        log_handler.logger.info(f"{len(set_level_violations)} set level violations found.")
    else:
        log_handler.logger.info("No set level violations found.")
    return set_level_violations

def convert_requirements_set_to_map(requirements_set):
    requirements_map = {}
    for req in requirements_set:
        requirements_map[req.requirement_id] = req.to_dict()
    return requirements_map

# Main pipeline logic as async function
async def run_pipeline(transcript, stop_event):
    output = {}

    # Segment transcript
    log_handler.logger.info("Pipeline status - Part 1/10 started: segment transcript")
    runs = await segment_transcript(transcript, n_runs=5)
    if not runs:
        log_handler.logger.error("Failed to segment transcript.")
        return
    log_handler.logger.info("Pipeline status - Part 1/10 completed: segment transcript")

    if log_handler.is_stop_requested(stop_event):
        return
    
    # Select runs with the most frequent number of topics
    log_handler.logger.info("Pipeline status - Part 2/10 started: select runs with number of topics = mode")
    runs_with_same_amount_topics = get_runs_with_same_amount_topics(runs)
    if not runs_with_same_amount_topics:
        log_handler.logger.error("No runs found with the most frequent number of topics.")
        return
    log_handler.logger.info("Pipeline status - Part 2/10 completed: select runs with number of topics = mode")

    if log_handler.is_stop_requested(stop_event):
        return
    
    # Use the first run with the mode number of topics for further processing
    selected_topic_list = runs_with_same_amount_topics[0]
    output['topic_list'] = selected_topic_list.copy()

    # Get topic texts and speaker turns
    log_handler.logger.info("Pipeline status - Part 3/10 started: Get topic texts and speaker turns")
    topic_texts = await get_topic_texts(selected_topic_list, transcript)
    if not topic_texts:
        log_handler.logger.error("Failed to get topic texts.")
        return
    output['topic_texts'] = topic_texts.copy()
    log_handler.logger.info("Pipeline status - Part 3/10 completed: Get topic texts and speaker turns")

    if log_handler.is_stop_requested(stop_event):
        return
    
    # Identify roles
    log_handler.logger.info("Pipeline status - Part 4/10 started: Identify roles")
    roles = await identify_roles(transcript)
    #convert roles to a map with role as key
    roles_map = {role_entry['role'].lower(): role_entry for role_entry in roles}
    output['roles'] = roles_map.copy()
    log_handler.logger.info("Pipeline status - Part 4/10 completed: Identify roles")

    if log_handler.is_stop_requested(stop_event):
        return

    # Extract requirements
    log_handler.logger.info("Pipeline status - Part 5/10 started: extract requirements")
    topic_texts_with_requirements = await extract_requirements(topic_texts, roles)
    log_handler.logger.info("Pipeline status - Part 5/10 completed: extract requirements")

    if log_handler.is_stop_requested(stop_event):
        return

    # Infer missing roles
    log_handler.logger.info("Pipeline status - Part 6/10 started: Infer missing roles")
    topic_texts_with_inferred_roles = await infer_missing_roles(topic_texts_with_requirements, roles)
    log_handler.logger.info("Pipeline status - Part 6/10 completed: Infer missing roles")

    if log_handler.is_stop_requested(stop_event):
        return
    
    # Infer missing rationales
    log_handler.logger.info("Pipeline status - Part 7/10 started: Infer missing rationales")
    topic_texts_with_inferred_rationales = await infer_missing_rationales(topic_texts_with_inferred_roles, roles)
    log_handler.logger.info("Pipeline status - Part 7/10 completed: Infer missing rationales")

    if log_handler.is_stop_requested(stop_event):
        return

    # Build Requirement objects
    log_handler.logger.info("Pipeline status - Part 8/10 started: Generate set of Requirement objects")
    requirements_set = build_requirements_set(topic_texts_with_inferred_rationales)
    log_handler.logger.info("Pipeline status - Part 8/10 completed: Generate set of Requirement objects")

    if log_handler.is_stop_requested(stop_event):
        return
    
    # Check criteria violations for each requirement (optional, call if needed)
    log_handler.logger.info("Pipeline status - Part 9/10 started: Check criteria violations for each requirement")
    requirements_set = await check_criteria_violations(requirements_set)
    log_handler.logger.info("Pipeline status - Part 9/10 completed: Check criteria violations for each requirement")

    if log_handler.is_stop_requested(stop_event):
        return

    requirements_map = convert_requirements_set_to_map(requirements_set)

    output['requirements'] = requirements_map

    # Check set level violations
    log_handler.logger.info("Pipeline status - Part 10/10 started: Check set level violations")
    set_level_violations = await check_set_level_violations(requirements_set)
    output['set_level_violations'] = set_level_violations
    log_handler.logger.info("Pipeline status - Part 10/10 completed: Check set level violations")
    
    output_dir = "/tmp/output"
    os.makedirs(output_dir, exist_ok=True)
    #dump output to a json file in the folder output
    with open(f"{output_dir}/output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

class LogHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        self.logger = logging.getLogger("stream_logger")
        self.configure_logger()

    def configure_logger(self):
        self.logger.setLevel(logging.INFO)
        handler = self
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)

    def stop_logging_stream(self):
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except queue.Empty:
                break
        done_message = "event: done\ndata:\n\n"
        self.log_queue.put(done_message)

    def is_stop_requested(self, stop_event):
        if stop_event.is_set():
            self.logger.info("Execution stopped by user")
            self.stop_logging_stream()
            return True
        return False  

def start_execution(transcript, stop_event, log_queue, api_key, runs_per_minute):
    global gemini
    gemini = llm.LLM(api_key, runs_per_minute)

    # Remove non-printable characters except newlines
    transcript = ''.join(c for c in transcript if c.isprintable() or c == '\n')
    global log_handler
    log_handler = LogHandler(log_queue)
    log_handler.logger.info("Starting execution")
    asyncio.run(run_pipeline(transcript, stop_event))
    log_handler.logger.info("Pipeline status: Execution completed")

