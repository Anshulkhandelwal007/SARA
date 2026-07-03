from fastapi import APIRouter
from schemas.response import StandardResponse, HealthResponse
from core.database import engine
from sqlalchemy import text
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=StandardResponse[HealthResponse])
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_connected = True
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_connected = False
        db_status = "disconnected"
    
    health_data = HealthResponse(
        status="healthy" if db_connected else "unhealthy",
        database=db_status,
        timestamp=datetime.utcnow().isoformat()
    )
    
    return StandardResponse(
        success=db_connected,
        data=health_data,
        message="Service is healthy" if db_connected else "Service is unhealthy",
        errors=None if db_connected else ["Database connection failed"],
        meta={"timestamp": datetime.utcnow().isoformat()}
    )
