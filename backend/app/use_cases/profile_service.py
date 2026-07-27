"""Profile Service — Use Case Layer."""

import logging
from typing import Any, Dict, List, Optional

from app.domain.repositories.interfaces import IHealthProfileRepository

logger = logging.getLogger(__name__)


class ProfileService:
    """Manages user health profile and emergency contact CRUD operations."""

    def __init__(self, profile_repo: IHealthProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def get_profile(self, user_id: str) -> Optional[Any]:
        """Retrieves health profile with emergency contacts for a given user."""
        return await self._profile_repo.get_by_user_id(user_id)

    async def upsert_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Any:
        """Creates or updates a user health profile.

        TODO (Phase 2): Validate chronic conditions against a curated
        medical terminology dictionary to prevent free-text injection.
        """
        logger.info(f"Upserting health profile for user_id={user_id}")
        return await self._profile_repo.upsert(user_id=user_id, profile_data=profile_data)

    async def get_emergency_contacts(self, user_id: str) -> List[Any]:
        """Returns all emergency contacts registered for a user."""
        return await self._profile_repo.get_emergency_contacts(user_id)

    async def upsert_emergency_contact(
        self, user_id: str, contact_data: Dict[str, Any]
    ) -> Any:
        """Creates or updates an emergency contact record."""
        return await self._profile_repo.upsert_emergency_contact(user_id, contact_data)

    async def delete_emergency_contact(self, contact_id: str, user_id: str) -> bool:
        """Removes an emergency contact from a user's record."""
        return await self._profile_repo.delete_emergency_contact(contact_id, user_id)
