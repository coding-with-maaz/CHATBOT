"""Validation utilities"""

import re
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_message(message: str, min_length: int = 1, max_length: int = 5000) -> tuple[bool, Optional[str]]:
    """
    Validate chat message
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not message:
        return False, "Message cannot be empty"
    
    if not isinstance(message, str):
        return False, "Message must be a string"
    
    message = message.strip()
    
    if len(message) < min_length:
        return False, f"Message must be at least {min_length} characters"
    
    if len(message) > max_length:
        return False, f"Message must not exceed {max_length} characters"
    
    return True, None


def validate_conversation_id(conversation_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate conversation ID format
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not conversation_id:
        return False, "Conversation ID cannot be empty"
    
    # Allow alphanumeric, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, conversation_id):
        return False, "Conversation ID contains invalid characters"
    
    if len(conversation_id) > 100:
        return False, "Conversation ID is too long"
    
    return True, None


def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially harmful characters (basic sanitization)
    text = text.replace('\x00', '')
    
    return text

