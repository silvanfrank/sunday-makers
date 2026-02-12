"""
FastAPI server for the FIRE Agent.
Exposes the agent as a web service.
"""
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from execution.orchestrator import FIREOrchestrator
from execution.logging_utils import log_message


# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

# Initialize FastAPI
app = FastAPI(
    title="FIRE Agent API",
    description="Financial Independence, Retire Early planning agent",
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
    "https://fire.longtermtrends.com",
    "https://agent.longtermtrends.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Session storage (in-memory for now)
sessions: Dict[str, FIREOrchestrator] = {}


# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    sessionId: str = Field(..., description="Unique session identifier")
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Chat history")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User metadata (name, email, etc)")


class ChatResponse(BaseModel):
    reply: str  # Changed from 'response' to 'reply' to match chatbox expectation
    timestamp: str


# Routes
@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "service": "FIRE Agent API",
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


# --- Rate Limiting Setup ---
import time
_rate_limit_store = {}
RATE_LIMIT_MAX_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 1800 # 30 minutes

def check_rate_limit(session_id: str) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    now = time.time()
    if session_id not in _rate_limit_store:
        _rate_limit_store[session_id] = []
    
    # Filter valid timestamps within window
    timestamps = [t for t in _rate_limit_store[session_id] if now - t < RATE_LIMIT_WINDOW_SECONDS]
    
    # Check limit
    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return False
        
    # Update store
    timestamps.append(now)
    _rate_limit_store[session_id] = timestamps
    return True


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Handles conversation with the FIRE Agent.
    """
    try:
        session_id = request.sessionId

        # Rate Limit Check
        if not check_rate_limit(session_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
        
        # Log user message immediately (before processing)
        log_message(session_id, "user", request.message, request.metadata)
        
        # Create new session if needed
        if session_id not in sessions:
            orchestrator = FIREOrchestrator(GEMINI_API_KEY)
            orchestrator.start_session()
            sessions[session_id] = orchestrator
        
        # Get orchestrator
        orchestrator = sessions[session_id]
        
        # Send message
        response = orchestrator.send_message(request.message)
        
        # Log model response (after processing)
        log_message(session_id, "model", response, request.metadata)
        
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
