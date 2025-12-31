"""Error handling middleware"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.logger import get_logger
from app.utils.response import error_response

logger = get_logger(__name__)


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return error_response(
        message="An internal server error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR"
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP exception handler"""
    return error_response(
        message=exc.detail,
        status_code=exc.status_code,
        error_code="HTTP_ERROR"
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Validation exception handler"""
    errors = exc.errors()
    return error_response(
        message="Validation error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        details={"errors": errors}
    )

