"""API v1 package init — exposes sub-module references for router aggregation."""

from app.interfaces.api.v1 import (
    analytics,
    assessment,
    auth,
    consultation,
    emergency,
    health,
    sync,
    users,
)

__all__ = [
    "analytics",
    "assessment",
    "auth",
    "consultation",
    "emergency",
    "health",
    "sync",
    "users",
]
