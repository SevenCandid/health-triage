"""Concrete SQLAlchemy 2.0 Repository Implementations.

Implements all abstract repository interfaces from the domain layer
using async SQLAlchemy 2.0 ORM operations.

Each repository accepts an AsyncSession via constructor injection,
making them fully testable with an in-memory test database.

See /docs/BackendArchitecture.md — Section 2.3 Interface Adapters Layer.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.triage_session import TriageSessionEntity
from app.domain.repositories.interfaces import (
    IEmergencyLogRepository,
    IHealthProfileRepository,
    IRuleTreeRepository,
    ITriageSessionRepository,
    IUserRepository,
)
from app.infrastructure.database.models import (
    EmergencyLogModel,
    HealthProfileModel,
    RuleTreeModel,
    TriageSessionModel,
)
from app.models.user import UserModel
from app.models.emergency_contact import EmergencyContactModel

logger = logging.getLogger(__name__)


class SqlAlchemyUserRepository(IUserRepository):
    """Async SQLAlchemy implementation of IUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        phone_number: str,
        email: Optional[str],
        full_name: str,
        password_hash: str,
        preferred_language: str = "en",
    ) -> UserModel:
        """Creates and persists a new user record."""
        user = UserModel(
            id=str(uuid.uuid4()),
            phone_number=phone_number,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            preferred_language_code=preferred_language,
            is_active=True,
            profile_completed=False,
        )
        self._session.add(user)
        await self._session.flush()  # assign DB-generated defaults without committing
        await self._session.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> Optional[UserModel]:
        """Retrieves a user record by its primary UUID."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone_number: str) -> Optional[UserModel]:
        """Retrieves a user record by unique phone number."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Retrieves a user record by unique email address."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> Optional[UserModel]:
        """Retrieves a user record by phone number OR email (supporting flexible formatting)."""
        clean_id = identifier.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # If it looks like a phone number (does not contain '@')
        if "@" not in clean_id:
            suffix = clean_id.lstrip("0")
            if len(suffix) >= 7:
                result = await self._session.execute(
                    select(UserModel).where(
                        or_(
                            UserModel.phone_number == clean_id,
                            UserModel.phone_number == f"+{clean_id}",
                            UserModel.phone_number.like(f"%{suffix}"),
                            UserModel.email == identifier,
                        )
                    )
                )
                user = result.scalar_one_or_none()
                if user:
                    return user

        result = await self._session.execute(
            select(UserModel).where(
                or_(
                    UserModel.phone_number == identifier,
                    UserModel.email == identifier,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_language(self, user_id: str, language_code: str) -> Optional[UserModel]:
        """Updates the user's preferred language code."""
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                preferred_language_code=language_code,
            )
        )
        return await self.get_by_id(user_id)

    async def delete(self, user_id: str) -> bool:
        """Hard-deletes a user and all cascading records."""
        result = await self._session.execute(
            delete(UserModel).where(UserModel.id == user_id)
        )
        return result.rowcount > 0


class SqlAlchemyHealthProfileRepository(IHealthProfileRepository):
    """Async SQLAlchemy implementation of IHealthProfileRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> Optional[HealthProfileModel]:
        """Retrieves the health profile associated with a given user."""
        result = await self._session.execute(
            select(HealthProfileModel).where(HealthProfileModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: str, profile_data: Dict[str, Any]) -> HealthProfileModel:
        """Creates or updates a health profile for the given user ID.

        Also marks profile_completed=True on the UserModel so that the JWT
        claim and frontend route guards reflect the change immediately.
        """
        existing = await self.get_by_user_id(user_id)
        if existing:
            for key, value in profile_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            await self._session.flush()
            await self._session.refresh(existing)
        else:
            profile = HealthProfileModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                **profile_data,
            )
            self._session.add(profile)
            await self._session.flush()
            await self._session.refresh(profile)
            existing = profile

        # Mark the user's profile as completed
        user_result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if user and not user.profile_completed:
            user.profile_completed = True
            await self._session.flush()

        return existing

    async def get_emergency_contacts(self, user_id: str) -> List[EmergencyContactModel]:
        """Returns the list of emergency contacts for a given user."""
        result = await self._session.execute(
            select(EmergencyContactModel).where(
                EmergencyContactModel.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def upsert_emergency_contact(
        self, user_id: str, contact_data: Dict[str, Any]
    ) -> EmergencyContactModel:
        """Creates or replaces an emergency contact for a user."""
        contact_id = contact_data.get("id")
        existing = None
        if contact_id:
            result = await self._session.execute(
                select(EmergencyContactModel).where(
                    EmergencyContactModel.id == contact_id,
                    EmergencyContactModel.user_id == user_id,
                )
            )
            existing = result.scalar_one_or_none()

        if existing:
            for key, value in contact_data.items():
                if hasattr(existing, key) and key != "id":
                    setattr(existing, key, value)
            await self._session.flush()
            await self._session.refresh(existing)
            return existing

        contact = EmergencyContactModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            contact_name=contact_data["contact_name"],
            phone_number=contact_data["phone_number"],
            relationship_type=contact_data.get("relationship_type", "Other"),
            is_primary=contact_data.get("is_primary", False),
        )
        self._session.add(contact)
        await self._session.flush()
        await self._session.refresh(contact)
        return contact

    async def delete_emergency_contact(self, contact_id: str, user_id: str) -> bool:
        """Removes an emergency contact by ID, scoped to the owning user."""
        result = await self._session.execute(
            delete(EmergencyContactModel).where(
                EmergencyContactModel.id == contact_id,
                EmergencyContactModel.user_id == user_id,
            )
        )
        return result.rowcount > 0


class SqlAlchemyTriageSessionRepository(ITriageSessionRepository):
    """Async SQLAlchemy implementation of ITriageSessionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, session_entity: TriageSessionEntity) -> TriageSessionModel:
        """Persists a completed triage session entity to the database."""
        model = TriageSessionModel(
            id=session_entity.id,
            user_id=session_entity.user_id,
            rule_tree_id=session_entity.rule_tree_id,
            urgency_level=session_entity.urgency_level.value if session_entity.urgency_level else "GREEN",
            primary_symptom=session_entity.primary_symptom,
            symptom_details=session_entity.symptom_details,
            ai_explanation=session_entity.ai_explanation,
            language_code=session_entity.language_code,
            created_offline=session_entity.created_offline,
            conducted_at=session_entity.conducted_at,
            synced_at=session_entity.synced_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def get_by_id(self, session_id: str) -> Optional[TriageSessionModel]:
        """Retrieves a single triage session by its UUID."""
        result = await self._session.execute(
            select(TriageSessionModel).where(TriageSessionModel.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[TriageSessionModel]:
        """Retrieves a paginated list of triage sessions for a given user."""
        result = await self._session.execute(
            select(TriageSessionModel)
            .where(TriageSessionModel.user_id == user_id)
            .order_by(TriageSessionModel.conducted_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def bulk_upsert(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Bulk-upserts offline outbox sessions by idempotent UUID key."""
        saved_ids: List[str] = []
        for session_data in sessions:
            session_id = session_data.get("id", str(uuid.uuid4()))
            existing_result = await self._session.execute(
                select(TriageSessionModel).where(TriageSessionModel.id == session_id)
            )
            existing = existing_result.scalar_one_or_none()
            if not existing:
                model = TriageSessionModel(
                    id=session_id,
                    user_id=session_data.get("user_id"),
                    urgency_level=session_data.get("urgency_level", "GREEN"),
                    primary_symptom=session_data.get("primary_symptom", "unknown"),
                    symptom_details=session_data.get("symptom_details", {}),
                    language_code=session_data.get("language_code", "en"),
                    created_offline=True,
                    conducted_at=datetime.fromisoformat(
                        session_data.get("conducted_at", datetime.now(timezone.utc).isoformat())
                    ),
                    synced_at=datetime.now(timezone.utc),
                )
                self._session.add(model)
                saved_ids.append(session_id)
        await self._session.flush()
        return saved_ids


class SqlAlchemyRuleTreeRepository(IRuleTreeRepository):
    """Async SQLAlchemy implementation of IRuleTreeRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self) -> Optional[RuleTreeModel]:
        """Retrieves the currently active versioned rule tree."""
        result = await self._session.execute(
            select(RuleTreeModel)
            .where(RuleTreeModel.is_active == True)  # noqa: E712
            .order_by(RuleTreeModel.published_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_version(self, version: str) -> Optional[RuleTreeModel]:
        """Retrieves a specific versioned rule tree by version string."""
        result = await self._session.execute(
            select(RuleTreeModel).where(RuleTreeModel.version == version)
        )
        return result.scalar_one_or_none()


class SqlAlchemyEmergencyLogRepository(IEmergencyLogRepository):
    """Async SQLAlchemy implementation of IEmergencyLogRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, session_id: str, latitude: float, longitude: float
    ) -> EmergencyLogModel:
        """Creates an emergency log entry linked to a triage session."""
        log = EmergencyLogModel(
            id=str(uuid.uuid4()),
            triage_session_id=session_id,
            latitude=latitude,
            longitude=longitude,
            status="DISPATCHED",
        )
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log

    async def get_by_session_id(self, session_id: str) -> Optional[EmergencyLogModel]:
        """Retrieves an emergency log by its associated triage session ID."""
        result = await self._session.execute(
            select(EmergencyLogModel).where(
                EmergencyLogModel.triage_session_id == session_id
            )
        )
        return result.scalar_one_or_none()
