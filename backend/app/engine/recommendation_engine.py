"""Recommendation Engine module.

Retrieves and filters clinical recommendations based on identified health concerns.
"""

import logging
from typing import List, Optional
from app.models.recommendation import RecommendationModel

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Retrieves patient self-care and medical guidance recommendations."""

    def get_recommendations_for_concern(
        self,
        recommendations: List[RecommendationModel],
        health_concern_id: Optional[str]
    ) -> List[str]:
        """Filters active recommendations linked to the given health concern.

        Returns a list of string recommendations.
        """
        if not health_concern_id:
            return []

        matched = [
            r.content_en for r in recommendations
            if r.is_active and r.health_concern_id == health_concern_id
        ]
        logger.debug(f"Retrieved {len(matched)} recommendations for health concern {health_concern_id}")
        return matched
