"""RecommendationTranslation Pydantic v2 Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RecommendationTranslationCreate(BaseModel):
    recommendation_id: str
    language_code: str = Field(..., min_length=2, max_length=10)
    content: str = Field(..., min_length=1)
    voice_content: Optional[str] = None


class RecommendationTranslationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recommendation_id: str
    language_code: str
    content: str
    voice_content: Optional[str]
