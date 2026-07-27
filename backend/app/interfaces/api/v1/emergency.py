"""Emergency Dispatch API Router."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.interfaces.api.dependencies import (
    get_current_user_id,
    get_emergency_service,
)
from app.interfaces.schemas.emergency import (
    EmergencyDispatchRequest,
    EmergencyDispatchResponse,
)
from app.use_cases.emergency_service import EmergencyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/emergency", tags=["Emergency"])

CurrentUser = Annotated[str, Depends(get_current_user_id)]


@router.post(
    "/dispatch",
    response_model=EmergencyDispatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dispatch emergency alert with GPS coordinates",
    description=(
        "Logs an emergency dispatch event with GPS location linked to a triage session. "
        "Returns a pre-formatted SMS payload string for the client to send. "
        "See /docs/EmergencySystem.md for full protocol specification."
    ),
)
async def dispatch_emergency(
    payload: EmergencyDispatchRequest,
    user_id: CurrentUser,
    service: EmergencyService = Depends(get_emergency_service),
) -> EmergencyDispatchResponse:
    """Creates an emergency log and returns an SMS payload for dispatch."""
    log = await service.dispatch(
        triage_session_id=payload.triage_session_id,
        latitude=payload.location.latitude,
        longitude=payload.location.longitude,
        primary_symptom=payload.primary_symptom,
    )
    return EmergencyDispatchResponse(
        log_id=log.id,
        triage_session_id=log.triage_session_id,
        status=log.status,
        triggered_at=log.triggered_at,
        sms_payload=getattr(log, "sms_payload", None),
    )
