
# --- PROMPT DEFINITIONS ---

SEGMENT_TRANSCRIPT_PROMPT = '''
three experts segment the following interview transcript into distinct topics.
Each expert is told to ensure consistency by following these rules:
Each segment should contain sentences discussing the same general topic.
A new segment should only start if the conversation meaningfully shifts.
If a topic gradually changes, consider whether it still relates to the previous one before splitting.
Avoid creating segments that are shorther than 2 minutes (end_time - start_time < 2 minutes) unless it is very clear that a topic shift is happening and *do not* create segments that are longer than 4 minutes(end_time - start_time > 4 minutes).
For each topic generate 10 possible labels, then select the label that appeared most frequently (the statistical mode).
Use clear and concise labels, drawing from the content rather than inventing new terms. If the topic could be a functionality or a requirement ensure the label clearly reflects the functionality.

Every time an expert detects a topic shift all three experts must compare their work and reach an agreement. A split cannot be made if all three experts do not agree. If all experts agree the split is made (and included in the output) only once, all the experts then continue from the end time of that split onwards-
Do NOT start a new topic in the middle of a speaker turn! each returned topic must include only whole speaker turns.
Do NOT stop until all speaker turns have been processed.
The first topic must start at the beginning of the transcript.
The last topic must end at the end of the transcript.
return a list of the segments in json format. Do not include the text in the output.
A segment **must** include all and only this: (start_time, end_time, summary, label) **exactly in the following valid json format**
VALID JSON OUTPUT FORMAT (MANDATORY):
[
  {
    "topic_id": <integer>,
    "start_time": "mm:ss",
    "end_time": "mm:ss",
    "label": "topic label"
  }
]
'''

GET_TOPIC_TEXTS_PROMPT = '''
Extract the text of the given topics without modifying it: {batch}
and return the same dictionary with the additional "text" data containing the full text of the topic (ensure all backslashes are removed so that the returned json is valid).
Additionally, for each topic, split on the basis of speaker-turn (meaning every time a different speaker talks, it is a new speaker turn).
Provide the topics in the following format, performing escapes if necessary, ensuring it is *valid JSON*:
[
    {{
        "topic_id": 1,
        "start_time": "xx:xx",
        "end_time": "xx:xx",
        "label": "The topic label",
        "text": "The text of the whole topic (all the speaker turns combined for a given topic)",
        "speaker_turns": [
            {{
                "speaker": "speaker name",
                "text": "text spoken by the speaker"
            }}
        ]
    }}
]
transcript: {transcript}
'''


IDENTIFY_ROLES_PROMPT = '''
This is an extract of a requirements elicitation session. You are an expert requirements engineer and your goal is your goal is to identify all distinct roles mentioned or implied with respect to the described system.
You do not care about the roles of speakers within the interview, you care about the abstract roles within the described system.
For each role, provide:
-The role name.
-A brief and concrete description of the role’s responsibilities or context.
-A first-person general goal description focused on key intents, summarizing what someone in that role fundamentally wants to achieve within the system, phrased from their own point of view.

A role can be a job title or a stakeholder type, avoiding generic terms like "User".
The general goal should capture the intent or need driving that role’s interaction with the system written as 2–3 cohesive sentences, not a checklist of features or tasks. Avoid listing multiple goals with commas; instead, combine them into a smooth narrative.
*Ensure the output is in valid json, in particular ensure that properties are always correctly wrapped by double quotes*
These are some correct examples of outputs:
Output:
[
{
    "role": "Staff Member",
    "description": "An individual who performs various tasks within an organization, such as operational duties or customer service roles.",
    "general_goal": "I want to know my schedule well in advance so I can manage my personal commitments. It's important that I can update my availability easily if unexpected situations arise. I want to avoid scheduling conflicts and feel confident that my assigned tasks align with what I can handle."
},
{
    "role": "Team Leader",
    "description": "The person responsible for coordinating team activities, managing availability, and ensuring smooth day-to-day operations.",
    "general_goal": "I need to ensure that the team is adequately staffed without anyone being overworked. I want to identify and resolve any coverage gaps quickly to prevent disruptions. My goal is to maintain efficient operations while supporting team members’ well-being."
}
]
Given text:
'''

