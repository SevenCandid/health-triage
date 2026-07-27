"""AuditLog Pydantic v2 Schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.audit_log import AuditAction


class AuditLogCreate(BaseModel):
    user_id: Optional[str] = None
    action: AuditAction
    resource_type: Optional[str] = Field(None, max_length=60)
    resource_id: Optional[str] = Field(None, max_length=36)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    metadata_json: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str]
    action: AuditAction
    resource_type: Optional[str]
    resource_id: Optional[str]
    occurred_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata_json: Optional[Dict[str, Any]]
    outcome: Optional[str]
    notes: Optional[str]
