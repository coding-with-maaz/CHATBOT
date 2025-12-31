"""Gemini AI service"""

import google.generativeai as genai
from typing import List, Dict, Optional
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Google Gemini AI service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self._initialized = False
    
    def initialize(self, force: bool = False) -> None:
        """Initialize Gemini model"""
        if self._initialized and self.model and not force:
            return
        
        if not self.settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            # Use the model from settings, fallback to gemini-2.0-flash if not set
            model_name = self.settings.GEMINI_MODEL or "gemini-2.0-flash"
            
            # Try to initialize the model
            try:
                self.model = genai.GenerativeModel(model_name)
                self._initialized = True
                logger.info(f"✅ Gemini model '{model_name}' initialized successfully")
            except Exception as model_error:
                # If model not found, try fallback
                if "not found" in str(model_error).lower() or "404" in str(model_error):
                    fallback_models = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-2.5-flash"]
                    logger.warning(f"Model '{model_name}' not found, trying fallback models...")
                    for fallback in fallback_models:
                        try:
                            logger.info(f"Trying fallback model: {fallback}")
                            self.model = genai.GenerativeModel(fallback)
                            self._initialized = True
                            logger.info(f"✅ Gemini model '{fallback}' initialized successfully")
                            break
                        except Exception as e2:
                            continue
                    else:
                        logger.error(f"❌ All fallback models failed")
                        raise model_error
                else:
                    raise model_error
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini model: {e}")
            raise
    
    async def generate_response(
        self,
        prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using Gemini API
        
        Args:
            prompt: User's message
            chat_history: Optional list of previous messages
        
        Returns:
            Generated response text
        """
        if not self._initialized:
            self.initialize()
        
        try:
            if chat_history:
                # Build conversation context
                conversation = []
                for msg in chat_history:
                    role = "user" if msg.get("role") == "user" else "model"
                    conversation.append({
                        "role": role,
                        "parts": [msg.get("content", "")]
                    })
                conversation.append({
                    "role": "user",
                    "parts": [prompt]
                })
                response = self.model.generate_content(conversation)
            else:
                response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating response: {e}")
            
            # Handle quota exceeded errors
            if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                raise Exception(
                    "API quota exceeded. Your free tier limit has been reached. "
                    "Please check your usage at https://ai.dev/usage or wait a few minutes before trying again."
                )
            # Handle rate limit errors
            elif "rate limit" in error_str.lower() or "retry" in error_str.lower():
                # Extract retry delay if available
                import re
                retry_match = re.search(r'retry in (\d+\.?\d*)s', error_str)
                if retry_match:
                    wait_time = retry_match.group(1)
                    raise Exception(
                        f"Rate limit reached. Please wait {wait_time} seconds before trying again."
                    )
                raise Exception("Rate limit reached. Please wait a moment and try again.")
            # Handle other errors
            else:
                raise Exception(f"Error generating response: {error_str}")
    
    def get_model_info(self) -> Dict[str, str]:
        """Get model information"""
        if not self._initialized:
            self.initialize()
        
        return {
            "model_name": self.settings.GEMINI_MODEL,
            "status": "initialized" if self._initialized else "not_initialized",
            "provider": "Google Gemini"
        }
    
    def is_initialized(self) -> bool:
        """Check if model is initialized"""
        return self._initialized


# Global instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
        _gemini_service.initialize()
    return _gemini_service