EXTRACT_REQUIREMENTS_PROMPT = '''
This is an extract of a requirements elicitation session. You are an expert requirements engineer and your goal is to identify all the information concerning requirements, *not manual user operations* from the text.
You must not omit any requirement-relevant information that is mentioned in the text. You must only refer to information mentioned in the given text.
If the information is given in the text clearly state who wants a given functionality (or for whom it is made for) assign a role from the set of provided roles. Otherwise, do not guess who wants it and simply write 'unidentified-role'.
If the information is given in the text clearly state why the user wants a given functionality (what the purpose of the functionality is) otherwise do not guess the reason it and simply write 'unidentified-rationale'.
Report textually(no modifications) the sentence or sentences in the input that you are extracting this information from.
You may return an empty list [] if there are no requirements mentioned in the text.
If requirements are present format them in the format given in the examples. Nothe that they must always begin with "I want".
Example: "There must be an overview functionality to allow chefs to see all active orders so they can plan ahead..."
*Ensure the output is in valid json, in particular ensure that properties are always correctly wrapped by double quotes and that curly braces are handled correctly*
Output: {
    "requirement_id": none,
    "requirement": "I want an overview functionality that shows all active orders",
    "role": "chef",
    "rationale": "so that I can plan ahead",
    "origin_sentences": ["yeah, and there should be a section where we see an overview of all active orders"]
}
Example": To make sure we don't miss an incoming order there should be a a notification sound every time a new order is placed.
Output: {
    "requirement_id": none,
    "requirement": "I want a notification sound to be produced every time a new order is placed",
    "role": "unidentified-role",
    "rationale": "so that I don't miss any incoming orders",
    "origin sentences": ["we need to be notified when a new order is placed", "notifications for new orders should make a sound"]
}
Roles: '''

INFER_MISSING_ROLES_PROMPT = '''
This is an extract of a requirements elicitation session. You are an expert requirements engineer and your goal is to identify The missing roles for the given requirements.

It is not clear for what role some of the given requirements should be implemented (role = 'unidentified-role'). Namely, who wants a given functionality (or for whom it is made for).
If the functionality matches one of the specified roles, assign the role and explain why that is the correct role. If the role cannot be deduced simply leave it as 'unidentified-role'.
A role is considered a match if the given functionality logically supports, benefits, or aligns with the responsibilities or goals described for the role, even if the role is not explicitly mentioned in the text.
When explaining why you are inferring try to relate to the role description or other similar functionalities with the same role.
Do not include already defined roles or roles that are stil undefined.
You must return the topic_id and the requirement_id exactly as provided in the input without changing it.*
*Ensure the output is in valid json, in particular ensure that properties are always correctly wrapped by double quotes*
Examples of correct outputs:
[
{
"topic_id": "56",
"requirement_id": "56345ad6",
"inferred_role": "chef",
"inferred_role_reason": "The chef role was inferred because the description of the chef role mentiones that information regarding new orders is directly relevant for the chef"
},
{
"topic_id": "43",
"requirement_id": "56345ad5",
"inferred_role": "chef",
"inferred_role_reason": "The chef role was inferred because a similar requirement, namely #req{requirement_id} has the role chef"
},
...]

Roles: '''

INFER_MISSING_RATIONALES_PROMPT = '''
A rationale (the part of a user story that begins with 'so that') may express one of three things:
- Clarification of means: The end explains the reason of the means. Example: "As a User, I want to edit a record, so that I can correct any mistakes."
- Dependency on another functionality: The end (implicitly) references a functionality which is required for the means to be realized. Although dependency is an indicator of a bad quality criteria, having no dependency at all between requirements is practically impossible. Example: "‘‘As a User, I want to open the interactive map, so that I can see the location of landmarks.’’ The end implies the existence of a landmark database"
- Quality requirement: The end communicates the intended qualitative effect of the means. Example: "As a User, I want to sort the results, so that I can more easily review the results" indicates that the means contributes maximizing easiness.
I am a {role_role}, {role_description}
A {role_role} is {role_description}

As a {role_role}, {requirement_text}, so that ...

Output: {{
    "topic_id": "{topic_id}" (DO NOT change this number),
    "requirement_id": "{requirement_id}" (DO NOT change this number),
    "inferred_rationale": "so that I ..." (the continuation in one concise, grammatically and syntactically correct full sentence i.e. the rationale; if the subject is {role_role} then speak in first person),
    "inferred_rationale_reason": an explanation for the given rationale
}}
'''

