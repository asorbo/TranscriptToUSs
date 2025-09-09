  // Scroll helper
    function scrollToElement(container, el) {
      const containerHeight = container.clientHeight;
      const elementHeight = el.offsetHeight;
      const twoVH = window.innerHeight / 100 * 3;
      const offset = el.offsetTop - container.offsetTop; - twoVH

      container.scrollTo({
        top: offset - containerHeight / 2 + elementHeight / 2,
        behavior: "smooth"
      });
    }
  
  async function setAutoscrollOnClick() {
    const topics = document.querySelectorAll(".topic");
    const topicsColumn = document.getElementById("topicsColumn");
    const requirementsColumn = document.getElementById("requirementsColumn");

    requirementsColumn.addEventListener("click", e => {
      const req = e.target.closest(".requirement_wrapper");
      if (!req) return;
      const id = req.dataset.id;
      const targetTopic = document.querySelector(`.topic[data-id='${id}']`);
      if (targetTopic) scrollToElement(topicsColumn, targetTopic);
      highlightPair(id);
    });

    // When topic clicked → scroll right
    topics.forEach(topic => {
      topic.addEventListener("click", () => {
        console.log("Topic clicked");
        const id = topic.dataset.id;
        const targetReq = document.querySelector(`.requirement_wrapper[data-id='${id}']`);
        scrollToElement(requirementsColumn, targetReq);
        highlightPair(id);
      });
    });

    // Highlight both sides
    function highlightPair(id) {
      console.log("Highlighting pair:", id);
      document.querySelectorAll(".topic, .requirement_wrapper").forEach(el => {
        el.classList.toggle("active", el.dataset.id === id);
      });
    }
  }
  window.addEventListener("DOMContentLoaded", setAutoscrollOnClick);