"""Emergency Service — Use Case Layer."""

import logging
import uuid
from typing import Any, Optional

from app.domain.repositories.interfaces import IEmergencyLogRepository

logger = logging.getLogger(__name__)


class EmergencyService:
    """Handles emergency alert dispatch and GPS log persistence."""

    def __init__(self, emergency_repo: IEmergencyLogRepository) -> None:
        self._emergency_repo = emergency_repo

    async def dispatch(
        self,
        triage_session_id: str,
        latitude: float,
        longitude: float,
        primary_symptom: str,
    ) -> Any:
        """Persists an emergency dispatch log and builds the SMS payload.

        Args:
            triage_session_id: UUID of the triggering triage session.
            latitude: Patient GPS latitude coordinate.
            longitude: Patient GPS longitude coordinate.
            primary_symptom: The chief presenting complaint for SMS context.

        Returns:
            Created EmergencyLogModel instance with pre-formatted sms_payload string.

        TODO (Phase 2 — EmergencySystem.md):
            - Integrate push notification dispatch to emergency contacts.
            - Connect to regional hospital directory API for nearest facility lookup.
        """
        log = await self._emergency_repo.create(
            session_id=triage_session_id,
            latitude=latitude,
            longitude=longitude,
        )

        # Build the offline-compatible SMS payload string
        maps_url = f"https://maps.google.com/?q={latitude},{longitude}"
        sms_payload = (
            f"EMERGENCY HEALTH ALERT! "
            f"Symptom: {primary_symptom.upper()}. "
            f"GPS Location: {maps_url}. "
            f"Please assist immediately. Sent via FirstAid+."
        )
        logger.warning(
            f"Emergency dispatched: log_id={log.id} "
            f"session_id={triage_session_id} "
            f"lat={latitude} lon={longitude}"
        )
        # Attach sms_payload as a transient attribute for the response
        log.sms_payload = sms_payload  # type: ignore[attr-defined]
        return log
