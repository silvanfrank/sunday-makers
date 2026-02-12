import sys
import os
from dotenv import load_dotenv

# Ensure the parent directory is in the path for module resolution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.orchestrator import InvestmentCoPilotOrchestrator
from execution.logging_utils import log_message

def main():
    # Load environment variables (API Key)
    load_dotenv()
    
    # Also check parent directory for .env
    if not os.getenv("GEMINI_API_KEY"):
        parent_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(parent_env):
            load_dotenv(parent_env)

    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found. Please set it in .env")
        return


    print("\n💰 Investment Co-Pilot CLI 💰")
    print("--------------------------------------------------")
    print("Directly connected to the Brain (Orchestrator).")
    print("Preserves state for 'cli-test-session'.")
    print("Type 'quit' or 'exit' to stop.")
    print("--------------------------------------------------\n")
    
    # Initialize Chat
    session_id = "cli-test-session"
    # Dummy Metadata for CLI testing
    cli_metadata = {
        "user_name": "CLI_Tester",
        "user_email": "tester@cli.local",
        "user_id": "cli-999"
    }

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        orchestrator = InvestmentCoPilotOrchestrator(api_key)
        orchestrator.start_session(session_id=session_id)
        
        # Investment Co-Pilot waits for user input first (directive has welcome message)
        print("Agent: Ready. How can I help you today?")
        
    except Exception as e:
        print(f"Failed to initialize chat: {e}")
        import traceback
        traceback.print_exc()
        return

    # Chat Loop
    while True:
        try:
            user_input = input("You: ")
            if user_input.strip().lower() in ["quit", "exit"]:
                print("\nGoodbye! 👋")
                break
            
            if not user_input.strip():
                continue

            # Log user message immediately
            log_message(session_id, "user", user_input, cli_metadata)
            
            # Send message using the orchestrator
            response = orchestrator.send_message(user_input)
            
            # Log model response
            log_message(session_id, "model", response, cli_metadata)
            
            print(f"\nCo-Pilot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

