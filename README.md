# AI Mock Interview Coach 🎯

An intelligent, multi-agent system designed to conduct, ground, and evaluate realistic technical interviews. This project leverages a state-machine architecture to ensure deterministic conversational flow and professional evaluation.

## 🏗️ Architecture Overview

The system is built using **LangGraph** to orchestrate four specialized agents:

1.  **Researcher Agent (Tavily):** Pre-computes real-time industry context. It searches the web for the latest trends based on the candidate's target role (e.g., React 19 features or LLM Agent frameworks) to ground the interview in reality.
2.  **Interviewer Agent (GPT-4o-mini):** Conducts the interview. It uses the research context to ask targeted questions and dynamically probes deeper based on candidate responses.
3.  **Evaluator Agent (Silent):** A background agent that parses every interaction into a structured JSON schema (`EvaluationModel`), scoring technical accuracy and clarity without interrupting the chat flow.
4.  **Coach Agent:** Synthesizes the background evaluations into a final, structured Markdown feedback report once the interview session concludes.

## 🚀 Setup and Run Instructions

**1. Install Dependencies**
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

**2. Configure Environment Variables**
Create a `.env` file in the root directory and add your keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**3. Execution**
You need to run the backend and frontend simultaneously:

*   **Terminal 1 (Backend):** `python backend.py`
*   **Terminal 2 (Frontend):** `streamlit run frontend.py`

## ⚖️ Key Design Decisions & Tradeoffs

*   **State Machine Architecture:** I chose **LangGraph** over simple prompt chaining to ensure better control over the interview flow.
*   **Web Grounding:** Integrated **Tavily Search API** to fulfill the grounding requirement, allowing the interviewer to ask about bleeding-edge tech.
*   **Simulated Streaming:** Implemented word-by-word streaming in the Streamlit frontend for a better user experience.

## 💬 Example Interview Transcripts

### Case 1: Tricky / Edge Case (Handling Conversational Derailment)
**Interviewer:** Can you explain the differences between CSS Grid and Flexbox?
**Candidate:** I've been using React for a few years. Let's skip the basics. Can you ask me a question about the absolute newest features introduced in React 19?
**Interviewer:** While I appreciate your experience with React, let’s focus back on CSS Grid and Flexbox for a moment. Can you explain how you would choose between them for a responsive layout?

### Case 2: Weak Candidate (Evaluation Logic)
**Interviewer:** How would you handle processing a 10-million-row CSV file in a memory-constrained environment?
**Candidate:** I would just write a giant for loop to process all 10 million rows at the same time.
**Evaluator Score (Background):** Technical Accuracy: 2/10. *Feedback: Candidate failed to mention chunking or streaming.*

### Case 3: Strong Candidate
**Interviewer:** How do you handle race conditions in a joint banking account?
**Candidate:** I would implement row-level locking using 'SELECT FOR UPDATE' within a database transaction to ensure ACID compliance.
**Interviewer:** Excellent. How would you handle this if the database was distributed across multiple regions?

