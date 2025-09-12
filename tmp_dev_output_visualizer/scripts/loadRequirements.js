function loadAdditionalInformation(data, req) {
    const additional = document.createElement("div");
    additional.className = "additional_information";
    
    roleInfo = loadAdditionalRoleInformation(data, req)
    rationaleInfo = loadAdditionalRationaleInformation(data, req)
    
    additional.appendChild(roleInfo);
    additional.appendChild(rationaleInfo);

    return additional;
}

function loadAdditionalRoleInformation(data, req){
    // --- Role information block ---
    const roleInfo = document.createElement("div");
    roleInfo.className = "role_information";

    // Role header
    const roleHeader = document.createElement("h5");
    roleHeader.textContent = "Role:";

    // Role description div
    const roleDescDiv = document.createElement("div");

    // Role name span
    const roleNameSpan = document.createElement("span");
    roleNameSpan.textContent = req.role;

    // Role description text
    const roleKey = req.role ? req.role.toLowerCase().trim() : "";
    const roleObj = (data.roles && data.roles[roleKey]) ? data.roles[roleKey] : null;
    const roleDescriptionText = roleObj && roleObj.description ? roleObj.description : "No description available for this role.";

    roleDescDiv.appendChild(roleNameSpan);
    roleDescDiv.appendChild(document.createTextNode(`: ${roleDescriptionText}`));

    // Role inference reasoning
    const roleReasonLabel = document.createElement("span");
    roleReasonLabel.className = "requirement_label";
    roleReasonLabel.textContent = "Inference reasoning: ";

    const roleReason = document.createElement("span");
    roleReason.textContent = req.is_role_inferred === false
        ? "This role was mentioned in the topic segment"
        : req.inferred_role_reason || "";

    // Assemble role block
    roleInfo.appendChild(roleHeader);
    roleInfo.appendChild(roleDescDiv);
    roleInfo.appendChild(roleReasonLabel);
    roleInfo.appendChild(roleReason);

    return roleInfo;
}

function loadAdditionalRationaleInformation(data, req){
    // --- Rationale information block ---
    const rationaleInfo = document.createElement("div");
    rationaleInfo.className = "rationale_information";

    // Rationale header
    const rationaleHeader = document.createElement("h5");
    rationaleHeader.textContent = "Rationale:";

    // Rationale inference reasoning
    const rationaleLabel = document.createElement("span");
    rationaleLabel.className = "requirement_label";
    rationaleLabel.textContent = "Inference reasoning: ";

    const rationaleReason = document.createElement("span");
    rationaleReason.textContent = req.is_rationale_inferred === false
        ? "This rationale was mentioned in the topic segment"
        : req.inferred_rationale_reason || "";

    // Assemble rationale block
    rationaleInfo.appendChild(rationaleHeader);
    rationaleInfo.appendChild(rationaleLabel);
    rationaleInfo.appendChild(rationaleReason);

    return rationaleInfo;
}

function createTopRow(req){
    const topRow = document.createElement("div");
    topRow.classList.toggle("top_row")
    const title = document.createElement("h4");
    title.textContent = `Requirement #${req.requirement_id}`;

    const topicSpan = document.createElement("span");
    topicSpan.textContent = `Topic ${req.topic_id}`;

    topRow.appendChild(title);
    topRow.appendChild(topicSpan);
    return topRow
}

function loadContent(req){
    const content = document.createElement("div");
    content.className = "requirement_content";

    const asSpan = document.createElement("span");
    asSpan.textContent = "As a ";

    const roleSpan = document.createElement("span");
    roleSpan.className = "role";
    roleSpan.textContent = req.role;
    roleSpan.setAttribute("is_role_inferred", req.is_role_inferred);
    if (req.is_role_inferred == true) {
        roleSpan.setAttribute("title", "Inferred by LLM - click to see reasoning");
    }

    const reqSpan = document.createElement("span");
    reqSpan.className = "requirement";
    reqSpan.textContent = `, ${req.requirement}, `;

    const rationaleSpan = document.createElement("span");
    rationaleSpan.className = "rationale";
    rationaleSpan.textContent = `${req.rationale}`;
    rationaleSpan.setAttribute("is_rationale_inferred", req.is_rationale_inferred);
    if (req.is_rationale_inferred == true) {
        rationaleSpan.setAttribute("title", "Inferred by LLM - click to see reasoning");
    }

    // Assemble content row
    content.appendChild(asSpan);
    content.appendChild(roleSpan);
    content.appendChild(reqSpan);
    content.appendChild(rationaleSpan);

    return content
}

