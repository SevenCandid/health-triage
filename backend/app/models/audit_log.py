"""Audit Log Model.

Immutable append-only record of security-relevant state changes.
Used for GDPR compliance, security incident forensics, and admin oversight.

Records: login attempts, profile updates, data deletions, role changes,
emergency dispatches, and API key usage.

See /docs/Privacy.md — Section 5 Audit Trail Requirements.
"""

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, String, Text, JSON
# Removed JSONB from dialects.postgresql import
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.models.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import UserModel


class AuditAction(str, enum.Enum):
    """Classified audit event types."""

    # Auth events
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN_SUCCESS = "USER_LOGIN_SUCCESS"
    USER_LOGIN_FAILURE = "USER_LOGIN_FAILURE"
    USER_LOGOUT = "USER_LOGOUT"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    # Data events
    PROFILE_CREATED = "PROFILE_CREATED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    EMERGENCY_CONTACT_ADDED = "EMERGENCY_CONTACT_ADDED"
    EMERGENCY_CONTACT_REMOVED = "EMERGENCY_CONTACT_REMOVED"
    # Triage events
    ASSESSMENT_STARTED = "ASSESSMENT_STARTED"
    ASSESSMENT_COMPLETED = "ASSESSMENT_COMPLETED"
    EMERGENCY_DISPATCHED = "EMERGENCY_DISPATCHED"
    # Admin events
    USER_DEACTIVATED = "USER_DEACTIVATED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    USER_DATA_DELETED = "USER_DATA_DELETED"
    # Sync events
    OFFLINE_SYNC_COMPLETED = "OFFLINE_SYNC_COMPLETED"


class AuditLogModel(UUIDPrimaryKeyMixin, Base):
    """Immutable, append-only security and compliance audit log entry.

    CRITICAL: This table must NEVER have UPDATE or DELETE operations applied.
    All records are permanent. Only INSERT is allowed.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_user_id_action", "user_id", "action"),
        Index("idx_audit_logs_occurred_at", "occurred_at"),
        {
            "comment": (
                "Immutable audit trail. INSERT ONLY — no updates or deletes permitted. "
                "Required for GDPR Article 30 (Records of processing activities)."
            )
        },
    )

    # ---- Actor ----------------------------------------------------------
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL", name="fk_audit_logs_user_id"),
        nullable=True,
        index=True,
        comment="Actor user UUID. NULL for anonymous or system-generated events.",
    )

    # ---- Event Descriptor -----------------------------------------------
    action: Mapped[AuditAction] = mapped_column(
        SAEnum(AuditAction, name="audit_action_enum", create_type=True),
        nullable=False,
        index=True,
        comment="Classified audit event type.",
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(60),
        nullable=True,
        comment="Resource type affected, e.g. 'User', 'AssessmentSession'.",
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        comment="UUID of the specific resource instance affected.",
    )

    # ---- Context --------------------------------------------------------
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="UTC timestamp when this event occurred.",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Requester IPv4/IPv6 address (max 45 chars covers IPv6).",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="HTTP User-Agent header of the client that triggered the event.",
    )
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Arbitrary event context payload (e.g. changed field names, new values).",
    )
    outcome: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Event outcome: 'SUCCESS', 'FAILURE', 'PARTIAL'.",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable summary of the event for admin review.",
    )

    # ---- Relationships --------------------------------------------------
    user: Mapped[Optional["UserModel"]] = relationship(
        "UserModel",
        back_populates="audit_logs",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog action={self.action} "
            f"user={self.user_id!r} "
            f"at={self.occurred_at}>"
        )
