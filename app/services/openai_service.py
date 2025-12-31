"""OpenAI AI service"""

from openai import AsyncOpenAI
from typing import List, Dict, Optional
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """OpenAI AI service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[AsyncOpenAI] = None
        self._initialized = False
    
    def initialize(self, force: bool = False) -> None:
        """Initialize OpenAI client"""
        if self._initialized and self.client and not force:
            return
        
        if not self.settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        try:
            # Initialize OpenAI client with just the API key
            self.client = AsyncOpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                timeout=30.0
            )
            self._initialized = True
            logger.info(f"✅ OpenAI client initialized successfully (model: {self.settings.OPENAI_MODEL})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}", exc_info=True)
            raise
    
    async def generate_response(
        self,
        prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using OpenAI API
        
        Args:
            prompt: User's message
            chat_history: Optional list of previous messages
        
        Returns:
            Generated response text
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # Build messages array
            messages = []
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    # Map assistant role to OpenAI's format
                    if role == "assistant":
                        messages.append({"role": "assistant", "content": content})
                    else:
                        messages.append({"role": "user", "content": content})
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating response: {e}")
            
            # Handle quota/rate limit errors
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                raise Exception(
                    "API quota exceeded. Your OpenAI API quota has been reached. "
                    "Please check your usage at https://platform.openai.com/usage or wait a few minutes before trying again."
                )
            elif "401" in error_str or "invalid" in error_str.lower():
                raise Exception("Invalid API key. Please check your OpenAI API key.")
            else:
                raise Exception(f"Error generating response: {error_str}")
    
    def get_model_info(self) -> Dict[str, str]:
        """Get model information"""
        if not self._initialized:
            self.initialize()
        
        return {
            "model_name": self.settings.OPENAI_MODEL,
            "status": "initialized" if self._initialized else "not_initialized",
            "provider": "OpenAI"
        }
    
    def is_initialized(self) -> bool:
        """Check if client is initialized"""
        return self._initialized


# Global instance
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """Get OpenAI service instance"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
        _openai_service.initialize()
    return _openai_service

