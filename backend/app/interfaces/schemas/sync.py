"""Offline Outbox Sync Pydantic v2 Schemas.

See /docs/APIReference.md — Section 3.2 POST /api/v1/sync/outbox
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OutboxSessionItem(BaseModel):
    """Individual offline triage session item from the client outbox queue."""

    local_id: str = Field(..., description="Client-side UUID for idempotency.")
    urgency_level: str = Field(..., pattern="^(RED|ORANGE|YELLOW|GREEN)$")
    primary_symptom: str = Field(..., min_length=1, max_length=100)
    symptom_details: Dict[str, Any] = Field(default_factory=dict)
    language_code: str = Field(default="en", pattern="^(en|tw)$")
    conducted_at: datetime


class OutboxSyncRequest(BaseModel):
    """Batch outbox sync request payload from client Service Worker."""

    batch_id: str = Field(..., description="Unique ID for this sync batch operation.")
    sessions: List[OutboxSessionItem] = Field(..., min_length=1)


class SyncedIdPair(BaseModel):
    """Maps a client local_id to the newly assigned server_id."""

    local_id: str
    server_id: str


class OutboxSyncResponse(BaseModel):
    """Batch outbox sync response payload."""

    processed_count: int
    synced_ids: List[SyncedIdPair]
    errors: List[str] = Field(default_factory=list)
