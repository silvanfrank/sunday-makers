"""
Orchestrator - The Brain of the FIRE Agent.
Connects Gemini LLM with deterministic tools using MANUAL function calling.
This allows us to bypass the LLM's "interpretation" of tool outputs.
"""
import os
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types

from execution.financial_calculators import calculate_fire_projections
from execution.generate_fire_roadmap import generate_fire_roadmap
from execution.data_mapper import build_roadmap_context


# Load system instructions
DIRECTIVE_PATH = Path(__file__).parent.parent / "directives" / "create_fire_plan.md"
with open(DIRECTIVE_PATH, "r") as f:
    SYSTEM_INSTRUCTIONS = f.read()


# Global client instance
_client = None
_sessions = {}  # Session storage for chat instances

# Tool registry for manual function calling
TOOLS = {
    "calculate_fire_projections": calculate_fire_projections,
    "generate_fire_roadmap": generate_fire_roadmap,
}


def get_client():
    """Configure and return the GenAI Client."""
    global _client
    if _client is not None:
        return _client
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    
    _client = genai.Client(api_key=api_key)
    return _client


class FIREOrchestrator:
    """Orchestrates the FIRE planning conversation using MANUAL function calling."""
    
    def __init__(self, api_key: str):
        """Initialize with Gemini API key."""
        os.environ["GEMINI_API_KEY"] = api_key
        self.client = get_client()
        self.chat = None
        self.session_id = None
    
    def start_session(self, session_id: Optional[str] = None, user_name: Optional[str] = None) -> str:
        """
        Start a new chat session.
        
        Args:
            session_id: Optional session identifier for tracking
            user_name: Optional user name for personalization
            
        Returns:
            Initial greeting from the agent
        """
        self.session_id = session_id
        
        # Customize system instruction with user context
        instruction = SYSTEM_INSTRUCTIONS
        if user_name:
            instruction = f"User Name: {user_name}\n\n" + instruction
        
        # Define tools - pass Python functions directly
        tools_list = [calculate_fire_projections, generate_fire_roadmap]
        
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
            history=[]
        )
        
        # Store session
        if session_id:
            _sessions[session_id] = self.chat
        
        # Send initial greeting
        response = self.chat.send_message("Hello")
        return self._process_response(response)
    
    def _process_response(self, response) -> str:
        """
        Process the LLM response, handling any function calls manually.
        
        If the LLM requests a function call, execute it and:
        - For `generate_fire_roadmap`: Return the result DIRECTLY (verbatim)
        - For other tools: Send result back to LLM for interpretation
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
                            
                            # CRITICAL: For generate_fire_roadmap, return DIRECTLY
                            if func_name == "generate_fire_roadmap":
                                print("[DEBUG] Returning roadmap VERBATIM")
                                return result  # Bypass LLM interpretation!
                                
                            # AUTO-CHAIN: If calculate_fire_projections, immediately generate roadmap
                            if func_name == "calculate_fire_projections":
                                print("[DEBUG] Auto-chaining generate_fire_roadmap...")
                                roadmap_args = build_roadmap_context(result)
                                roadmap = TOOLS["generate_fire_roadmap"](**roadmap_args)
                                
                                # POST-REPORT CONTEXT INJECTION
                                # Send the full roadmap to the model so it can reference the report
                                # in follow-up conversations.
                                print("[DEBUG] Injecting post-report context (full roadmap)...")
                                
                                # Send function response containing the full roadmap
                                function_response = types.Part.from_function_response(
                                    name="calculate_fire_projections",
                                    response={
                                        "status": "success", 
                                        "message": "FIRE Roadmap generated and shown to user. Use this content to answer follow-up questions.",
                                        "roadmap_shown_to_user": roadmap
                                    }
                                )
                                
                                try:
                                    # This message won't be shown to user, but updates model's context
                                    self.chat.send_message(function_response)
                                    print("[DEBUG] Post-report context sent successfully")
                                except Exception as ctx_error:
                                    print(f"[WARN] Could not inject context: {ctx_error}")
                                
                                return roadmap

                            # For other tools, send result back to LLM
                            function_response = types.Part.from_function_response(
                                name=func_name,
                                response=result  # Pass raw result, not wrapped
                            )
                            
                            # Send function response back to model
                            followup = self.chat.send_message(function_response)

                            return self._process_response(followup)
                            
                        except Exception as e:
                            error_msg = f"Error executing {func_name}: {str(e)}"
                            print(f"[ERROR] {error_msg}")
                            return f"I encountered an error while calculating: {str(e)}"
                    else:
                        return f"Unknown function requested: {func_name}"
        
        # No function call found
        if not response.text:
            return "I apologize, but I couldn't process that request. Please try again."
            
        return response.text
    
    def send_message(self, user_message: str) -> str:
        """
        Send a message and get response with automatic retries.
        
        Args:
            user_message: The user's message
            
        Returns:
            The agent's response text
        """
        if not self.chat:
            raise RuntimeError("Session not started. Call start_session() first.")
        
        import time
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = self.chat.send_message(user_message)
                result = self._process_response(response)
                
                # Check for the generic error message which indicates failure
                if result == "I apologize, but I couldn't process that request. Please try again.":
                    if attempt < max_retries - 1:
                        print(f"[WARN] Received generic error. Retrying... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(1) # Brief pause before retry
                        continue
                
                return result
                
            except Exception as e:
                error_msg = f"Error processing message: {str(e)}"
                print(f"[ERROR] {error_msg}")
                
                if attempt < max_retries - 1:
                     print(f"[WARN] Exception occurred. Retrying... (Attempt {attempt + 1}/{max_retries})")
                     time.sleep(1)
                     continue
                
                raise
        
        return "I apologize, but I couldn't process that request. Please try again."
    
    def get_history(self) -> list:
        """Get conversation history."""
        if not self.chat:
            return []
        return self.chat.history if hasattr(self.chat, 'history') else []


def create_fire_chat(session_id: Optional[str] = None, history: Optional[list] = None, 
                     user_name: Optional[str] = None, api_key: Optional[str] = None):
    """
    Creates or retrieves a FIRE chat session.
    
    Args:
        session_id: Session identifier
        history: Optional conversation history
        user_name: Optional user name for personalization
        api_key: Gemini API key
        
    Returns:
        Chat session object
    """
    global _sessions
    
    # If we have an active session in memory, return it
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found")
    
    client = get_client()
    
    # Customize system instruction with user context
    instruction = SYSTEM_INSTRUCTIONS
    if user_name:
        instruction = f"User Name: {user_name}\n\n" + instruction
    
    # Define tools
    tools_list = [calculate_fire_projections, generate_fire_roadmap]
    
    # Initialize new chat with MANUAL function calling
    chat = client.chats.create(
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
    
    if session_id:
        _sessions[session_id] = chat
    
    return chat
