"""Chat-related data models"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content", min_length=1)
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1, max_length=5000)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    chat_history: Optional[List[ChatMessage]] = Field(None, description="Previous chat history")
    stream: bool = Field(False, description="Whether to stream the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is Python?",
                "conversation_id": "conv_abc123",
                "chat_history": [],
                "stream": False
            }
        }


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    message_id: Optional[str] = Field(None, description="Message ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Python is a programming language...",
                "conversation_id": "conv_abc123",
                "timestamp": "2024-01-01T12:00:00Z",
                "message_id": "msg_xyz789"
            }
        }


class ConversationHistory(BaseModel):
    """Conversation history model"""
    conversation_id: str
    messages: List[ChatMessage]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0


class ConversationSummary(BaseModel):
    """Conversation summary model"""
    conversation_id: str
    first_message: Optional[str] = None
    last_message: Optional[str] = None
    message_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

