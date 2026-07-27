"""Language Pydantic v2 Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict


class LanguageCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=10, pattern=r"^[a-z]{2,3}(-[A-Z]{2})?$")
    name_en: str = Field(..., min_length=1, max_length=60)
    name_native: str = Field(..., min_length=1, max_length=60)
    is_active: bool = True
    supports_voice: bool = False


class LanguageUpdate(BaseModel):
    name_en: Optional[str] = Field(None, min_length=1, max_length=60)
    name_native: Optional[str] = Field(None, min_length=1, max_length=60)
    is_active: Optional[bool] = None
    supports_voice: Optional[bool] = None


class LanguageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name_en: str
    name_native: str
    is_active: bool
    supports_voice: bool
    created_at: datetime
    updated_at: datetime
