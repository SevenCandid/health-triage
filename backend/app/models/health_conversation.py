"""Health Conversation Model.

Records an ongoing health conversation (formerly AssessmentSession) conducted by a user.
A conversation can contain multiple symptoms, evaluated interactively, and aggregated.
"""

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, Text, text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.symptom import SymptomModel
    from app.models.severity_level import SeverityLevelModel
    from app.models.health_concern import HealthConcernModel
    from app.models.assessment_response import AssessmentResponseModel


class ConversationStatus(str, enum.Enum):
    """Lifecycle status of a health conversation."""
    IN_PROGRESS = "IN_PROGRESS"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    ARCHIVED = "ARCHIVED"
    SYNCED = "SYNCED"


class ConsultationMode(str, enum.Enum):
    """How the user interacted with the triage flow."""
    TEXT = "TEXT"
    VOICE = "VOICE"
    HYBRID = "HYBRID"


class ConversationSymptomModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Links a HealthConversation to a specific Symptom, storing its sub-evaluation result."""
    __tablename__ = "conversation_symptoms"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("health_conversations.id", ondelete="CASCADE", name="fk_conv_symp_conversation_id"),
        nullable=False,
        index=True,
    )
    symptom_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("symptoms.id", ondelete="CASCADE", name="fk_conv_symp_symptom_id"),
        nullable=False,
        index=True,
    )
    identified_concern_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("health_concerns.id", ondelete="SET NULL", name="fk_conv_symp_concern_id"),
        nullable=True,
    )
    severity_level_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("severity_levels.id", ondelete="SET NULL", name="fk_conv_symp_severity_id"),
        nullable=True,
    )

    conversation: Mapped["HealthConversationModel"] = relationship(
        "HealthConversationModel", back_populates="symptoms"
    )
    symptom: Mapped["SymptomModel"] = relationship("SymptomModel")
    identified_concern: Mapped[Optional["HealthConcernModel"]] = relationship("HealthConcernModel")
    severity_level: Mapped[Optional["SeverityLevelModel"]] = relationship("SeverityLevelModel")

    def __repr__(self) -> str:
        return f"<ConversationSymptom conv={self.conversation_id} sym={self.symptom_id}>"


class HealthConversationModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Complete record of an ongoing health conversation."""

    __tablename__ = "health_conversations"

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE", name="fk_health_conversations_user_id"),
        nullable=True,
        index=True,
    )
    
    status: Mapped[ConversationStatus] = mapped_column(
        SAEnum(ConversationStatus, name="conversation_status_enum", create_type=True),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        server_default=ConversationStatus.ACTIVE.value,
        index=True,
    )
    consultation_mode: Mapped[ConsultationMode] = mapped_column(
        SAEnum(ConsultationMode, name="consultation_mode_enum", create_type=True),
        nullable=False,
        default=ConsultationMode.TEXT,
        server_default=ConsultationMode.TEXT.value,
    )
    language_code: Mapped[str] = mapped_column(
        String(10), nullable=False, default="en", server_default="en"
    )

    created_offline: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false"), index=True
    )
    conducted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    client_session_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, unique=True, index=True)

    ai_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_answers_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="conversations")
    symptoms: Mapped[List["ConversationSymptomModel"]] = relationship(
        "ConversationSymptomModel", back_populates="conversation", cascade="all, delete-orphan"
    )
    responses: Mapped[List["AssessmentResponseModel"]] = relationship(
        "AssessmentResponseModel", back_populates="conversation", cascade="all, delete-orphan", order_by="AssessmentResponseModel.answered_at"
    )

    def __repr__(self) -> str:
        return f"<HealthConversation id={self.id!r} status={self.status}>"
