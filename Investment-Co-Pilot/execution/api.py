from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import json
import os
import subprocess
from dotenv import load_dotenv
from execution.financial_utils import calculate_holistic_allocation, get_recommended_portfolio
from execution.generate_ips import generate_ips_markdown
from execution.orchestrator import create_chat
from execution.logging_utils import log_message

# Load environment variables
load_dotenv()

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

app = FastAPI(title="Investment Co-Pilot API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.longtermtrends.net", 
        "https://longtermtrends.net", 
        "http://www.longtermtrends.net",
        "http://longtermtrends.net",
        "https://www.longtermtrends.com", 
        "https://longtermtrends.com",
        "http://www.longtermtrends.com",
        "http://longtermtrends.com",
        "https://agent.longtermtrends.com",
        "https://staging.longtermtrends.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://91.99.236.206",
        "https://staging.longtermtrends.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class WealthContext(BaseModel):
    housing_status: str = "rent"
    income_stability: str = "stable"
    has_high_interest_debt: bool = False
    months_savings: int = 6

class AllocationRequest(BaseModel):
    age: int
    risk: str = "moderate" # aggressive, moderate, conservative
    goal: str = "longevity" # liquidity, longevity, legacy
    wealth_context: Optional[WealthContext] = None

class IPSRequest(BaseModel):
    name: str = "Investor"
    age: int
    region: str = "US"
    esg_preference: bool = False
    goals: Dict[str, str] = {"liquidity": "Emergency Fund", "longevity": "Retirement"}
    wealth_context: WealthContext
    allocation: Dict[str, int]

# --- Chat Models ---
class ChatRequest(BaseModel):
    message: str
    sessionId: str
    history: Optional[list] = []
    metadata: Optional[dict] = {}

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Investment Co-Pilot"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Orchestration Layer: Handles natural language conversation + Tool Calling.
    """
    try:
        # Rate Limit Check
        if not check_rate_limit(req.sessionId):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

        # Log user message immediately (before processing)
        log_message(req.sessionId, "user", req.message, req.metadata)

        # Extract user context
        user_name = req.metadata.get("user_name") if req.metadata else None

        # Create chat session (stateful via memory)
        # We explicitly do NOT pass user_name to the orchestrator to ensure anonymity.
        # The agent will not know the user's name, preventing it from being sent to Gemini.
        orchestrator = create_chat(session_id=req.sessionId, history=req.history, user_name=None)

        # Send User Message through Orchestrator to ensure tool calling/fallbacks work
        reply_text = orchestrator.send_message(req.message)
        
        # Log model response (after processing)
        log_message(req.sessionId, "model", reply_text, req.metadata)

        return {"reply": reply_text}

    except Exception as e:
        print(f"Error: {e}")
        error_msg = "I'm having trouble connecting to my brain. Please try again."
        # Log error as model response
        log_message(req.sessionId, "model", f"[ERROR] {str(e)}", req.metadata)
        return {"reply": error_msg}

@app.post("/calculate-allocation")
def calculate_allocation(req: AllocationRequest):

    """
    Calculates the recommended asset allocation based on holistic profile.
    """
    try:
        # Pydantic to Dict
        wealth_ctx = req.wealth_context.dict() if req.wealth_context else {}
        
        result = calculate_holistic_allocation(
            age=req.age,
            risk_profile=req.risk,
            wealth_context=wealth_ctx,
            goal=req.goal
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-ips")
def generate_ips(req: IPSRequest):
    """
    Generates the Markdown content for an IPS.
    """
    try:
        # Convert Pydantic object to simple dict for the utility function
        data = req.dict()
        
        # Generate Markdown
        markdown_content = generate_ips_markdown(**data)
        
        return {
            "status": "success",
            "format": "markdown",
            "content": markdown_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
