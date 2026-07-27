"""Domain Unit Tests — UrgencyLevel Value Object."""

import pytest
from app.domain.value_objects.urgency_level import UrgencyLevel


def test_urgency_level_values():
    """All four urgency levels must be defined."""
    assert UrgencyLevel.RED.value == "RED"
    assert UrgencyLevel.ORANGE.value == "ORANGE"
    assert UrgencyLevel.YELLOW.value == "YELLOW"
    assert UrgencyLevel.GREEN.value == "GREEN"


def test_urgency_level_timeframes():
    """Timeframe hours must follow clinical priority order."""
    assert UrgencyLevel.RED.timeframe_hours == 0
    assert UrgencyLevel.ORANGE.timeframe_hours == 1
    assert UrgencyLevel.YELLOW.timeframe_hours == 24
    assert UrgencyLevel.GREEN.timeframe_hours == 72


def test_urgency_display_labels():
    """Display labels must be human-readable strings."""
    assert "Emergency" in UrgencyLevel.RED.display_label
    assert "Urgent" in UrgencyLevel.ORANGE.display_label
