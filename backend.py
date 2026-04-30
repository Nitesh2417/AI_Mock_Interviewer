import uuid
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.state import InterviewState
from src.graph import app_graph

# Logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ye Hai Mera Backend")

# In-memory store 
sessions = {}

# This for Validation
class SetupRequest(BaseModel):
    target_role: str
    focus_area: str
    background: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/start")
def start_interview(request: SetupRequest):
    """Initializes the interview state and triggers the first question."""
    session_id = str(uuid.uuid4())
    logger.info(f"Starting new interview session: {session_id} for role: {request.target_role}")
    
    
    initial_state: InterviewState = {
        "target_role": request.target_role,
        "focus_area": request.focus_area,
        "background": request.background,
        "industry_context": "",  
        "turn_count": 0,
        "transcript": [],
        "evaluations": []
    }
    
    try:
       
        result_state = app_graph.invoke(initial_state)
        
        
        sessions[session_id] = result_state
        return {"session_id": session_id, "state": result_state}
        
    except Exception as e:
        logger.error(f"Graph execution failed during setup: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize the interview graph.")

@app.post("/chat")
def chat(request: ChatRequest):
    """Receives the candidate's answer, updates state, and resumes the graph."""
    if request.session_id not in sessions:
        logger.warning(f"Attempted to access missing session: {request.session_id}")
        raise HTTPException(status_code=404, detail="Session not found. It may have expired.")
        
    current_state = sessions[request.session_id]
    
    
    current_state["transcript"].append({"role": "Candidate", "content": request.message})
    
  
    current_state["turn_count"] = current_state.get("turn_count", 0) + 1
    
    try:
       
        result_state = app_graph.invoke(current_state)
        
        
        sessions[request.session_id] = result_state
        return {"state": result_state}
        
    except Exception as e:
        logger.error(f"Graph execution failed during chat: {e}")
        raise HTTPException(status_code=500, detail="The AI agents encountered an error processing your response.")

if __name__ == "__main__":
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