CHECK_CRITERIA_VIOLATIONS_PROMPT = '''
You are an expert requirements engineer evaluating a user story for compliance with 8 criteria.
Recall that a user story is structured as such: "AS A [role], I WANT [means], SO THAT [ends]."

Here are the 8 criteria:
1. Well-formed: A user story includes at least a role and a means.
2. Atomic: A user story expresses a requirement for exactly one feature. *For the atomic criterion only look at the means and ignore the ends.*
3. Minimal: A user story contains nothing more than role, means, and (optionally) ends. Any additional information such as comments, descriptions of the expected behavior, or testing hints should be left out.
4. Conceptually sound: The means expresses a feature and the ends should describe its purpose.
5. Problem-oriented: A user story only specifies the problem, not the solution to it. Shall avoid implementation details.
6. Unambiguous: A user story avoids terms or abstractions that lead to multiple interpretations. If any of the four ambiguity types are detected include them in the ambiguity_types list and give a reason for each of them.
Ambiguity can be of four types:
- Lexical: a word/phrase has >= 2 dictionary meanings. It arises when a word can have multiple meanings. Lexical ambiguity can occur when there is homonymy or polysemy. Homonymy: the ambiguity stems from words with different meanings that have the same phonetic and written representation. Polysemy: when the same word can take several different meanings.
- Syntactical: It arises when the words within a sentence can be given different structures, yielding multimple interpretations.
- Semantic: sentence meaning depends external context. It arises when the meaning of a sentence can vary when put in different contexts.
- Pragmatic: meaning can shift within the same context. It arises when the meaning of a sentence can vary within one context.
7. Full sentence: A user story is a well-formed full sentence.
8. Estimatable: A story does not denote a coarse-grained requirement that is difficult to plan and prioritize. It should be small enough to estimate.

Please:
Check the input user story against each criterion:
- If a criterion is violated, set isViolated to true and provide a reason why.
- Suggest a revised version that fixes the issue making as little changes as possible, maintaining correct grammar and syntax, and if possible avoiding violating any of the other criteria. The improvement field should contain a string or a slist of strings in case the improvement splits the original user story into two or more.
Only if the suggested fixes for each criteria do not conflict with eachother, provide a final revised version as either a string or list of strings taking into consideration all the criteria violations previously identified.

Examples of correct outputs for each criteria:
Each segment should contain sentences discussing the same general topic.
A new segment should only start if the conversation meaningfully shifts.
If a topic gradually changes, consider whether it still relates to the previous one before splitting.
Avoid creating segments that are shorther than 2 minutes (end_time - start_time < 2 minutes) unless it is very clear that a topic shift is happening and *do not* create segments that are longer than 4 minutes(end_time - start_time > 4 minutes).
For each topic generate 10 possible labels, then select the label that appeared most frequently (the statistical mode).
Use clear and concise labels, drawing from the content rather than inventing new terms. If the topic could be a functionality or a requirement ensure the label clearly reflects the functionality.

Every time an expert detects a topic shift all three experts must compare their work and reach an agreement. A split cannot be made if all three experts do not agree. If all experts agree the split is made (and included in the output) only once, all the experts then continue from the end time of that split onwards-
Do NOT start a new topic in the middle of a speaker turn! each returned topic must include only whole speaker turns.
Do NOT stop until all speaker turns have been processed.
The first topic must start at the beginning of the transcript.
The last topic must end at the end of the transcript.
return a list of the segments in json format. Do not include the text in the output.
A segment **must** include all and only this: (start_time, end_time, summary, label) **exactly in the following valid json format**
{
    "topic_id": "an incremental integer id"
    "start_time": "xx:xx",
    "end_time": "xx:xx"
    "label": "The topic label",
}
'''

