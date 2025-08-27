"""
Health check and system status endpoints.
"""
from datetime import datetime
from fastapi import APIRouter
from app.api.models import HealthResponse
from app.state.session_manager import session_manager
from app import __version__

router = APIRouter(
    tags=["health"]
)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns basic system status and version information.
    """
    return HealthResponse(
        ok=True,
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=__version__
    )


@router.get("/status")
async def system_status():
    """
    Detailed system status endpoint.
    Includes session statistics and system health metrics.
    """
    session_stats = session_manager.get_session_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": __version__,
        "session_statistics": session_stats,
        "components": {
            "intent_classifier": "active",
            "session_manager": "active",
            "response_policy": "active"
        }
    }
