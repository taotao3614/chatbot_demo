"""
Main application entry point for the Chatbot MVP.
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.models import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A simple chatbot MVP with extensible architecture",
    version="0.1.0",
    debug=True  # 启用调试模式
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Custom validation error handler for user-friendly messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """自定义验证错误处理器，提供用户友好的错误消息"""
    errors = exc.errors()
    
    # 检查是否是空输入错误
    for error in errors:
        if (error.get("loc") == ["body", "user_text"] and 
            error.get("type") == "string_too_short"):
            return JSONResponse(
                status_code=422,
                content={
                    "error_code": "EMPTY_INPUT",
                    "message": "Please enter a message to continue our conversation.",
                    "details": {
                        "field": "user_text",
                        "issue": "Message cannot be empty"
                    }
                }
            )
        elif (error.get("loc") == ["body", "user_text"] and 
              error.get("type") == "string_too_long"):
            return JSONResponse(
                status_code=422,
                content={
                    "error_code": "MESSAGE_TOO_LONG",
                    "message": "Your message is too long. Please keep it under 1000 characters.",
                    "details": {
                        "field": "user_text",
                        "max_length": 1000
                    }
                }
            )
    
    # 默认验证错误处理
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "INVALID_INPUT",
            "message": "Please check your input and try again.",
            "details": {"errors": errors}
        }
    )

# Include routers with versioning
app.include_router(
    health_router,
    prefix="/api/v1"
)
app.include_router(
    chat_router,
    prefix="/api/v1"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {
            "error_code": "HTTP_ERROR",
            "message": str(exc.detail)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred"
        ).dict()
    )

# Root endpoint to serve the chat interface
@app.get("/")
async def read_root():
    """Redirect to the chat interface"""
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.app_name} v0.1.0")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # 禁用热重载
        log_level="info"
    )