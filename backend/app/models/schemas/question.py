"""Question Pydantic v2 Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.question import QuestionType


class QuestionCreate(BaseModel):
    symptom_id: str
    node_id: str = Field(..., min_length=1, max_length=100)
    question_text_en: str = Field(..., min_length=1)
    question_text_tw: Optional[str] = None
    voice_prompt_en: Optional[str] = None
    voice_prompt_tw: Optional[str] = None
    question_type: QuestionType = QuestionType.SINGLE_SELECT
    is_red_flag_trigger: bool = False
    is_required: bool = True
    order_index: int = Field(default=0, ge=0)
    help_text_en: Optional[str] = Field(None, max_length=500)


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    symptom_id: str
    node_id: str
    question_text_en: str
    question_text_tw: Optional[str]
    question_type: QuestionType
    is_red_flag_trigger: bool
    is_required: bool
    order_index: int
    help_text_en: Optional[str]
