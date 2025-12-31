"""AI model routes"""

from fastapi import APIRouter
from app.services.chat import get_chat_service
from app.config.settings import get_settings
from app.utils.response import success_response
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/info")
async def ai_info():
    """Get AI model information"""
    try:
        settings = get_settings()
        chat_service = await get_chat_service()
        model_info = chat_service.ai_service.get_model_info()
        
        # Add provider info
        model_info["provider"] = settings.AI_PROVIDER
        model_info["available_providers"] = {
            "openai": settings.OPENAI_API_KEY is not None,
            "gemini": settings.GEMINI_API_KEY is not None
        }
        
        return success_response(
            data=model_info,
            message="AI model information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting AI info: {e}")
        return success_response(
            data={
                "status": "error",
                "message": str(e),
                "provider": get_settings().AI_PROVIDER
            },
            message="Failed to retrieve AI model information"
        )

