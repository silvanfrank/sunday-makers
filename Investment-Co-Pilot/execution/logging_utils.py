"""
Shared logging utilities for the Investment Co-Pilot.
Used by both api.py and interactive_chat.py to ensure consistent logging format.
"""
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Logging Configuration
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
TRANSCRIPT_FILE = LOGS_DIR / "transcripts.jsonl"


def log_message(
    session_id: str,
    role: str,
    message: str,
    metadata: Optional[dict] = None
) -> None:
    """
    Log a single message to the JSONL transcript file.
    
    Args:
        session_id: Unique identifier for the chat session
        role: The sender of the message ('user' or 'model')
        message: The message content
        metadata: Optional dict with user info (user_name, user_email, user_id)
    
    Log Format:
        {
            "metadata": {...},           # First (if provided)
            "timestamp": "ISO8601",
            "sessionId": "...",
            "role": "user" | "model",
            "message": "..."
        }
    """
    entry = {}
    
    # Metadata first (user preference)
    if metadata:
        entry["metadata"] = metadata
    
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    entry["sessionId"] = session_id
    entry["role"] = role
    entry["message"] = message
    
    with open(TRANSCRIPT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

