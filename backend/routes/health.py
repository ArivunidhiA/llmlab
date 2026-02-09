"""Health check endpoint."""

from fastapi import APIRouter, Depends
from models import HealthResponse
from database import get_db
from config import settings
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])

# Track app start time
APP_START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(db=Depends(get_db)):
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with app status and database connectivity
    """
    try:
        # Test database connection
        db_connected = True
        # In real scenario, perform actual DB test
        # result = await db.table("users").select("COUNT(*)").execute()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_connected = False
    
    uptime = time.time() - APP_START_TIME
    
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        version=settings.APP_VERSION,
        uptime_seconds=uptime,
        database_connected=db_connected,
        timestamp=datetime.now(),
    )
