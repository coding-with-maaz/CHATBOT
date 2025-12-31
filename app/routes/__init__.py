"""Routes module"""

from fastapi import APIRouter
from app.routes import chat, health, ai, gap_analysis

# Create main router
api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(gap_analysis.router, prefix="/gap-analysis", tags=["Gap Analysis"])

__all__ = ["api_router"]

