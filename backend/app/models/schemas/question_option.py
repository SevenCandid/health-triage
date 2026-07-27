"""QuestionOption Pydantic v2 Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class QuestionOptionCreate(BaseModel):
    question_id: str
    option_value: str = Field(..., min_length=1, max_length=100)
    label_en: str = Field(..., min_length=1, max_length=200)
    label_tw: Optional[str] = Field(None, max_length=200)
    next_node_id: Optional[str] = Field(None, max_length=100)
    terminal_severity_level_id: Optional[str] = None
    is_terminal: bool = False
    is_red_flag: bool = False
    order_index: int = Field(default=0, ge=0)


class QuestionOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_id: str
    option_value: str
    label_en: str
    label_tw: Optional[str]
    next_node_id: Optional[str]
    terminal_severity_level_id: Optional[str]
    is_terminal: bool
    is_red_flag: bool
    order_index: int