function countIndividualCriteriaViolations(req) {
    const violations = req.criteria_violations;
    if (!violations || typeof violations !== "object") {
        return 0;
    }

    return Object.values(violations)
                 .filter(criterion => criterion && criterion.isViolated)
                 .length;
}

function loadFooter(criteriaViolationCounter, req){
    const footer = document.createElement("div");
    footer.className = "requirement_footer";

    const hsButton = document.createElement("button");
    hsButton.className = "openHistory";
    hsButton.textContent = "HS";
    hsButton.addEventListener("click", () => {
        openPipelineModal(req.is_role_inferred, req.is_rationale_inferred);
    });

    const expandButton = document.createElement("button");
    expandButton.className = "expandButton";

    if (criteriaViolationCounter != null){
        footer.append(criteriaViolationCounter);
    }
    footer.appendChild(hsButton);
    footer.appendChild(expandButton);
    
    return footer
}

function makeIndividualCriteriaViolationCounter(req){
    const individualCriteriaViolationsCount = countIndividualCriteriaViolations(req);
    if (individualCriteriaViolationsCount == 0){
        return null;
    }
    const criteriaViolationCounter = document.createElement("span");
    criteriaViolationCounter.classList.add("console-error");
    const violationIcon = document.createElement("img");
    violationIcon.src = "cross.svg";

    criteriaViolationCounter.append(violationIcon);
    criteriaViolationCounter.append(individualCriteriaViolationsCount);

    return criteriaViolationCounter;
}

function loadCriteriaViolations(req, criteriaViolationCounter) {
    const criteriaViolations = req.criteria_violations;

    if (criteriaViolationCounter == null || !criteriaViolations || Object.keys(criteriaViolations).length === 0) {
        return;
    }

    const outer = document.createElement("div");
    outer.className = "individual_criteria_violations";

    const header_wrapper = document.createElement("div");
    header_wrapper.appendChild(criteriaViolationCounter.cloneNode(true));

    // Heading
    const heading = document.createElement("h5");
    heading.textContent = "individual user story QUS criteria violations:";
    header_wrapper.appendChild(heading);
    outer.append(header_wrapper);

    // Wrapper and inner container (matches your template structure)
    const wrapper = document.createElement("div");
    const inner = document.createElement("div");
    wrapper.appendChild(inner);

    // Safety: ensure criteriaViolations is an object
    if (criteriaViolations && typeof criteriaViolations === "object") {
        Object.entries(criteriaViolations).forEach(([name, crit]) => {
            // only create blocks for violated criteria
            if (!crit || crit.isViolated !== true) return;

            const violationDiv = document.createElement("div");
            violationDiv.className = "violation";

            // Criterion name
            const nameHeader = document.createElement("h6");
            nameHeader.textContent = name;
            violationDiv.appendChild(nameHeader);

            // Violation reason label + text
            const reasonDiv = document.createElement("div");
            const reasonLabel = document.createElement("span");
            reasonLabel.className = "requirement_label";
            reasonLabel.textContent = "Violation reason: ";
            reasonDiv.append(reasonLabel);

            const reasonText = document.createElement("span");
            reasonText.textContent = crit.reason || "No reason provided.";
            reasonDiv.appendChild(reasonText);
            violationDiv.append(reasonDiv);

            // Suggested improvement only if present (not null/undefined)
            if (crit.improvement != null) {
                const improvementLabel = document.createElement("span");
                improvementLabel.className = "requirement_label";
                improvementLabel.textContent = " Suggested improvement: ";
                violationDiv.appendChild(improvementLabel);

                const improvementText = document.createElement("span");

                if (Array.isArray(crit.improvement)) {
                    // Append each suggestion with line breaks between them
                    crit.improvement.forEach((item, idx) => {
                        const part = document.createElement("span");
                        part.textContent = item;
                        improvementText.appendChild(part);
                        if (idx < crit.improvement.length - 1) {
                            improvementText.appendChild(document.createElement("br"));
                        }
                    });
                } else {
                    improvementText.textContent = crit.improvement;
                }

                violationDiv.appendChild(improvementText);
            }

            inner.appendChild(violationDiv);
        });
    }

    outer.appendChild(wrapper);
    return outer;
}

