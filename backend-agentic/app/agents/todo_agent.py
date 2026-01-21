import os
from openai import OpenAI
from app.mcp.registry import mcp_registry
from typing import Dict, Any, List
from pydantic import BaseModel

class AgentConfig(BaseModel):
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000

class TodoAgent:
    def __init__(self, api_key: str = None):
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.config = AgentConfig()
        
        # Get all registered tools for the agent
        self.tools = self._prepare_tools_for_agent()
    
    def _prepare_tools_for_agent(self) -> List[Dict[str, Any]]:
        """
        Prepare MCP tools in the format required by OpenAI's function calling
        """
        tools = []
        for name, definition in mcp_registry.get_all_tool_definitions().items():
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": definition.description,
                    "parameters": definition.parameters
                }
            })
        return tools
    
    def process_message(self, user_message: str, user_id: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Process a user message using the agent with MCP tools
        """
        # Prepare the messages for the agent
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant for managing tasks. Use the provided tools to add, list, update, complete, or delete tasks. Always ask for clarification if the user doesn't provide sufficient information for a tool. Be friendly and concise in your responses."
            }
        ]
        
        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Call the OpenAI API with tools
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",  # Let the model decide which tool to use
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # Process the response
            response_message = response.choices[0].message
            
            # If the model wants to call a tool
            tool_calls = response_message.tool_calls
            if tool_calls:
                # Extend conversation with assistant's tool request
                messages.append(response_message)
                
                # Execute each tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)  # Note: In production, use json.loads
                    
                    # Add user_id to function args if not present
                    if 'user_id' not in function_args:
                        function_args['user_id'] = user_id
                    
                    # Execute the tool
                    try:
                        tool_result = mcp_registry.execute_tool(function_name, **function_args)
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "name": function_name,
                            "content": str(tool_result),
                            "tool_call_id": tool_call.id
                        })
                    except Exception as e:
                        # Add error to messages
                        messages.append({
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error executing tool: {str(e)}",
                            "tool_call_id": tool_call.id
                        })
                
                # Get final response from the model based on tool results
                final_response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
                
                return final_response.choices[0].message.content
            
            # If no tool calls were made, return the assistant's response directly
            else:
                return response_message.content or "I processed your request."
        
        except Exception as e:
            return f"I'm sorry, I encountered an error processing your request: {str(e)}"
    
    def get_available_tools(self) -> Dict[str, Any]:
        """
        Get information about all available tools
        """
        return {
            "tools": [definition.model_dump() for definition in mcp_registry.get_all_tool_definitions().values()]
        }

# Global agent instance
todo_agent = None

def get_agent() -> TodoAgent:
    """
    Get the global agent instance, creating it if it doesn't exist
    """
    global todo_agent
    if not todo_agent:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        todo_agent = TodoAgent(api_key=api_key)
    return todo_agent