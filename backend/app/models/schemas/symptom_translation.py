"""Symptom Translation Pydantic v2 Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SymptomTranslationCreate(BaseModel):
    symptom_id: str
    language_code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    voice_prompt: Optional[str] = Field(None, max_length=300)


class SymptomTranslationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    symptom_id: str
    language_code: str
    name: str
    description: Optional[str]
    voice_prompt: Optional[str]
