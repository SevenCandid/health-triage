"""Emergency Contact Pydantic v2 Schemas."""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.emergency_contact import RelationshipType


class EmergencyContactCreate(BaseModel):
    contact_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=7, max_length=20)
    relationship_type: RelationshipType = RelationshipType.OTHER
    is_primary: bool = False
    notes: Optional[str] = Field(None, max_length=255)

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+[1-9]\d{6,19}$", v):
            raise ValueError("Phone must be E.164 format.")
        return v


class EmergencyContactUpdate(BaseModel):
    contact_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    relationship_type: Optional[RelationshipType] = None
    is_primary: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=255)


class EmergencyContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    contact_name: str
    phone_number: str
    relationship_type: RelationshipType
    is_primary: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
