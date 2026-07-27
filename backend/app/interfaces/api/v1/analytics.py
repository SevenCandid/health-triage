"""Analytics Dashboard API Router."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.interfaces.api.dependencies import get_analytics_service
from app.use_cases.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    summary="Aggregate triage analytics metrics",
    description=(
        "Returns anonymized aggregate triage statistics for admin dashboards. "
        "TODO (Phase 2 — FR-ANL-001): Implement live PostgreSQL aggregate queries. "
        "Currently returns a stub response. See /docs/FunctionalRequirements.md FR-ANL."
    ),
)
async def get_dashboard(
    service: AnalyticsService = Depends(get_analytics_service),
) -> Dict[str, Any]:
    """Returns aggregate triage dashboard metrics."""
    return await service.get_dashboard_metrics()
