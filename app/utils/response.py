"""Response formatting utilities"""

from typing import Any, Optional, Dict
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    metadata: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a success response"""
    response_data = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if metadata:
        response_data["metadata"] = metadata
    
    return JSONResponse(content=response_data, status_code=status_code)


def error_response(
    message: str = "An error occurred",
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create an error response"""
    response_data = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        response_data["details"] = details
    
    return JSONResponse(content=response_data, status_code=status_code)


def create_response(
    success: bool,
    data: Any = None,
    message: str = "",
    status_code: int = status.HTTP_200_OK,
    **kwargs
) -> JSONResponse:
    """Create a generic response"""
    if success:
        return success_response(data=data, message=message, status_code=status_code, metadata=kwargs)
    else:
        return error_response(
            message=message,
            status_code=status_code,
            error_code=kwargs.get("error_code"),
            details=kwargs.get("details")
        )

