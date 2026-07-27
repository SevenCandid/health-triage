"""AssessmentResponse Pydantic v2 Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AssessmentResponseCreate(BaseModel):
    session_id: str
    question_id: Optional[str] = None
    selected_option_id: Optional[str] = None
    node_id: str = Field(..., max_length=100)
    answer_value: str = Field(..., max_length=500)
    answer_raw_text: Optional[str] = None
    triggered_red_flag: bool = False
    answered_at: datetime = Field(default_factory=datetime.utcnow)


class AssessmentResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    question_id: Optional[str]
    selected_option_id: Optional[str]
    node_id: str
    answer_value: str
    answer_raw_text: Optional[str]
    triggered_red_flag: bool
    answered_at: datetime
