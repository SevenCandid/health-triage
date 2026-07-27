"""Offline Outbox Sync API Router."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status

from app.interfaces.api.dependencies import (
    get_optional_user_id,
    get_sync_service,
)
from app.interfaces.schemas.sync import OutboxSyncRequest, OutboxSyncResponse, SyncedIdPair
from app.use_cases.sync_service import SyncService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post(
    "/outbox",
    response_model=OutboxSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk sync offline outbox sessions",
    description=(
        "Idempotently ingests a batch of offline triage session records from the "
        "client-side IndexedDB outbox queue. Deduplicates by session UUID. "
        "See /docs/OfflineStrategy.md — Section 3 (Outbox Pattern)."
    ),
)
async def sync_outbox(
    payload: OutboxSyncRequest,
    service: SyncService = Depends(get_sync_service),
    user_id: Optional[str] = Depends(get_optional_user_id),
) -> OutboxSyncResponse:
    """Processes offline outbox sync batch."""
    sessions_as_dicts = [
        s.model_dump() for s in payload.sessions
    ]
    result = await service.process_outbox(
        batch_id=payload.batch_id,
        sessions=sessions_as_dicts,
        user_id=user_id,
    )
    return OutboxSyncResponse(
        processed_count=result["processed_count"],
        synced_ids=[SyncedIdPair(**p) for p in result["synced_ids"]],
        errors=result["errors"],
    )