async function loadRequirements() {
    fetch("output.json")
    .then(response => response.json())
    .then(data => {
        const requirements = data.requirements;
        const requirementsColumn = document.getElementById("requirementsColumn");
        requirementsColumn.innerHTML = ""; // Clear existing content

        const requirementsArray = Object.values(requirements);
        requirementsArray.sort((a, b) => a.topic_id - b.topic_id);
        requirementsArray.forEach(req => {

            // Main wrapper
            const wrapper = document.createElement("div");
            wrapper.className = "requirement_wrapper";
            wrapper.setAttribute("data-id", req.topic_id);

            // Top row: Requirement title on left, topic+button on right
            topRow = createTopRow(req)

            // Requirement content row
            content = loadContent(req)

            //Additional information
            additional = loadAdditionalInformation(data, req)

            criteriaViolationCounter = makeIndividualCriteriaViolationCounter(req)
            individualCriteriaViolations = loadCriteriaViolations(req, criteriaViolationCounter)
            if (individualCriteriaViolations != null) {
                additional.append(individualCriteriaViolations)
            }
            // Requirement footer
            footer = loadFooter(criteriaViolationCounter, req)

            

            // Add to wrapper
            wrapper.appendChild(topRow);
            wrapper.appendChild(content);
            wrapper.appendChild(additional);
            wrapper.appendChild(footer);

            // Add to column
            requirementsColumn.appendChild(wrapper);
        });
        const pipelineModal = document.getElementById("pipelineModal");
        const prompts = data.prompts;
        loadPipelinePrompts(pipelineModal, prompts);
    })
    .catch(err => console.error("Error loading requirements:", err));
}

function createPromptElement({ title, prompt }) {
  const promptDiv = document.createElement("div");
  promptDiv.className = "prompt";

  // Title span
  const titleSpan = document.createElement("span");
  titleSpan.className = "prompt-title";
  titleSpan.textContent = title;
  promptDiv.appendChild(titleSpan);

  // Text span (hidden by default)
  const textSpan = document.createElement("span");
  textSpan.className = "prompt-text";
  textSpan.textContent = prompt;
  promptDiv.appendChild(textSpan);

  // Toggle visibility on click
  titleSpan.addEventListener("click", () => {
    promptDiv.classList.toggle("expanded");
  });

  return promptDiv;
}


// Load multiple prompts into the modal and show it
function loadPipelinePrompts(modalElement, prompts) {
  if (!modalElement) return null;
  const body = modalElement.querySelector(".modal-body");
  const closeBtn = modalElement.querySelector(".modal-close");
  closeBtn.addEventListener("click", () => {
        modalElement.style.display = "none";
    });
  if (!body) return null;
  // Remove any previously injected .prompt nodes
  const oldPrompts = body.querySelectorAll(".prompt");
  oldPrompts.forEach(n => n.remove());

  // If prompts is not an array but has a single object, normalize to array
  const list = Array.isArray(prompts) ? prompts : (prompts ? [prompts] : []);

  Object.entries(prompts).forEach(([title, text]) => {
  if (text == null) return; // skip null/undefined just in case
    body.appendChild(createPromptElement({ title, prompt: text }));
    });
}

function openPipelineModal(isRoleInferred, isRationaleInferred) {
    const modalElement = document.getElementById("pipelineModal");
    modalElement.style.display = "flex"; // show the modal, assuming your CSS hides it by default

    const prompts = modalElement.querySelectorAll(".prompt");
    prompts.forEach(prompt => {
        const titleEl = prompt.querySelector(".prompt-title");
        if (!titleEl) return; // skip if no title

        const title = titleEl.textContent.trim();
        if (title === "INFER_MISSING_ROLES_PROMPT") {
            prompt.style.display = isRoleInferred ? "block" : "none";
        } else if (title === "INFER_MISSING_RATIONALES_PROMPT") {
            prompt.style.display = isRationaleInferred ? "block" : "none";
        }
    });
}

// Load requirements when the page loads
window.addEventListener("DOMContentLoaded", loadRequirements);
