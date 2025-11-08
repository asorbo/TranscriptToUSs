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

<img width="1919" height="854" alt="Screenshot 2025-09-18 195010" src="https://github.com/user-attachments/assets/0a78c566-7e5f-4b48-9265-5e480c9cd535" />

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

## How to Run the Prototype

Everything is containerized with Docker.  
Below is a step-by-step guide on how to set up and run the prototype.

---

### 1. Run the LLM Pipeline

1. **Install Docker**  
   Follow the official guide: [Install Docker](https://www.docker.com/get-started/)

2. **Clone the repository (or download it using this [link](https://github.com/asorbo/TranscriptToUSs.git))**  
   ```bash
   git clone git@github.com:asorbo/TranscriptToUSs.git
   cd TranscriptToUSs
   ```

3. **Build and run the Docker image**  
   Set the required environment variables when running the container:
   - `API_KEY`: A Google API key with the Gemini API service enabled.  
   - `RUNS_PER_MINUTE`: API calls per minute (used to throttle requests to avoid unexpected costs).  

   Example:
   ```bash
   docker build -t elicitation-to-us:latest .
   docker run -p 8123:8123 -e API_KEY="your-google-api-key" -e RUNS_PER_MINUTE="15" elicitation-to-us:latest
   ```

4. **Open the user interface**  
   Go to [http://localhost:8123](http://localhost:8123) in your browser.  
   - Paste the elicitation interview transcript.
   - Press **Enter** to start processing.
   - When finished, a `.zip` file containing all outputs will be downloaded automatically.

---

### 2. View the Outputs

#### **Windows**
1. Extract the downloaded `.zip` folder.
2. Double-click `start-viewer-windows.exe`.  
   - If blocked by Windows, click **More info** → **Run anyway**.

---

#### **Linux**
1. Extract the `.zip` folder.
2. In the terminal, run:
   ```bash
   ./webviewer-linux
   ```
   If not executable:
   ```bash
   chmod +x ./webviewer-linux
   ./webviewer-linux
   ```

---

#### **macOS**
1. Extract the `.zip` folder.
2. In the terminal, run:
   ```bash
   ./webviewer-mac
   ```
   If not executable:
   ```bash
   chmod +x ./webviewer-mac
   ./webviewer-mac
   ```
3. If macOS blocks the script:
   - Go to **System Settings → Privacy & Security**.
   - Locate the blocked item under **Full Disk Access**, **Accessibility**, or **General → Allow Anyway/Open Anyway**.
   - Grant permission for the program to run.

---

#### **Any System with Python Installed**
1. Extract the `.zip` folder.
2. Install dependencies and start the viewer:
   ```bash
   pip install -r requirements.txt
   python start-viewer-python.py
   ```

---

---

## Project Status  
- Research ongoing until **October 2025**  
- Active development on:  
  - Codebase  
  - Paper draft  
  - Expert Evaluation of the pipeline  
