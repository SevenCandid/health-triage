"""Assessment Session Model.

Records a single complete triage assessment session conducted by a user.
Links the user, primary symptom, identified health concern, and resulting
severity level. Stores offline metadata for sync reconciliation.

Replaces the legacy TriageSessionModel — this is the canonical domain model.
See /docs/DatabaseDesign.md and /docs/OfflineStrategy.md.
"""

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, Text, text, JSON
# Removed JSONB from dialects.postgresql import
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.symptom import SymptomModel
    from app.models.severity_level import SeverityLevelModel
    from app.models.health_concern import HealthConcernModel
    from app.models.assessment_response import AssessmentResponseModel


class SessionStatus(str, enum.Enum):
    """Lifecycle status of an assessment session."""

    IN_PROGRESS = "IN_PROGRESS"    # Legacy status for active sessions
    ACTIVE = "ACTIVE"              # Questions still being answered / Active conversation
    COMPLETED = "COMPLETED"        # Full evaluation completed
    ARCHIVED = "ARCHIVED"          # User closed before completion or manually archived
    SYNCED = "SYNCED"              # Offline session synced to server


class ConsultationMode(str, enum.Enum):
    """How the user interacted with the triage flow."""

    TEXT = "TEXT"
    VOICE = "VOICE"
    HYBRID = "HYBRID"


class AssessmentSessionModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Complete record of one triage assessment session."""

    __tablename__ = "assessment_sessions"
    __table_args__ = {
        "comment": (
            "Canonical triage assessment session records. "
            "Supports offline-first creation with deferred sync."
        )
    }

    # ---- Foreign Keys ---------------------------------------------------
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE", name="fk_assessment_sessions_user_id"),
        nullable=True,
        index=True,
        comment="Authenticated user UUID. NULL for anonymous triage sessions.",
    )
    symptom_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("symptoms.id", ondelete="SET NULL", name="fk_assessment_sessions_symptom_id"),
        nullable=True,
        index=True,
        comment="Primary symptom selected as the decision tree entry point.",
    )
    identified_concern_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey(
            "health_concerns.id",
            ondelete="SET NULL",
            name="fk_assessment_sessions_concern_id",
        ),
        nullable=True,
        index=True,
        comment="HealthConcern identified by the rule engine. NULL if evaluation incomplete.",
    )
    severity_level_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey(
            "severity_levels.id",
            ondelete="SET NULL",
            name="fk_assessment_sessions_severity_id",
        ),
        nullable=True,
        index=True,
        comment="Final severity level assigned to this session.",
    )

    # ---- Session Metadata -----------------------------------------------
    status: Mapped[SessionStatus] = mapped_column(
        SAEnum(SessionStatus, name="session_status_enum", create_type=True),
        nullable=False,
        default=SessionStatus.ACTIVE,
        server_default=SessionStatus.ACTIVE.value,
        index=True,
        comment="Lifecycle status of this assessment session.",
    )
    consultation_mode: Mapped[ConsultationMode] = mapped_column(
        SAEnum(ConsultationMode, name="consultation_mode_enum", create_type=True),
        nullable=False,
        default=ConsultationMode.TEXT,
        server_default=ConsultationMode.TEXT.value,
        comment="Interaction mode used during this session.",
    )
    language_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
        server_default="en",
        comment="BCP 47 language code active during this session.",
    )

    # ---- Offline Sync ---------------------------------------------------
    created_offline: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        comment="True if this session was created while the client was offline.",
    )
    conducted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="UTC timestamp when the session was actually conducted (may predate sync).",
    )
    synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC timestamp when this offline session was synced to the server.",
    )
    client_session_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        unique=True,
        index=True,
        comment="Client-side UUID for idempotent offline outbox sync.",
    )

    # ---- AI Enhancement -------------------------------------------------
    ai_explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Gemini AI generated contextual explanation (Phase 2).",
    )
    raw_answers_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Complete node_id→answer_value snapshot for rule engine audit trail.",
    )

    # ---- Relationships --------------------------------------------------
    user: Mapped[Optional["UserModel"]] = relationship(
        "UserModel",
        back_populates="assessment_sessions",
    )
    symptom: Mapped[Optional["SymptomModel"]] = relationship(
        "SymptomModel",
        foreign_keys=[symptom_id],
    )
    identified_concern: Mapped[Optional["HealthConcernModel"]] = relationship(
        "HealthConcernModel",
        foreign_keys=[identified_concern_id],
    )
    severity_level: Mapped[Optional["SeverityLevelModel"]] = relationship(
        "SeverityLevelModel",
        foreign_keys=[severity_level_id],
    )
    responses: Mapped[List["AssessmentResponseModel"]] = relationship(
        "AssessmentResponseModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="AssessmentResponseModel.answered_at",
    )

    def __repr__(self) -> str:
        return (
            f"<AssessmentSession id={self.id!r} "
            f"status={self.status} "
            f"offline={self.created_offline}>"
        )
