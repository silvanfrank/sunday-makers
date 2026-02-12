"""
Orchestrator - The Brain of the Investment Co-Pilot.
Connects Gemini LLM with deterministic tools using MANUAL function calling.
This allows us to trace tool execution and handle errors properly.
"""
from google import genai
from google.genai import types
import os
from execution.financial_utils import calculate_holistic_allocation
from execution.generate_ips import generate_ips_markdown
from execution.data_mapper import build_ips_context

from pathlib import Path
from typing import Optional

# Load system instruction from file
DIRECTIVE_PATH = Path(__file__).parent.parent / "directives" / "orchestrator_directive.md"
with open(DIRECTIVE_PATH, "r") as f:
    SYSTEM_INSTRUCTION = f.read()

_client = None
_sessions = {}  # Simple in-memory session store

# Tool registry for manual function calling
TOOLS = {
    "calculate_holistic_allocation": calculate_holistic_allocation,
    "generate_ips_markdown": generate_ips_markdown,
}


def get_client():
    """Configures and returns the GenAI Client."""
    global _client
    if _client is not None:
        return _client
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    
    _client = genai.Client(api_key=api_key)
    return _client


class InvestmentCoPilotOrchestrator:
    """Orchestrates the Investment Co-Pilot conversation using MANUAL function calling."""
    
    def __init__(self, api_key: str):
        """Initialize with Gemini API key."""
        os.environ["GEMINI_API_KEY"] = api_key
        self.client = get_client()
        self.chat = None
        self.session_id = None
    
    def start_session(self, session_id: Optional[str] = None, user_name: Optional[str] = None, history: Optional[list] = None) -> str:
        """
        Start a new chat session.
        
        Args:
            session_id: Optional session identifier for tracking
            user_name: Optional user name for personalization
            history: Optional conversation history to resume
            
        Returns:
            Initial greeting from the agent
        """
        self.session_id = session_id
        
        # Customize system instruction with user context
        instruction = SYSTEM_INSTRUCTION
        if user_name:
            instruction = f"User Name: {user_name}\n\n" + instruction
        
        # Define tools - pass Python functions directly
        tools_list = [calculate_holistic_allocation, generate_ips_markdown]
        
        # Create chat with MANUAL function calling (disable=True)
        self.chat = self.client.chats.create(
            model="gemini-3-pro-preview",
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                tools=tools_list,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True,  # DISABLE automatic - we handle it manually
                ),
            ),
            history=history if history else []
        )
        
        # Store session
        if session_id:
            _sessions[session_id] = self
        
        # Return empty - welcome message is in the directive's initial context
        return ""
    
    def _process_response(self, response) -> str:
        """
        Process the LLM response, handling any function calls manually.
        
        If the LLM requests a function call, execute it and:
        - For `generate_ips_markdown`: Return the result DIRECTLY (verbatim)
        - For other tools: Send result back to LLM for interpretation or chain to next tool
        """
        # Check if response contains function calls
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                # Check if this part is a function call
                if hasattr(part, 'function_call') and part.function_call:
                    func_call = part.function_call
                    func_name = func_call.name
                    func_args = dict(func_call.args) if func_call.args else {}
                    
                    print(f"[DEBUG] Tool called: {func_name}")
                    print(f"[DEBUG] Args: {func_args}")
                    
                    # Execute the function
                    if func_name in TOOLS:
                        try:
                            result = TOOLS[func_name](**func_args)
                            print(f"[DEBUG] Tool result: {type(result).__name__}")
                            
                            # CRITICAL: For generate_ips_markdown, return DIRECTLY
                            if func_name == "generate_ips_markdown":
                                print("[DEBUG] Returning IPS VERBATIM")
                                return result  # Bypass LLM interpretation!
                            
                            # AUTO-CHAIN: If calculate_holistic_allocation, immediately generate IPS
                            if func_name == "calculate_holistic_allocation":
                                print("[DEBUG] Auto-chaining generate_ips_markdown...")
                                print(f"[DEBUG] Allocation result: {result}")
                                
                                # The result now contains all needed data (region, esg, age, etc.)
                                # Pass it directly as the allocation, and extract other fields
                                ips_args = build_ips_context(result, func_args)
                                print(f"[DEBUG] IPS args: {ips_args}")
                                ips_result = TOOLS["generate_ips_markdown"](**ips_args)
                                print("[DEBUG] Returning IPS VERBATIM (auto-chained)")
                                
                                # POST-REPORT CONTEXT INJECTION
                                # Send the full IPS to the model so it can reference the report
                                # in follow-up conversations.
                                print("[DEBUG] Injecting post-report context (full IPS)...")
                                
                                function_response = types.Part.from_function_response(
                                    name="calculate_holistic_allocation",
                                    response={
                                        "status": "success", 
                                        "message": "IPS generated and shown to user. Use this content to answer follow-up questions.",
                                        "ips_shown_to_user": ips_result
                                    }
                                )
                                
                                try:
                                    self.chat.send_message(function_response)
                                    print("[DEBUG] Post-report context sent successfully")
                                except Exception as ctx_error:
                                    print(f"[WARN] Could not inject context: {ctx_error}")
                                
                                return ips_result
                            
                            # For other tools, send result back to LLM
                            function_response = types.Part.from_function_response(
                                name=func_name,
                                response=result  # Pass raw result
                            )
                            
                            print(f"[DEBUG] Sending tool result back to LLM...")
                            
                            # Send function response back to model
                            followup = self.chat.send_message(function_response)
                            return self._process_response(followup)
                            
                        except Exception as e:
                            error_msg = f"Error executing {func_name}: {str(e)}"
                            print(f"[ERROR] {error_msg}")
                            import traceback
                            traceback.print_exc()
                            return f"I encountered an error while calculating: {str(e)}"
                    else:
                        print(f"[ERROR] Unknown function: {func_name}")
                        return f"Unknown function requested: {func_name}"
        
        # No function call - return text response
        text = response.text if response.text else ""
        if not text:
            print("[DEBUG] Empty text response - checking parts...")
            print(f"[DEBUG] Response candidates: {len(response.candidates) if response.candidates else 0}")
            
            # Check for MALFORMED_FUNCTION_CALL - the LLM tried but failed
            if response.candidates and hasattr(response.candidates[0], 'finish_reason'):
                finish_reason = str(response.candidates[0].finish_reason)
                if "MALFORMED_FUNCTION_CALL" in finish_reason:
                    print("[DEBUG] Detected MALFORMED_FUNCTION_CALL - attempting fallback...")
                    return self._handle_malformed_function_call()
            
            if response.candidates and response.candidates[0].content.parts:
                print(f"[DEBUG] Number of parts: {len(response.candidates[0].content.parts)}")
                for i, part in enumerate(response.candidates[0].content.parts):
                    print(f"[DEBUG] Part {i}: {type(part).__name__}")
                    print(f"[DEBUG] Part {i} attrs: {dir(part)}")
                    if hasattr(part, 'function_call') and part.function_call:
                        print(f"[DEBUG] Part {i} has function_call: {part.function_call}")
                    if hasattr(part, 'text') and part.text:
                        text += part.text
                        print(f"[DEBUG] Part {i} text: {part.text[:100]}...")
            else:
                print("[DEBUG] No parts found in response!")
                print(f"[DEBUG] Raw response: {response}")
        return text
    
    def _handle_malformed_function_call(self) -> str:
        """
        Fallback handler when LLM generates a malformed function call.
        Extracts user inputs from conversation history and calls tools directly.
        """
        import re
        print("[DEBUG] Running fallback: extracting inputs from conversation history...")
        
        # Get conversation history - the SDK returns Content objects
        history = []
        if self.chat and hasattr(self.chat, '_curated_history'):
            history = self.chat._curated_history
        elif self.chat and hasattr(self.chat, 'history'):
            history = self.chat.history
        
        print(f"[DEBUG] History length: {len(history)}")
        
        # Find the confirmation message (contains structured inputs)
        confirmation_text = ""
        for i, msg in enumerate(reversed(history)):
            print(f"[DEBUG] Checking msg {i}: type={type(msg).__name__}")
            
            # Handle Content objects from google-genai SDK
            if hasattr(msg, 'role') and hasattr(msg, 'parts'):
                if msg.role == 'model':
                    for part in msg.parts:
                        text = ""
                        if hasattr(part, 'text'):
                            text = part.text or ""
                        elif isinstance(part, str):
                            text = part
                        
                        if "Age:" in text and "Region:" in text:
                            confirmation_text = text
                            print(f"[DEBUG] Found confirmation in msg {i}")
                            break
            
            if confirmation_text:
                break

        
        if not confirmation_text:
            print("[ERROR] Could not find confirmation message in history")
            return "I apologize, but I had trouble processing. Could you please confirm your inputs again?"
        
        print(f"[DEBUG] Found confirmation text, parsing...")
        
        # Parse values using regex
        age_match = re.search(r'\*\*Age:\*\*\s*(\d+)', confirmation_text)
        region_match = re.search(r'\*\*Region:\*\*\s*(\w+)', confirmation_text)
        housing_match = re.search(r'\*\*Housing:\*\*\s*(\w+)', confirmation_text)
        goal_match = re.search(r'\*\*Goal:\*\*\s*(\w+)', confirmation_text)
        risk_match = re.search(r'\*\*Risk Profile:\*\*\s*(\w+)', confirmation_text)
        fun_match = re.search(r'\*\*Fun Bucket:\*\*\s*(\d+)', confirmation_text)
        esg_match = re.search(r'\*\*ESG:\*\*\s*(\w+)', confirmation_text)
        
        func_args = {
            "age": int(age_match.group(1)) if age_match else 40,
            "region": region_match.group(1) if region_match else "EU",
            "housing_status": housing_match.group(1).lower() if housing_match else "rent",
            "goal": goal_match.group(1).lower() if goal_match else "longevity",
            "risk_profile": risk_match.group(1).lower() if risk_match else "moderate",
            "fun_bucket_pct": int(fun_match.group(1)) if fun_match else 0,
            "esg_preference": esg_match and esg_match.group(1).lower() == "yes",
            "has_high_interest_debt": False,
            "months_savings": 6,
        }
        
        print(f"[DEBUG] Parsed args: {func_args}")
        
        try:
            result = TOOLS["calculate_holistic_allocation"](**func_args)
            print(f"[DEBUG] Fallback allocation: {result['strategy']}")
            
            ips_args = build_ips_context(result, func_args)
            ips_result = TOOLS["generate_ips_markdown"](**ips_args)
            print("[DEBUG] Fallback IPS generated successfully")
            return ips_result
            
        except Exception as e:
            print(f"[ERROR] Fallback failed: {e}")
            import traceback
            traceback.print_exc()
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    
    def send_message(self, user_message: str) -> str:
        """
        Send a message and get response.
        
        Args:
            user_message: The user's message
            
        Returns:
            The agent's response text
        """
        if not self.chat:
            raise RuntimeError("Session not started. Call start_session() first.")
        
        try:
            response = self.chat.send_message(user_message)
            return self._process_response(response)
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_history(self) -> list:
        """Get conversation history."""
        if not self.chat:
            return []
        return self.chat.history if hasattr(self.chat, 'history') else []


def create_chat(session_id=None, history=None, user_name=None):
    """
    Creates or retrieves a chat session wrapped in an Orchestrator.
    This ensures all calls go through the manual function calling logic.
    """
    global _sessions
    
    # If we have an active orchestrator in memory, return it
    if session_id and session_id in _sessions:
        return _sessions[session_id]

    api_key = os.getenv("GEMINI_API_KEY")
    orchestrator = InvestmentCoPilotOrchestrator(api_key)
    orchestrator.start_session(session_id=session_id, user_name=user_name, history=history)
    
    if session_id:
        _sessions[session_id] = orchestrator
        
    return orchestrator
