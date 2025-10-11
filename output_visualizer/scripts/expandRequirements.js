// Function to expand a requirement wrapper
function expandRequirement(e) {
    console.log(e);
    const req = e.target.closest(".requirement_wrapper");
    if (!req) return;
    const isAlreadyExpanded = req.classList.contains("expanded");
    if (isAlreadyExpanded) {
        return;
    }
    if (
        e.target.classList.contains("expandButton") ||
        e.target.classList.contains("role") ||
        (e.target.getAttribute("is_rationale_inferred") == "true")
    ) {
        collapseAllRequirements();
        console.log("expanding " + req.getAttribute("requirement-id"));
        req.classList.toggle("expanded");
    }

    document.querySelectorAll(".highlight").forEach(el => {
            el.classList.remove("highlight");
        });
    
    if (req.classList.contains("expanded")) {
        const id = req.dataset.id;
        const topicElement = document.querySelector(`.topic[data-id='${id}']`);
        const sentences = JSON.parse(req.dataset.origin_sentences);
        console.log(sentences);
        highlightSentences(topicElement, sentences);
    }

    //center vertically
    requestAnimationFrame(() => {
      scrollToElement(requirementsColumn, req);
    });
    
}

function highlightSentences(topicElement, sentences) {
    let html = topicElement.innerHTML; 
    sentences.forEach(sentence => {
        // Escape regex special characters in the sentence
        const safeSentence = sentence.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const regex = new RegExp(safeSentence, "g");
        html = html.replace(regex, `<span class="highlight">$&</span>`);
    });
    topicElement.innerHTML = html;
}

function collapseAllRequirements(){
    if (!userIsScrolling) return;
    document.querySelectorAll(".requirement_wrapper.expanded").forEach(el => {
        el.classList.remove("expanded");
    });
    userIsScrolling = false;
    removeHighlights();
}

function removeHighlights() {
    // Find all highlight spans inside the given root (default: whole document)
    const highlights = document.querySelectorAll("span.highlight");
    highlights.forEach(span => {
        // Replace the span with just its plain text content
        const textNode = document.createTextNode(span.textContent);
        span.parentNode.replaceChild(textNode, span);
    });
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