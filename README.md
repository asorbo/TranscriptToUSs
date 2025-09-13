# From Elicitation Interviews to User Stories  
### A Prompt Chaining LLM Approach for Automated Candidate Requirements Extraction  

> **Note**: This research project is ongoing until **October 2025**. The README, codebase, and paper are under active development.  

---

## 📖 Overview  

This prototype automatically formulates **candidate requirements** as **User Stories** based on elicitation interview transcripts.  
Through a series of **prompt-chaining steps**, the system:  
1. Processes the transcript  
2. Extracts requirement-relevant content  
3. Generates **traceable User Stories** linked back to the original transcript for interpretability  

The process can take several minutes depending on the transcript’s length and complexity.

---

## Application Screens  

### Transcript Upload & Processing  

<img width="1916" height="861" alt="uploadTranscript" src="https://github.com/user-attachments/assets/e1f11770-8040-43dd-af7f-aec03ba5b159" />  

- The user pastes the **elicitation interview transcript**  
- The system processes it step-by-step, showing progress in real time  
- When complete, results are delivered in a **zip file** along with the **output visualizer**  

---

### Output Visualizer - Contracted View  

<img width="1918" height="859" alt="ContractedView" src="https://github.com/user-attachments/assets/78a8df56-56dc-4229-b94a-1b1ac0707c97" />  

- **Transcript segments** appear on the left  
- **Generated User Stories** appear on the right  
- Selecting a requirement highlights its source segment and related user stories  
- Expandable elements let you explore inferred roles, rationales, and relationships  

---

### Output Visualizer - Expanded View  

<img width="1916" height="859" alt="ExpandedView" src="https://github.com/user-attachments/assets/cdf1d940-170e-414f-b20b-ec712f316709" />  

- Shows the **role** and **rationale** for each requirement  
- Displays **reasoning** if roles/rationales were inferred rather than directly extracted  
- Lists potential **QUS framework violations**  
- Suggests **improvements** when possible  

---

## How to run the prototype
Everything is containerized with Docker.
A brief guide on how to run this is coming soon.

---

## Project Status  
- Research ongoing until **October 2025**  
- Active development on:  
  - Codebase  
  - Paper draft  
  - Expert Evaluation of the pipeline  
