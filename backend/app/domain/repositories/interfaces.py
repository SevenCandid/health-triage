"""Domain Repository Interfaces (Abstract Base Classes).

Defines the port contracts that concrete SQLAlchemy repositories must implement.
The domain layer only knows about these interfaces — never the ORM implementation.

This enforces Clean Architecture's Dependency Inversion Principle:
  High-level use cases depend on abstractions, not on concrete infrastructure.

See /docs/BackendArchitecture.md — Section 2.1 Domain Layer.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.domain.entities.triage_session import TriageSessionEntity


# ---------------------------------------------------------------------------
# User Repository Interface
# ---------------------------------------------------------------------------
class IUserRepository(ABC):
    """Contract for user account persistence operations."""

    @abstractmethod
    async def create(self, phone_number: str, email: Optional[str], full_name: str, password_hash: str, preferred_language: str = "en") -> Any:
        """Creates and persists a new user record."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[Any]:
        """Retrieves a user record by its primary UUID."""
        ...

    @abstractmethod
    async def get_by_phone(self, phone_number: str) -> Optional[Any]:
        """Retrieves a user record by unique phone number."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Any]:
        """Retrieves a user record by unique email address."""
        ...

    @abstractmethod
    async def get_by_identifier(self, identifier: str) -> Optional[Any]:
        """Retrieves a user record by phone number OR email."""
        ...

    @abstractmethod
    async def update_language(self, user_id: str, language_code: str) -> Optional[Any]:
        """Updates the user's preferred language code."""
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Hard-deletes a user and all cascading records (GDPR right to erasure)."""
        ...


# ---------------------------------------------------------------------------
# Health Profile Repository Interface
# ---------------------------------------------------------------------------
class IHealthProfileRepository(ABC):
    """Contract for user health profile persistence operations."""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Any]:
        """Retrieves the health profile associated with a given user."""
        ...

    @abstractmethod
    async def upsert(self, user_id: str, profile_data: Dict[str, Any]) -> Any:
        """Creates or updates a health profile for the given user ID."""
        ...

    @abstractmethod
    async def get_emergency_contacts(self, user_id: str) -> List[Any]:
        """Returns the list of emergency contacts for a given user."""
        ...

    @abstractmethod
    async def upsert_emergency_contact(self, user_id: str, contact_data: Dict[str, Any]) -> Any:
        """Creates or replaces an emergency contact for a user."""
        ...

    @abstractmethod
    async def delete_emergency_contact(self, contact_id: str, user_id: str) -> bool:
        """Removes an emergency contact by ID, scoped to the owning user."""
        ...


# ---------------------------------------------------------------------------
# Triage Session Repository Interface
# ---------------------------------------------------------------------------
class ITriageSessionRepository(ABC):
    """Contract for triage session persistence and retrieval."""

    @abstractmethod
    async def save(self, session_entity: TriageSessionEntity) -> Any:
        """Persists a completed triage session entity to the database."""
        ...

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[Any]:
        """Retrieves a single triage session by its UUID."""
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Any]:
        """Retrieves a paginated list of triage sessions for a given user."""
        ...

    @abstractmethod
    async def bulk_upsert(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Bulk-upserts offline outbox sessions by idempotent UUID key."""
        ...


# ---------------------------------------------------------------------------
# Rule Tree Repository Interface
# ---------------------------------------------------------------------------
class IRuleTreeRepository(ABC):
    """Contract for clinical decision tree retrieval and version management."""

    @abstractmethod
    async def get_active(self) -> Optional[Any]:
        """Retrieves the currently active (latest) versioned rule tree."""
        ...

    @abstractmethod
    async def get_by_version(self, version: str) -> Optional[Any]:
        """Retrieves a specific versioned rule tree by version string."""
        ...


# ---------------------------------------------------------------------------
# Emergency Log Repository Interface
# ---------------------------------------------------------------------------
class IEmergencyLogRepository(ABC):
    """Contract for emergency dispatch log persistence."""

    @abstractmethod
    async def create(self, session_id: str, latitude: float, longitude: float) -> Any:
        """Creates an emergency log entry linked to a triage session."""
        ...

    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> Optional[Any]:
        """Retrieves an emergency log by its associated triage session ID."""
        ...
