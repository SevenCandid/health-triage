"""Emergency Dispatch Pydantic v2 Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class GpsLocation(BaseModel):
    """GPS coordinate payload."""

    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    accuracy_meters: Optional[float] = Field(default=None, ge=0.0)


class EmergencyDispatchRequest(BaseModel):
    """Emergency alert dispatch request payload.

    See /docs/EmergencySystem.md — Section 3.2
    """

    triage_session_id: str
    urgency_level: str = "RED"
    primary_symptom: str
    location: GpsLocation


class EmergencyDispatchResponse(BaseModel):
    """Emergency alert dispatch confirmation response."""

    log_id: str
    triage_session_id: str
    status: str
    triggered_at: datetime
    sms_payload: Optional[str] = None  # Pre-formatted SMS string for client to dispatch

    model_config = {"from_attributes": True}
