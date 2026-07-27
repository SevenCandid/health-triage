"""User Health Profile Pydantic v2 Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class EmergencyContactRequest(BaseModel):
    """Emergency contact create/update request."""

    id: Optional[str] = None
    contact_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=7, max_length=20)
    relationship_type: str = Field(default="Other", max_length=50)
    is_primary: bool = False


class EmergencyContactResponse(BaseModel):
    """Emergency contact read response."""

    id: str
    contact_name: str
    phone_number: str
    relationship_type: str
    is_primary: bool

    model_config = {"from_attributes": True}


class HealthProfileRequest(BaseModel):
    """Health profile create/update request payload."""

    full_name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=120)
    biological_sex: str = Field(..., pattern="^(MALE|FEMALE|OTHER)$")
    blood_group: Optional[str] = Field(
        default=None,
        pattern="^(A|B|AB|O)[+-]$",
        description="ABO blood group with Rh factor (e.g. A+, O-).",
    )
    chronic_conditions: List[str] = Field(default_factory=list)
    known_allergies: List[str] = Field(default_factory=list)


class HealthProfileResponse(BaseModel):
    """Health profile read response payload."""

    id: str
    user_id: str
    full_name: str
    age: int
    biological_sex: str
    blood_group: Optional[str]
    chronic_conditions: List[str]
    known_allergies: List[str]
    updated_at: datetime
    emergency_contacts: List[EmergencyContactResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
