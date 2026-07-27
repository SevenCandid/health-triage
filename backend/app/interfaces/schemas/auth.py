"""Authentication Pydantic v2 Schemas.

Request/response DTOs for user registration and login flows.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    """User registration request payload."""

    full_name: str = Field(..., min_length=2, max_length=120)
    phone_number: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="Phone number in E.164 format (e.g. +233241234567)",
        examples=["+233241234567"],
    )
    email: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=8, max_length=72)
    preferred_language: str = Field(default="en", pattern="^(en|tw)$")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validates phone number conforms to E.164 format."""
        if not re.match(r"^\+[1-9]\d{6,19}$", v):
            raise ValueError("Phone number must be in E.164 format (e.g. +233241234567)")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Enforces minimum password complexity rules."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class LoginRequest(BaseModel):
    """User login request payload."""

    identifier: str = Field(..., min_length=5, max_length=255, description="Email or phone number")
    password: str = Field(..., min_length=8, max_length=72)


class TokenResponse(BaseModel):
    """JWT access token response payload."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: "UserResponse"

class RefreshTokenRequest(BaseModel):
    """Token refresh request payload."""

    refresh_token: str


class UserResponse(BaseModel):
    """Authenticated user public representation."""

    id: str
    full_name: str
    phone_number: str
    email: Optional[str]
    preferred_language_code: str
    is_active: bool
    profile_completed: bool

    model_config = {"from_attributes": True}
