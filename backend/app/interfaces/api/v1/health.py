"""Health Check API Router."""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config import settings
from app.infrastructure.database.session import get_async_db
from app.interfaces.schemas.common import HealthCheckResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Service health check",
    description="Returns service liveness status and database connectivity check.",
)
async def health_check(db: AsyncSession = Depends(get_async_db)) -> HealthCheckResponse:
    """Checks application liveness and PostgreSQL/SQLite database connectivity."""
    db_status = "unavailable"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        db_status = f"error: {exc}"

    return HealthCheckResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
    )
