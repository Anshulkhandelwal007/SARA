from fastapi import APIRouter
from schemas.common import HealthResponse
from core.database import engine
from sqlalchemy import text
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_connected = False
    
    return HealthResponse(
        status="healthy" if db_connected else "unhealthy",
        version="1.0.0",
        database_connected=db_connected,
        timestamp=datetime.utcnow().isoformat()
    )
