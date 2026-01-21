import os
from typing import Dict, Any, List
from openai import OpenAI
from app.models.conversation import Message
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    def process_message(self, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Process a user message and return AI response.
        """
        try:
            # Prepare the messages for the API
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant for managing todos and tasks. Respond in a friendly, concise manner. If the user wants to create, update, or manage tasks, acknowledge their request and suggest how they can use the app to accomplish it. If they speak in Urdu, respond in Urdu. If they speak in English, respond in English."
                }
            ]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response
            ai_response = response.choices[0].message.content.strip()
            return ai_response
            
        except Exception as e:
            # Return a generic error response
            print(f"Error in AI processing: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request. Could you please try again?"

# Global instance
ai_client = AIClient()

def get_ai_response(message: str, conversation_history: List[Dict[str, str]] = None) -> str:
    """
    Get response from AI for a given message.
    """
    return ai_client.process_message(message, conversation_history)