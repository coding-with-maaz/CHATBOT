"""Chat routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.chat import ChatRequest, ChatResponse, ConversationHistory
from app.services.chat import get_chat_service
from app.utils.response import success_response, error_response
from app.utils.validators import validate_message, validate_conversation_id
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a chat message and get AI response
    
    - **message**: User's message (required)
    - **conversation_id**: Optional conversation ID for context
    - **chat_history**: Optional previous chat history
    """
    # Validate message
    is_valid, error_msg = validate_message(request.message)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Validate conversation ID if provided
    if request.conversation_id:
        is_valid, error_msg = validate_conversation_id(request.conversation_id)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        chat_service = await get_chat_service()
        result = await chat_service.send_message(
            message=request.message,
            conversation_id=request.conversation_id,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            timestamp=result["timestamp"]
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing chat request: {e}")
        
        # Handle quota/rate limit errors with appropriate status code
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower() or "429" in error_msg:
            raise HTTPException(
                status_code=429,
                detail=error_msg
            )
        # Handle other errors
        raise HTTPException(status_code=500, detail=f"Error processing chat: {error_msg}")


@router.get("/history/{conversation_id}")
async def get_history(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages to return")
):
    """Get conversation history"""
    # Validate conversation ID
    is_valid, error_msg = validate_conversation_id(conversation_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        chat_service = await get_chat_service()
        history = await chat_service.get_conversation_history(conversation_id, limit)
        
        return success_response(
            data=history.dict(),
            message="Conversation history retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.get("/conversations")
async def list_conversations(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of conversations to return")
):
    """List recent conversations from database"""
    try:
        chat_service = await get_chat_service()
        summaries = await chat_service.get_conversation_summaries(limit)
        
        # Convert to dict format
        conversations_data = [summary.dict() for summary in summaries]
        
        return success_response(
            data=conversations_data,
            message=f"Retrieved {len(conversations_data)} conversations from database",
            metadata={"count": len(conversations_data), "limit": limit}
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        # Return empty list instead of error to allow UI to work
        return success_response(
            data=[],
            message="No conversations found or database unavailable",
            metadata={"error": str(e)}
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    # Validate conversation ID
    is_valid, error_msg = validate_conversation_id(conversation_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        chat_service = await get_chat_service()
        deleted = await chat_service.delete_conversation(conversation_id)
        
        if deleted:
            return success_response(
                data={"conversation_id": conversation_id},
                message="Conversation deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

