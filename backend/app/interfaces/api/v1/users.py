"""User Profile API Router."""

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from app.interfaces.api.dependencies import (
    get_current_user_id,
    get_profile_service,
)
from app.interfaces.schemas.profile import (
    EmergencyContactRequest,
    EmergencyContactResponse,
    HealthProfileRequest,
    HealthProfileResponse,
)
from app.use_cases.profile_service import ProfileService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["User Profile"])

CurrentUser = Annotated[str, Depends(get_current_user_id)]


@router.get(
    "/me/profile",
    response_model=HealthProfileResponse,
    summary="Get current user health profile",
)
async def get_my_profile(
    user_id: CurrentUser,
    service: ProfileService = Depends(get_profile_service),
) -> HealthProfileResponse:
    """Returns the health profile for the currently authenticated user."""
    profile = await service.get_profile(user_id)
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health profile not found. Please create one first.")
    contacts = await service.get_emergency_contacts(user_id)
    response = HealthProfileResponse.model_validate(profile)
    response.emergency_contacts = [
        EmergencyContactResponse.model_validate(c) for c in contacts
    ]
    return response


@router.put(
    "/me/profile",
    response_model=HealthProfileResponse,
    summary="Create or update current user health profile",
)
async def upsert_my_profile(
    payload: HealthProfileRequest,
    user_id: CurrentUser,
    service: ProfileService = Depends(get_profile_service),
) -> HealthProfileResponse:
    """Creates or updates the health profile for the currently authenticated user."""
    profile = await service.upsert_profile(
        user_id=user_id,
        profile_data=payload.model_dump(exclude_none=True),
    )
    contacts = await service.get_emergency_contacts(user_id)
    response = HealthProfileResponse.model_validate(profile)
    response.emergency_contacts = [
        EmergencyContactResponse.model_validate(c) for c in contacts
    ]
    return response


@router.get(
    "/me/emergency-contacts",
    response_model=List[EmergencyContactResponse],
    summary="Get emergency contacts",
)
async def get_emergency_contacts(
    user_id: CurrentUser,
    service: ProfileService = Depends(get_profile_service),
) -> List[EmergencyContactResponse]:
    """Returns all emergency contacts registered for the authenticated user."""
    contacts = await service.get_emergency_contacts(user_id)
    return [EmergencyContactResponse.model_validate(c) for c in contacts]


@router.post(
    "/me/emergency-contacts",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add or update an emergency contact",
)
async def upsert_emergency_contact(
    payload: EmergencyContactRequest,
    user_id: CurrentUser,
    service: ProfileService = Depends(get_profile_service),
) -> EmergencyContactResponse:
    """Creates or updates an emergency contact for the authenticated user."""
    contact = await service.upsert_emergency_contact(
        user_id=user_id,
        contact_data=payload.model_dump(),
    )
    return EmergencyContactResponse.model_validate(contact)
