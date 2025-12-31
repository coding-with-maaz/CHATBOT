"""Main application entry point"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.config.settings import get_settings
from app.services.database import get_database_service
from app.services.gemini import get_gemini_service
from app.routes import api_router
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.middleware.error_handler import (
    exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from app.middleware.logging import LoggingMiddleware
from app.utils.logger import setup_logging, get_logger
from app.utils.response import success_response

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting application...")
    
    try:
        # Connect to MongoDB
        await get_database_service()
        logger.info("✅ MongoDB connected")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        # Continue even if MongoDB fails (for development)
    
    try:
        # Initialize AI service (OpenAI or Gemini based on config)
        settings = get_settings()
        if settings.AI_PROVIDER.lower() == "openai":
            from app.services.openai_service import get_openai_service
            get_openai_service()
            logger.info("✅ OpenAI AI initialized")
        else:
            get_gemini_service()
            logger.info("✅ Gemini AI initialized")
    except Exception as e:
        logger.error(f"❌ AI initialization failed: {e}")
        # Continue even if AI fails (for development)
    
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")
    try:
        db_service = await get_database_service()
        await db_service.disconnect()
        logger.info("✅ MongoDB disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting MongoDB: {e}")
    
    logger.info("✅ Application shut down")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A complete chatbot API with MongoDB and Gemini AI integration",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add exception handlers
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(500, exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include routers
app.include_router(api_router, prefix="/api")

# Mount static files
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
static_file_path = os.path.abspath(os.path.join(static_dir, "index.html"))

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve UI"""
    try:
        logger.debug(f"Serving UI from: {static_file_path}")
        logger.debug(f"File exists: {os.path.exists(static_file_path)}")
        if os.path.exists(static_file_path):
            with open(static_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                logger.debug(f"HTML content length: {len(html_content)}")
                return HTMLResponse(content=html_content)
        else:
            logger.warning(f"Static file not found at: {static_file_path}")
    except Exception as e:
        logger.error(f"Error serving static file: {e}", exc_info=True)
    
    # Fallback if static file doesn't exist
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot API</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
            a { color: #6366f1; text-decoration: none; margin: 0 10px; }
        </style>
    </head>
    <body>
        <h1>Python Chatbot API</h1>
        <p>API is running. Static files not found.</p>
        <a href="/docs">API Docs</a>
        <a href="/api/health">Health Check</a>
    </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
