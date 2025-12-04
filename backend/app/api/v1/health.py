from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint to verify service status.
    """
    return {
        "status": "ok",
        "service": "vaaniai-backend",
        "version": settings.VERSION
    }