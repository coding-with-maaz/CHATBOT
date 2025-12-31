"""Application settings and configuration"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Python Chatbot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # MongoDB Configuration
    MONGO_URI: Optional[str] = None
    MONGO_USERNAME: Optional[str] = None
    MONGO_PASSWORD: Optional[str] = None
    MONGO_HOST: Optional[str] = None
    MONGO_DB_NAME: str = "drtoolofficial_db"
    MONGO_USE_SRV: bool = False
    
    # AI Provider Configuration
    AI_PROVIDER: str = "openai"  # Options: "openai" or "gemini"
    
    # Gemini API Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"  # Available: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash, gemini-flash-latest
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # Available: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Chat Configuration
    MAX_CHAT_HISTORY: int = 50
    DEFAULT_CONVERSATION_TTL_DAYS: int = 30
    
    def get_mongo_uri(self) -> str:
        """Get MongoDB connection URI"""
        if self.MONGO_URI:
            return self.MONGO_URI
        
        if not all([self.MONGO_USERNAME, self.MONGO_PASSWORD, self.MONGO_HOST]):
            raise ValueError("MongoDB credentials not properly configured")
        
        protocol = "mongodb+srv" if self.MONGO_USE_SRV else "mongodb"
        return f"{protocol}://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}/{self.MONGO_DB_NAME}?retryWrites=true&w=majority"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

