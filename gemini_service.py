import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = None

def initialize_model():
    """Initialize the Gemini model"""
    global model
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini model initialized successfully")
        return model
    except Exception as e:
        print(f"❌ Failed to initialize Gemini model: {e}")
        raise


async def generate_response(prompt: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Generate a response using Gemini API
    
    Args:
        prompt: User's message
        chat_history: Optional list of previous messages in format [{"role": "user", "content": "..."}, ...]
    
    Returns:
        Generated response text
    """
    global model
    
    if model is None:
        initialize_model()
    
    try:
        # If chat history exists, build conversation context
        if chat_history:
            # Convert chat history to Gemini's format
            conversation = []
            for msg in chat_history:
                role = "user" if msg.get("role") == "user" else "model"
                conversation.append({
                    "role": role,
                    "parts": [msg.get("content", "")]
                })
            # Add current prompt
            conversation.append({
                "role": "user",
                "parts": [prompt]
            })
            
            # Generate response with conversation context
            response = model.generate_content(conversation)
        else:
            # Simple prompt without history
            response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")


def get_model_info():
    """Get information about the current model"""
    global model
    if model is None:
        initialize_model()
    return {
        "model_name": "gemini-pro",
        "status": "initialized"
    }

