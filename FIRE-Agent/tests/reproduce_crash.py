
import os
from dotenv import load_dotenv
from execution.orchestrator import FIREOrchestrator

# Load Env
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    parent_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(parent_env):
        load_dotenv(parent_env)

import uuid
api_key = os.getenv("GEMINI_API_KEY")
orchestrator = FIREOrchestrator(api_key)
session_id = f"crash-test-{uuid.uuid4()}"
print(f"Starting session: {session_id}")
greeting = orchestrator.start_session(session_id=session_id)
print(f"Agent: {greeting}")

# Simulate the conversation that caused the crash
user_message = "- **Age:** 36- **Invested Assets:** $1,000,000- **Home Equity:** $0- **Annual Income:** $0 (Immediate Drawdown)- **Annual Expenses:** $100,000- **Expected Inheritance:** $1,000,000 at age 40"

print(f"\nSending user message: {user_message}")
try:
    response = orchestrator.send_message(user_message)
    print(f"\nResponse received successfully (Length: {len(response)})")
    # print(response[:500]) # Print first 500 chars
except Exception as e:
    print(f"\nCRASH CAUGHT: {e}")
