"""
Interactive CLI for the Car Agent.
Run with: python -m execution.interactive_chat
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.orchestrator import CarOrchestrator


def main():
    """Run the interactive Car Agent chat."""
    # Load environment
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment.")
        print("Create a .env file with: GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    print("=" * 60)
    print("🚗 Car Affordability Agent")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation.")
    print("-" * 60)
    print()
    
    # Initialize orchestrator
    orchestrator = CarOrchestrator(api_key)
    greeting = orchestrator.start_session()
    print(f"Agent: {greeting}")
    print()
    
    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye! Drive safe! 🚗")
                break
            
            response = orchestrator.send_message(user_input)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Drive safe! 🚗")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
