"""
Orchestrator - The Brain of the Car Agent.
Connects Gemini LLM with deterministic tools using MANUAL function calling.
This allows us to bypass the LLM's "interpretation" of tool outputs.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any

from google import genai
from google.genai import types

from execution.car_calculators import calculate_car_affordability
from execution.generate_car_report import generate_car_report


# Global client instance
_client = None
_sessions = {}  # Session storage for chat instances

# Tool registry for manual function calling
TOOLS = {
    "calculate_car_affordability": calculate_car_affordability,
    "generate_car_report": generate_car_report,
}


def get_client():
    """Configure and return the GenAI Client."""
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        _client = genai.Client(api_key=api_key)
    return _client


class CarOrchestrator:
    """Orchestrates the car affordability conversation using MANUAL function calling."""
    
    def __init__(self, api_key: str):
        """Initialize with Gemini API key."""
        os.environ["GEMINI_API_KEY"] = api_key
        self.client = get_client()
        self.chat = None
        self.last_calculation = None  # Store last calculation for report generation
    
    def start_session(self, session_id: Optional[str] = None, user_name: Optional[str] = None) -> str:
        """
        Start a new chat session.
        
        Args:
            session_id: Optional session identifier for tracking
            user_name: Optional user name for personalization
            
        Returns:
            Initial greeting from the agent
        """
        # Load system instructions
        directive_path = Path(__file__).parent.parent / "directives" / "calculate_car_affordability.md"
        with open(directive_path, "r") as f:
            system_instruction = f.read()
        
        # Define tools for function calling
        tools = [
            types.Tool(function_declarations=[
                types.FunctionDeclaration(
                    name="calculate_car_affordability",
                    description="Calculate car affordability based on income, expenses, investments, and desired car class. Returns a comprehensive analysis including 10% rule, TCO, and opportunity cost.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "annual_income": types.Schema(
                                type=types.Type.NUMBER,
                                description="Annual income (after taxes)"
                            ),
                            "annual_expenses": types.Schema(
                                type=types.Type.NUMBER,
                                description="Annual expenses"
                            ),
                            "current_investments": types.Schema(
                                type=types.Type.NUMBER,
                                description="Current invested assets (optional, for opportunity cost)"
                            ),
                            "desired_car_class": types.Schema(
                                type=types.Type.STRING,
                                description="The car class of interest: 'budget', 'luxury', or 'supercar'"
                            ),
                        },
                        required=["annual_income", "annual_expenses", "desired_car_class"]
                    )
                ),
                types.FunctionDeclaration(
                    name="generate_car_report",
                    description="Generate a detailed Car Affordability Report in Markdown format based on the calculation results.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "use_last_calculation": types.Schema(
                                type=types.Type.BOOLEAN,
                                description="Use the results from the last calculate_car_affordability call"
                            ),
                        },
                        required=["use_last_calculation"]
                    )
                ),
            ])
        ]
        
        # Create chat with manual function calling
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                temperature=0.7,
            )
        )
        
        return "Hello! I am your Car Coach, an educational tool to help you understand how much car you can realistically afford. To start, what is your annual income (after taxes)?"
    
    def _process_response(self, response) -> str:
        """
        Process the LLM response, handling any function calls manually.
        
        If the LLM requests a function call, execute it and:
        - For `generate_car_report`: Return the result DIRECTLY (verbatim)
        - For other tools: Send result back to LLM for interpretation
        """
        # Check if there's a function call
        if not response.candidates or not response.candidates[0].content.parts:
            return "I'm sorry, I didn't understand that. Could you please rephrase?"
        
        for part in response.candidates[0].content.parts:
            if part.function_call:
                func_name = part.function_call.name
                func_args = dict(part.function_call.args) if part.function_call.args else {}
                
                # Execute the function
                if func_name == "calculate_car_affordability":
                    # Handle optional parameter
                    if "current_investments" not in func_args:
                        func_args["current_investments"] = 0
                    
                    result = calculate_car_affordability(**func_args)
                    self.last_calculation = result  # Store for reference
                    
                    # CHAIN: Immediately generate report and return VERBATIM
                    # This bypasses LLM interpretation entirely
                    report = generate_car_report(result)
                    
                    # Acknowledge to LLM that we handled both tools
                    function_response = types.Content(
                        role="function",
                        parts=[types.Part(
                            function_response=types.FunctionResponse(
                                name=func_name,
                                response={"result": "Calculation complete. Report generated and displayed to user."}
                            )
                        )]
                    )
                    self.chat.send_message(function_response)
                    
                    return report  # Return report directly, bypass LLM
                
                elif func_name == "generate_car_report":
                    if self.last_calculation is None:
                        return "I need to run the calculations first. Let me gather your information."
                    
                    # Generate report and return VERBATIM (bypass LLM)
                    report = generate_car_report(self.last_calculation)
                    
                    # Still need to acknowledge to the LLM that we handled it
                    function_response = types.Content(
                        role="function",
                        parts=[types.Part(
                            function_response=types.FunctionResponse(
                                name=func_name,
                                response={"result": "Report generated and displayed to user."}
                            )
                        )]
                    )
                    # Send acknowledgment but DON'T use its response
                    self.chat.send_message(function_response)
                    
                    return report  # Return report directly
                
                else:
                    return f"Unknown function: {func_name}"
        
        # No function call, return the text response
        if response.candidates[0].content.parts[0].text:
            return response.candidates[0].content.parts[0].text
        
        return "I'm not sure how to respond to that."
    
    def send_message(self, user_message: str) -> str:
        """
        Send a message and get response with automatic retries.
        
        Args:
            user_message: The user's message
            
        Returns:
            The agent's response text
        """
        if self.chat is None:
            self.start_session()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.chat.send_message(user_message)
                return self._process_response(response)
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"I encountered an error: {str(e)}. Please try again."
                continue
        
        return "I'm having trouble processing your request. Please try again."
    
    def get_history(self) -> list:
        """Get conversation history."""
        if self.chat is None:
            return []
        return list(self.chat.get_history())


def create_car_chat(session_id: Optional[str] = None, history: Optional[list] = None, 
                    user_name: Optional[str] = None, api_key: Optional[str] = None):
    """
    Creates or retrieves a Car chat session.
    
    Args:
        session_id: Session identifier
        history: Optional conversation history
        user_name: Optional user name for personalization
        api_key: Gemini API key
        
    Returns:
        Chat session object
    """
    global _sessions
    
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY required")
    
    orchestrator = CarOrchestrator(api_key)
    orchestrator.start_session(session_id=session_id, user_name=user_name)
    
    if session_id:
        _sessions[session_id] = orchestrator
    
    return orchestrator
