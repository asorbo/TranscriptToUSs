
async function loadTopics() {
try {
    // Fetch the JSON file
    const response = await fetch("output.json");
    const data = await response.json();
    const topics = data.topic_texts;

    const container = document.getElementById("topicsColumn");
    container.innerHTML = ""; // Clear any existing content

    // Loop through topics
    Object.values(topics).forEach(topic => {
    // Create topic container
    const topicDiv = document.createElement("div");
    topicDiv.classList.add("topic");
    topicDiv.setAttribute("data-id", topic.topic_id);

    // Title and time
    const title = document.createElement("h4");
    title.textContent = `Topic ${topic.topic_id}: ${topic.label}`;

    const time = document.createElement("span");
    time.textContent = `${topic.start_time} - ${topic.end_time}`;

    topicDiv.appendChild(title);
    topicDiv.appendChild(time);

    // Speaker turns
    topic.speaker_turns.forEach(turn => {
        const turnDiv = document.createElement("div");
        turnDiv.classList.add("speaker_turn");

        const speakerSpan = document.createElement("span");
        speakerSpan.textContent = turn.speaker + ": ";

        const textSpan = document.createElement("span");
        textSpan.textContent = turn.text.replace(/\\n|\\\s/g, " ");

        turnDiv.appendChild(speakerSpan);
        turnDiv.appendChild(textSpan);
        topicDiv.appendChild(turnDiv);
    });

    // Add topicDiv to container
    container.appendChild(topicDiv);
    });
} catch (err) {
    console.error("Error loading topics:", err);
}
}

// Load topics when the page loads
window.addEventListener("DOMContentLoaded", loadTopics);