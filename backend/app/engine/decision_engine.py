"""Decision Engine module.

Maps severity levels and evaluation outcomes to high-level clinical system action protocols.
"""

import logging
from typing import Dict, Any
from app.models.severity_level import UrgencyCode

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Provides decision outcome protocols based on evaluated urgency levels."""

    ACTION_MAP = {
        UrgencyCode.RED: {
            "action": "EMERGENCY_DISPATCH",
            "timeframe_hours": 0,
            "guidance": "Call emergency services immediately or go to the nearest emergency department."
        },
        UrgencyCode.ORANGE: {
            "action": "SEEK_URGENT_CARE",
            "timeframe_hours": 1,
            "guidance": "Visit a hospital or urgent care clinic within 60 minutes."
        },
        UrgencyCode.YELLOW: {
            "action": "VISIT_CLINIC",
            "timeframe_hours": 24,
            "guidance": "Visit a community clinic or doctor within 24 hours."
        },
        UrgencyCode.GREEN: {
            "action": "SELF_CARE",
            "timeframe_hours": 72,
            "guidance": "Monitor symptoms at home. Rest and hydrate. Seek care if symptoms worsen."
        }
    }

    def get_action_protocol(self, urgency: UrgencyCode) -> Dict[str, Any]:
        """Returns action protocol metadata for the given urgency level."""
        return self.ACTION_MAP.get(urgency, self.ACTION_MAP[UrgencyCode.GREEN])
