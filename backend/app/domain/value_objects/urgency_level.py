"""Domain Value Objects — Urgency Level Enum.

Defines the four clinical risk stratification levels used throughout
the triage decision tree evaluation, adapted from the Manchester Triage
System (MTS) and Emergency Severity Index (ESI).

See /docs/RuleEngineDesign.md for full classification definitions.
"""


from enum import Enum


class UrgencyLevel(str, Enum):
    """Four-tier clinical urgency classification.

    - RED: Life-threatening emergency. Immediate intervention required.
    - ORANGE: Very urgent. Hospital evaluation within 60 minutes.
    - YELLOW: Urgent. Clinic visit within 24 hours.
    - GREEN: Non-urgent. Self-care guidance; routine appointment.
    """

    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

    @property
    def timeframe_hours(self) -> int:
        """Returns the maximum recommended care timeframe in hours."""
        mapping = {
            UrgencyLevel.RED: 0,
            UrgencyLevel.ORANGE: 1,
            UrgencyLevel.YELLOW: 24,
            UrgencyLevel.GREEN: 72,
        }
        return mapping[self]

    @property
    def display_label(self) -> str:
        """Returns a human-readable urgency label string."""
        labels = {
            UrgencyLevel.RED: "Emergency",
            UrgencyLevel.ORANGE: "Very Urgent",
            UrgencyLevel.YELLOW: "Urgent",
            UrgencyLevel.GREEN: "Non-Urgent",
        }
        return labels[self]
