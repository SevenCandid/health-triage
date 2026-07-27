"""Sync Service — Use Case Layer.

Handles bulk ingestion of offline outbox queue items from the
client-side Service Worker background sync.

See /docs/OfflineStrategy.md — Section 3 (Outbox Pattern).
"""

import logging
from typing import Any, Dict, List, Optional

from app.domain.repositories.interfaces import ITriageSessionRepository

logger = logging.getLogger(__name__)


class SyncService:
    """Processes and persists offline triage session outbox batches."""

    def __init__(self, triage_repo: ITriageSessionRepository) -> None:
        self._triage_repo = triage_repo

    async def process_outbox(
        self,
        batch_id: str,
        sessions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Idempotently ingests a batch of offline triage session records.

        Args:
            batch_id: Unique sync batch identifier for logging.
            sessions: List of serialized offline session dicts.
            user_id: Authenticated user to associate records with.

        Returns:
            Dict containing processed_count, synced_ids, and errors list.
        """
        logger.info(
            f"Processing outbox sync batch: batch_id={batch_id} "
            f"count={len(sessions)} user_id={user_id}"
        )
        errors: List[str] = []
        sessions_with_user: List[Dict[str, Any]] = []
        local_id_map: Dict[str, str] = {}

        for item in sessions:
            enriched = dict(item)
            enriched["id"] = item["local_id"]
            if user_id:
                enriched["user_id"] = user_id
            sessions_with_user.append(enriched)
            local_id_map[item["local_id"]] = item["local_id"]

        try:
            saved_ids = await self._triage_repo.bulk_upsert(sessions_with_user)
            synced_pairs = [
                {"local_id": sid, "server_id": sid} for sid in saved_ids
            ]
        except Exception as exc:
            logger.error(f"Outbox sync batch failed: {exc}")
            errors.append(str(exc))
            synced_pairs = []

        return {
            "processed_count": len(synced_pairs),
            "synced_ids": synced_pairs,
            "errors": errors,
        }
