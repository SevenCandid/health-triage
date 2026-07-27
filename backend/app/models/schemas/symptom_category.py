"""Symptom Category Pydantic v2 Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.symptom_category import BodySystem


class SymptomCategoryCreate(BaseModel):
    name_en: str = Field(..., min_length=1, max_length=100)
    name_tw: Optional[str] = Field(None, max_length=100)
    slug: str = Field(..., min_length=1, max_length=80, pattern=r"^[a-z0-9-]+$")
    body_system: BodySystem
    icon_name: Optional[str] = Field(None, max_length=60)
    display_order: int = Field(default=0, ge=0)
    is_emergency_fast_track: bool = False


class SymptomCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name_en: str
    name_tw: Optional[str]
    slug: str
    body_system: BodySystem
    icon_name: Optional[str]
    display_order: int
    is_emergency_fast_track: bool
    created_at: datetime
