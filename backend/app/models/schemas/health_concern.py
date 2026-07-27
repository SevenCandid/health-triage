"""HealthConcern Pydantic v2 Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HealthConcernCreate(BaseModel):
    severity_level_id: str
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    name_en: str = Field(..., min_length=1, max_length=200)
    name_tw: Optional[str] = Field(None, max_length=200)
    description_en: Optional[str] = Field(None, max_length=1000)
    requires_emergency_dispatch: bool = False
    icd10_code: Optional[str] = Field(None, max_length=10)


class HealthConcernRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    severity_level_id: str
    slug: str
    name_en: str
    name_tw: Optional[str]
    description_en: Optional[str]
    requires_emergency_dispatch: bool
    icd10_code: Optional[str]
