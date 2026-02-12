"""
FastAPI server for the Car Agent.
Exposes the agent as a web service.
"""
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from execution.orchestrator import CarOrchestrator


# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

# Initialize FastAPI
app = FastAPI(
    title="Car Agent API",
    description="Car Affordability planning agent",
    version="1.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://longtermtrends.net",
    "https://www.longtermtrends.net",
    "https://longtermtrends.com",
    "https://www.longtermtrends.com",
    "https://car.longtermtrends.com",
    "https://agent.longtermtrends.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Session storage (in-memory)
sessions: Dict[str, CarOrchestrator] = {}


# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    sessionId: str = Field(..., description="Unique session identifier")
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Chat history")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User metadata")


class ChatResponse(BaseModel):
    reply: str
    timestamp: str


# Rate limiting
_rate_limit_store = {}
RATE_LIMIT_MAX_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 1800  # 30 minutes


def check_rate_limit(session_id: str) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    now = time.time()
    if session_id not in _rate_limit_store:
        _rate_limit_store[session_id] = []
    
    timestamps = [t for t in _rate_limit_store[session_id] if now - t < RATE_LIMIT_WINDOW_SECONDS]
    
    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    timestamps.append(now)
    _rate_limit_store[session_id] = timestamps
    return True


# Routes
@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "service": "Car Agent API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "active_sessions": len(sessions)
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Handles conversation with the Car Agent.
    """
    try:
        session_id = request.sessionId

        if not check_rate_limit(session_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
        
        # Create new session if needed
        if session_id not in sessions:
            orchestrator = CarOrchestrator(GEMINI_API_KEY)
            orchestrator.start_session()
            sessions[session_id] = orchestrator
        
        orchestrator = sessions[session_id]
        response = orchestrator.send_message(request.message)
        
        return ChatResponse(
            reply=response,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "deleted", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/sessions")
async def list_sessions():
    """List active sessions."""
    return {
        "active_sessions": len(sessions),
        "session_ids": list(sessions.keys())
    }


# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
