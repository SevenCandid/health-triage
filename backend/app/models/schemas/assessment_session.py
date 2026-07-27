"""AssessmentSession Pydantic v2 Schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.assessment_session import SessionStatus, ConsultationMode


class AssessmentSessionCreate(BaseModel):
    user_id: Optional[str] = None
    symptom_id: Optional[str] = None
    status: SessionStatus = SessionStatus.IN_PROGRESS
    consultation_mode: ConsultationMode = ConsultationMode.TEXT
    language_code: str = Field(default="en", max_length=10)
    created_offline: bool = False
    conducted_at: datetime = Field(default_factory=datetime.utcnow)
    client_session_id: Optional[str] = Field(None, max_length=36)
    raw_answers_snapshot: Optional[Dict[str, Any]] = None


class AssessmentSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str]
    symptom_id: Optional[str]
    identified_concern_id: Optional[str]
    severity_level_id: Optional[str]
    status: SessionStatus
    consultation_mode: ConsultationMode
    language_code: str
    created_offline: bool
    conducted_at: datetime
    synced_at: Optional[datetime]
    client_session_id: Optional[str]
    ai_explanation: Optional[str]
    raw_answers_snapshot: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class AssessmentSessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    symptom_id: Optional[str]
    severity_level_id: Optional[str]
    status: SessionStatus
    conducted_at: datetime
    created_offline: bool
