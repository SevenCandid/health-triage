"""SeverityLevel Pydantic v2 Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.severity_level import UrgencyCode


class SeverityLevelCreate(BaseModel):
    code: UrgencyCode
    label_en: str = Field(..., min_length=1, max_length=60)
    label_tw: Optional[str] = Field(None, max_length=60)
    description_en: Optional[str] = Field(None, max_length=500)
    badge_color_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    timeframe_minutes: int = Field(..., ge=0)
    requires_emergency_dispatch: bool = False
    display_order: int = Field(default=0, ge=0)


class SeverityLevelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: UrgencyCode
    label_en: str
    label_tw: Optional[str]
    description_en: Optional[str]
    badge_color_hex: str
    timeframe_minutes: int
    requires_emergency_dispatch: bool
    display_order: int
