"""User Domain Pydantic v2 Schemas."""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.user import BiologicalSex, BloodGroup, UserRole


class UserCreate(BaseModel):
    phone_number: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=8, max_length=72)
    preferred_language_code: str = Field(default="en", max_length=10)
    full_name: Optional[str] = Field(None, max_length=120)
    age: Optional[int] = Field(None, ge=0, le=120)
    biological_sex: Optional[BiologicalSex] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+[1-9]\d{6,19}$", v):
            raise ValueError("Phone number must be in E.164 format.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=120)
    age: Optional[int] = Field(None, ge=0, le=120)
    biological_sex: Optional[BiologicalSex] = None
    blood_group: Optional[BloodGroup] = None
    preferred_language_code: Optional[str] = Field(None, max_length=10)


class UserPublic(BaseModel):
    """Minimal user representation safe to return in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    phone_number: str
    role: UserRole
    is_active: bool
    preferred_language_code: str
    created_at: datetime


class UserRead(UserPublic):
    """Full user representation for authenticated user's own profile."""
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str]
    age: Optional[int]
    biological_sex: Optional[BiologicalSex]
    blood_group: Optional[BloodGroup]
    updated_at: datetime
