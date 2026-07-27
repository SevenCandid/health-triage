"""Symptom Pydantic v2 Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.symptom import SymptomSeverityHint
from app.models.schemas.symptom_translation import SymptomTranslationRead


class SymptomCreate(BaseModel):
    category_id: str
    slug: str = Field(..., min_length=1, max_length=80, pattern=r"^[a-z0-9-]+$")
    name_en: str = Field(..., min_length=1, max_length=150)
    description_en: Optional[str] = Field(None, max_length=500)
    severity_hint: SymptomSeverityHint = SymptomSeverityHint.MODERATE
    is_red_flag: bool = False
    icd10_code: Optional[str] = Field(None, max_length=10)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class SymptomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category_id: str
    slug: str
    name_en: str
    description_en: Optional[str]
    severity_hint: SymptomSeverityHint
    is_red_flag: bool
    icd10_code: Optional[str]
    display_order: int
    is_active: bool
    created_at: datetime


class SymptomWithTranslations(SymptomRead):
    """Symptom with all language translations embedded."""
    translations: List[SymptomTranslationRead] = []
