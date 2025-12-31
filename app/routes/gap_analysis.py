"""Gap Analysis Routes"""

from fastapi import APIRouter, HTTPException, Query
from app.services.gap_analysis import get_gap_analysis_service
from app.utils.response import success_response
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/conversation/{conversation_id}")
async def analyze_conversation(conversation_id: str):
    """
    Analyze a specific conversation for gaps
    
    - **conversation_id**: ID of the conversation to analyze
    """
    try:
        gap_service = await get_gap_analysis_service()
        analysis = await gap_service.analyze_conversation(conversation_id)
        
        return success_response(
            data=analysis,
            message="Gap analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing conversation: {str(e)}"
        )


@router.get("/all")
async def analyze_all_conversations():
    """
    Analyze all conversations for overall patterns and gaps
    """
    try:
        gap_service = await get_gap_analysis_service()
        analysis = await gap_service.analyze_all_conversations()
        
        return success_response(
            data=analysis,
            message="Gap analysis of all conversations completed"
        )
    except Exception as e:
        logger.error(f"Error analyzing all conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing conversations: {str(e)}"
        )

