"""Recommendation Pydantic v2 Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.recommendation import RecommendationType


class RecommendationCreate(BaseModel):
    health_concern_id: str
    recommendation_type: RecommendationType
    content_en: str = Field(..., min_length=1)
    step_order: int = Field(default=0, ge=0)
    is_active: bool = True
    source_reference: Optional[str] = Field(None, max_length=255)


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    health_concern_id: str
    recommendation_type: RecommendationType
    content_en: str
    step_order: int
    is_active: bool
    source_reference: Optional[str]
