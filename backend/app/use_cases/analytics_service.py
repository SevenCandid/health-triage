"""Analytics Service — Use Case Layer."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Generates aggregate anonymized triage metrics for admin dashboards.

    TODO (Phase 2 — FR-ANL-001):
        Implement async SQL aggregation queries using GROUP BY urgency_level,
        date_trunc('week', conducted_at), and primary_symptom to produce
        real-time dashboard metrics.

        All queries MUST strip PII fields before ingestion per FR-ANL-002.
    """

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Returns a stub analytics dashboard payload.

        TODO (Phase 2): Replace with live PostgreSQL aggregate queries.
        """
        logger.info("Analytics dashboard metrics requested (stub response).")
        return {
            "total_sessions": 0,
            "severity_breakdown": {
                "RED": 0,
                "ORANGE": 0,
                "YELLOW": 0,
                "GREEN": 0,
            },
            "top_symptoms": [],
            "sessions_this_week": 0,
            "note": "Analytics aggregation is not yet implemented. See Phase 2 roadmap.",
        }
