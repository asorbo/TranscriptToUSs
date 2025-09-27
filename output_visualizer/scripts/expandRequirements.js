// Function to expand a requirement wrapper
function expandRequirement(e) {
    const req = e.target.closest(".requirement_wrapper");
    if (!req) return;

    if (
        e.target.classList.contains("expandButton") ||
        e.target.classList.contains("role") ||
        (e.target.getAttribute("is_rationale_inferred") == "true")
    ) {
        collapseAllRequirements();
        req.classList.toggle("expanded");
    }

    //center vertically
    requestAnimationFrame(() => {
      scrollToElement(requirementsColumn, req);
    });
    
}

function collapseAllRequirements(){
    if (!userIsScrolling) return;
    document.querySelectorAll(".requirement_wrapper.expanded").forEach(el => {
        el.classList.remove("expanded");
    });
    userIsScrolling = false;
}

// Attach event listeners after the requirements are loaded
function attachExpandEvents() {
    requirementsColumn.addEventListener("click", expandRequirement)
}

let userIsScrolling = false;

requirementsColumn.addEventListener("wheel", () => userIsScrolling = true);
requirementsColumn.addEventListener("touchstart", () => userIsScrolling = true);
requirementsColumn.addEventListener("keydown", () => userIsScrolling = true);

// Call this function after dynamically loading requirements
window.addEventListener("DOMContentLoaded", attachExpandEvents);