"""Health check routes"""

from fastapi import APIRouter, HTTPException
from app.services.database import get_database_service
from app.utils.response import success_response, error_response
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def health_check():
    """Health check endpoint"""
    db_service = await get_database_service()
    db_healthy = await db_service.health_check()
    
    if db_healthy:
        return success_response(
            data={
                "status": "healthy",
                "database": "connected",
                "services": {
                    "mongodb": "connected"
                }
            },
            message="All services are healthy"
        )
    else:
        return error_response(
            message="Database connection failed",
            status_code=503,
            error_code="SERVICE_UNAVAILABLE"
        )


@router.get("/db")
async def db_info():
    """Get database information"""
    try:
        db_service = await get_database_service()
        db = db_service.get_database()
        
        if not db:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        collections = await db.list_collection_names()
        
        return success_response(
            data={
                "database_name": db.name,
                "collections": collections,
                "collection_count": len(collections)
            },
            message="Database information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return error_response(
            message=str(e),
            status_code=500,
            error_code="DATABASE_ERROR"
        )