CHECK_CRITERIA_VIOLATIONS_PROMPT = '''
You are an expert requirements engineer evaluating a user story for compliance with 8 criteria.
Recall that a user story is structured as such: "AS A [role], I WANT [means], SO THAT [ends]."

Here are the 8 criteria:
1. Well-formed: A user story includes at least a role and a means.
2. Atomic: A user story expresses a requirement for exactly one feature. *For the atomic criterion only look at the means and ignore the ends.*
3. Minimal: A user story contains nothing more than role, means, and (optionally) ends. Any additional information such as comments, descriptions of the expected behavior, or testing hints should be left out.
4. Conceptually sound: The means expresses a feature and the ends should describe its purpose.
5. Problem-oriented: A user story only specifies the problem, not the solution to it. Shall avoid implementation details.
6. Unambiguous: A user story avoids terms or abstractions that lead to multiple interpretations. If any of the four ambiguity types are detected include them in the ambiguity_types list and give a reason for each of them.
Ambiguity can be of four types:
- Lexical: a word/phrase has >= 2 dictionary meanings. It arises when a word can have multiple meanings. Lexical ambiguity can occur when there is homonymy or polysemy. Homonymy: the ambiguity stems from words with different meanings that have the same phonetic and written representation. Polysemy: when the same word can take several different meanings.
- Syntactical: It arises when the words within a sentence can be given different structures, yielding multimple interpretations.
- Semantic: sentence meaning depends external context. It arises when the meaning of a sentence can vary when put in different contexts.
- Pragmatic: meaning can shift within the same context. It arises when the meaning of a sentence can vary within one context.
7. Full sentence: A user story is a well-formed full sentence.
8. Estimatable: A story does not denote a coarse-grained requirement that is difficult to plan and prioritize. It should be small enough to estimate.

Please:
Check the input user story against each criterion:
- If a criterion is violated, set isViolated to true and provide a reason why.
- Suggest a revised version that fixes the issue making as little changes as possible, maintaining correct grammar and syntax, and if possible avoiding violating any of the other criteria. The improvement field should contain a string or a slist of strings in case the improvement splits the original user story into two or more.
Only if the suggested fixes for each criteria do not conflict with eachother, provide a final revised version as either a string or list of strings taking into consideration all the criteria violations previously identified.

Examples of correct outputs for each criteria:
Input:
I want to see an error when I cannot see recommendations after I upload an article
Output (extract):
"Well-formed": {
    "isViolated": true,
    "reason": "The user story does not adhere to the correct syntax, as it has no role.",
    "improvement": None
  }

Input:
As a User, I am able to click a particular location from the map and thereby perform a search of landmarks associated with that latitude longitude combination
Output (extract):
  "Atomic": {
    "isViolated": true,
    "reason": "The user story consists of two separate requirements: the act of clicking on a location and the display of associated landmarks. This user story should be split into two. ",
    "improvement": [
      "As a User, I’m able to click a particular location from the map",
      "As a User, I’m able to see landmarks associated with the latitude and longitude combination of a particular location"
    ]
  }

Input:
As a care professional, I want to see the registered hours of this week (split into products and activities). See: Mockup from Alice NOTE—first create the overview screen—then add validationsOutput (extract):
  "Minimal": {
    "isViolated": true,
    "reason": "The user story, aside from a role and means, it includes extra information: a reference to an undefined mockup and a note on how to approach the implementation.",
    "improvement": "As a care professional, I want to see the registered hours of this week."
  }

Input:
As a User, I want to open the interactive map, so that I can see the location of landmarks
Output (extract):
  "Conceptually sound": {
    "isViolated": true,
    "reason": "The end is actually a dependency on another (hidden) functionality, which is required in order for the means to be realized, implying the existence of a landmark database which is not mentioned in any of the other stories. A significant additional feature that is erroneously represented as an end, but should be a means in a separate user story.",
    "improvement": [
      "As a User, I want to open the interactive map",
      "As a User, I want to see the location of landmarks on the interactive map."
      ]
  }

Input:
As a Coach, I want to ensure players attend training, so that the team performs well.
Output:
"Conceptually sound": {
  "isViolated": true,
  "reason": "The means does not describe a concrete system feature but rather an abstract goal. 'Ensuring players attend training' is a desired outcome, not a concrete feature that the system can provide. This lacks conceptual clarity and should be reformulated to describe the actual functionality that supports this goal.",
  "improvement": "As a Coach, I want to track player attendance at training sessions, so that the team performs well."
}

Input:
As a Referee, I want to submit match reports, so that match reports are submitted.
Output (extract):
"Conceptually sound": {
  "isViolated": true,
  "reason": "The end merely repeats the means in different words and does not explain the rationale or value behind submitting match reports. A proper end should express the benefit or purpose of this action.",
  "improvement": "As a Referee, I want to submit match reports, so that match outcomes and incidents are documented for review and record-keeping."
}

Input:
As a care professional I want to save a reimbursement—add save button on top right (never grayed out)
Output (extract):
  "Problem-oriented": {
    "isViolated": true,
    "reason": "The user story includes implementation details (a solution) within the user story text. A user story should specify only the problem. If absolutely necessary, implementation hints can be included as comments or descriptions. Aside from breaking the minimal quality criteria,",
    "improvement": "As a care professional, I want to save a reimbursement."
  }
Input:
As a User, I am able to edit the content that I added to a person’s profile page.
Output (extract):
  "Unambiguous": {
    "isViolated": true,
    "ambiguity_types": ["lexical"],
    "reason": "'Content' is a polysemous term: it can refer to various types of media such as audio, video, or text. This lexical ambiguity makes the user story unclear, as it does not specify which type(s) of content are meant. The user story should explicitly mention which media are editable.",
    "improvement": "As a User, I am able to edit video, photo, and audio content that I added to a person’s profile page."
  }
Input:
As a manager, I want the dashboard to quickly show how sales figures act in real time, so that I can decide on promotions.
Output (extract):
"Unambiguous": {
    "isViolated": true,
    "types": ["Lexical", "Syntactical"],
    "reason": "The term 'quickly' could refer to UI response time or frequency of data refresh(lexical ambiguity due to ploysemy). The clause 'in real time' can attach to ‘shows’ or ‘act’ (syntactical).",
    "improvement": "As a manager, I want the dashboard to update sales figures every minute so that I can decide on promotions within five minutes."
  }

Input:
Server configuration
Output (extract):
  "Full sentence": {
    "isViolated": true,
    "reason": "The user story is not expressed as a full sentence (in addition to not complying with syntactic quality). A user story should read like a full sentence, without typos or grammatical errors. By reformulating the feature as a full sentence user story, it will automatically specify what exactly needs to be configured.",
    "improvement": "As an Administrator, I want to configure the server’s sudo-ers."
  }

Input:
As a care professional I want to see my route list for next/future days, so that I can prepare myself (for example I can see at what time I should start traveling)
Output (extract):
  "Estimatable": {
    "isViolated": true,
    "reason": "A user story should not be so large that estimating and planning it with reasonable certainty becomes impossible. requests a route list so that care professionals can prepare themselves. While this might be just an unordered list of places to go to during a workday, it is just as likely that the feature includes ordering the routes algorithmically to minimize distance travelled and/or showing the route on a map. These many functionalities inhibit accurate estimation and call for splitting the user story into multiple user stories.",
    "improvement": [
      "As a Care Professional, I want to see my route list for next/future days, so that I can prepare myself",
      "As a Manager, I want to upload a route list for care professionals."
    ]
  }

Only use the given context to provide an improvement when a constraint is violated. Attain to the facts presented in the input user story or the context.
The output must be exactly in the provided output schema.
Output schema:
{
  "Well-formed": {
    "isViolated": "a boolean value",
    "reason": "If isViolated is set to true, the reason why the criterion is violated",
    "improvement": None #Do not suggest an improvement for the well-formed criterion
  },

  "Atomic": {
    "isViolated": "a boolean value",
    "reason": "If isViolated is set to true, the reason why the criterion is violated",
    "improvement": [a list of atomic requirements as strings]
  },

  "Minimal": {
    "isViolated": "a boolean value",
    "reason": "If isViolated is set to true, the reason why the criterion is violated",
    "improvement": "The improved version of the requirement"
  },

  "Conceptually sound": {
    "isViolated": "a boolean value",
    "reason": "If isViolated is set to true, the reason why the criterion is violated",
    "improvement": "The improved version of the requirement"
  },

  "Problem-oriented": {
    "isViolated": "a boolean value",
    "reason": "If isViolated is set to true, the reason why the criterion is violated",
    "improvement": "The improved version of the requirement"
  },

  "Unambiguous": {
    "isViolated": "a boolean value",
    "ambiguity_types": [one or more types from the set (lexical, syntactical, semantic, pragmatic)],
    "reason": "If isViolated is set to true, how each ambiguity type specified in ambiguity_types is present",
    "improvement": "The improved version of the requirement"
  },

  "Full sentence": {
    "isViolated": "a boolean value",
    "reason": "If isViolated is set to true, the reason why the criterion is violated",
    "improvement": "The improved version of the requirement"
  },

  "Estimatable": {
    "isViolated": "a boolean value",
    "reason": "If isViolated is set to true, the reason why the criterion is violated",
    "improvement": "The improved version of the requirement"
  }

  "overall_improvement": {
    "reason": "If isViolated is set to true for any of the previous criteria, summarize the reasons for the violations",
    "improvement": "The improved version of the requirement taking into consideration all the proposed improvements" | null (if improvements conflict with eachother)
  }
}


Context:
'''

