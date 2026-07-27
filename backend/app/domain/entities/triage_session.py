"""Domain Entities — Triage Session.

A pure Python dataclass representing the state of a triage session
within the domain layer. This entity has ZERO dependency on any
external framework (no SQLAlchemy, no Pydantic, no FastAPI).

See /docs/BackendArchitecture.md for Clean Architecture layer rules.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

from app.domain.value_objects.urgency_level import UrgencyLevel


@dataclass
class TriageResult:
    """Immutable result produced by the rule engine evaluator."""

    urgency: UrgencyLevel
    primary_action_en: str
    primary_action_tw: str
    timeframe_hours: int
    first_aid_protocol_id: Optional[str] = None

    @property
    def is_emergency(self) -> bool:
        """Returns True if the triage result requires immediate emergency response."""
        return self.urgency == UrgencyLevel.RED


@dataclass
class TriageSessionEntity:
    """Core domain entity representing a completed patient triage session.

    Encapsulates all state produced by a single triage evaluation run.
    Created by the rule engine evaluator; persisted by the repository.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    rule_tree_id: Optional[str] = None
    primary_symptom: str = ""
    symptom_details: Dict[str, Any] = field(default_factory=dict)
    language_code: str = "en"
    created_offline: bool = False
    conducted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    synced_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result: Optional[TriageResult] = None
    ai_explanation: Optional[str] = None

    @property
    def urgency_level(self) -> Optional[UrgencyLevel]:
        """Returns the urgency level from the embedded result, if available."""
        return self.result.urgency if self.result else None
