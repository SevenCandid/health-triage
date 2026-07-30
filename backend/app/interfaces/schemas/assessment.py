"""Assessment API Pydantic v2 Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.health_conversation import ConversationStatus as SessionStatus, ConsultationMode
from app.models.severity_level import UrgencyCode


class AssessmentStartRequest(BaseModel):
    """Payload to start a new assessment session."""
    language_code: str = Field(default="en", pattern="^(en|tw)$")
    consultation_mode: ConsultationMode = ConsultationMode.TEXT
    created_offline: bool = False


class AssessmentStartResponse(BaseModel):
    """Response returned upon starting a session."""
    session_id: str
    status: SessionStatus
    language_code: str
    consultation_mode: ConsultationMode
    created_at: datetime
    pending_symptom: Optional[str] = None
    pending_symptom_slug: Optional[str] = None
    pending_session_id: Optional[str] = None


class AssessmentSymptomsRequest(BaseModel):
    """Payload to set the initial primary symptom for a session."""
    session_id: str
    symptom_slug: str = Field(..., min_length=1, max_length=500)
    user_text: Optional[str] = None


class QuestionOptionDTO(BaseModel):
    """DTO for question option representation."""
    id: str
    option_value: str
    label_en: str
    label_tw: Optional[str] = None


class NextQuestionDTO(BaseModel):
    """DTO for the next question to be answered by the patient."""
    id: str
    node_id: str
    question_text_en: str
    question_text_tw: Optional[str] = None
    question_type: str
    options: List[QuestionOptionDTO] = Field(default_factory=list)


class AssessmentSymptomsResponse(BaseModel):
    """Response returned after setting primary symptom."""
    session_id: str
    symptom_slug: str
    next_question: Optional[NextQuestionDTO] = None
    is_emergency: bool = False
    severity: Optional[UrgencyCode] = None


class AssessmentAnswerRequest(BaseModel):
    """Payload to record an answer to a question node."""
    session_id: str
    node_id: str = Field(..., min_length=1, max_length=100)
    answer_value: str = Field(..., min_length=1, max_length=500)
    answer_raw_text: Optional[str] = None


class AssessmentResultResponse(BaseModel):
    """Final assessment result model."""
    session_id: str
    severity: UrgencyCode
    recommendations: List[str]
    explanation: str
    is_emergency: bool
    conducted_at: datetime
    symptom_name: Optional[str] = None
    raw_answers: Optional[Dict[str, str]] = None


class AssessmentAnswerResponse(BaseModel):
    """Response returned after answering a question."""
    session_id: str
    is_completed: bool
    next_question: Optional[NextQuestionDTO] = None
    result: Optional[AssessmentResultResponse] = None


class AssessmentProgressResponse(BaseModel):
    """Response representing current session progress."""
    session_id: str
    status: SessionStatus
    symptom_id: Optional[str] = None
    answers_count: int
    conducted_at: datetime
    created_offline: bool

    model_config = ConfigDict(from_attributes=True)


class AssessmentRestartRequest(BaseModel):
    """Payload to restart an existing assessment session."""
    session_id: str


class AssessmentRestartResponse(BaseModel):
    """Response returned upon restarting an assessment session."""
    new_session_id: str
    status: SessionStatus
    message: str = "Assessment session restarted successfully."