SET_LEVEL_VIOLATIONS_PROMPTS = {
        'uniqueness': '''
        You are an expert requirements engineer evaluating a set of user stories for compliance with the uniqueness criterion.
        When scanning for criteria violations you prioritize recall, meaning that it is better to include a violation you are uncertain about than potentially missing an actual violation.
        Uniqueness criterion: A user story is unique when no other user story in the given set is (semantically) equal or too similar.
        If subsets (groups of 2 or more) of user stories violate the uniqueness criterion explain why they violate it and add them to the output, otherwise do not include them in the output.

        The output must be exactly in the provided output schema.
        for each subset that violates the criterion add an object to the returned list as specified in the schema.
        The list user_stories_subset must include the user stories objects exactly as provided, *do not change any attribute*
        Output schema:
        [
        {
        set_level_violation = "uniqueness",
        reason = "a string motivating why the criterion is violated"(Use formulations such as 'may be' violated expressing that these are potential violations and not facts) ,
        user_stories_subset = [a list of user stories objects that violate the uniqueness criterion ]
        },
        ...
        ]

        Set of user stories:

        ''',
                'conflict-free': '''
        You are an expert requirements engineer evaluating a set of user stories for compliance with the conflict-free criterion.
        When scanning for criteria violations you prioritize recall, meaning that it is better to include a violation you are uncertain about than potentially missing an actual violation.
        Conflict-free criterion: A user story is conflicting when it is inconsistent with one or more other user stories in the given set.
        If subsets (groups of 2 or more) of user stories violate the conflict-free criterion explain why they violate it and add them to the output, otherwise do not include them in the output.

        The output must be exactly in the provided output schema.
        for each subset that violates the criterion add an object to the returned list as specified in the schema.
        The list user_stories_subset must include the user stories objects exactly as provided, *do not change any attribute*
        Output schema:
        [
        {
        set_level_violation = "conflict-free",
        reason = "a string motivating why the criterion is violated"(Use formulations such as 'may be' violated expressing that these are potential violations and not facts) ,
        user_stories_subset = [a list of user stories objects that violate the conflict-free criterion ]
        },
        ...
        ]

        Set of user stories:

        '''
    }
