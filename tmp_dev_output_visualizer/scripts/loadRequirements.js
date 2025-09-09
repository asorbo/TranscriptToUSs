function loadAdditionalInformation(data, req) {
    const additional = document.createElement("div");
    additional.className = "additional_information";

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

    additional.appendChild(roleInfo);
    additional.appendChild(rationaleInfo);

    return additional;
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

function loadFooter(req){
    const footer = document.createElement("div");
    footer.className = "requirement_footer";

    const hsButton = document.createElement("button");
    hsButton.className = "openHistory";
    hsButton.textContent = "HS";

    const expandButton = document.createElement("button");
    expandButton.className = "expandButton";
    expandButton.textContent = "↕";

    footer.appendChild(hsButton);
    footer.appendChild(expandButton);
    
    return footer
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

            // Requirement footer
            footer = loadFooter(req)

            // Add to wrapper
            wrapper.appendChild(topRow);
            wrapper.appendChild(content);
            wrapper.appendChild(additional);
            wrapper.appendChild(footer);

            // Add to column
            requirementsColumn.appendChild(wrapper);
        });
    })
    .catch(err => console.error("Error loading requirements:", err));
}

// Load requirements when the page loads
window.addEventListener("DOMContentLoaded", loadRequirements);
