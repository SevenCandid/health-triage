"""Emergency Contact Model.

Stores emergency contacts registered by a user. Up to 5 contacts
are allowed per user; exactly one must be marked as primary.

See /docs/EmergencySystem.md — Section 2.1 Contact Registry.
"""

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import UserModel


class RelationshipType(str, enum.Enum):
    """Relationship of the emergency contact to the patient."""

    SPOUSE = "SPOUSE"
    PARENT = "PARENT"
    CHILD = "CHILD"
    SIBLING = "SIBLING"
    FRIEND = "FRIEND"
    COLLEAGUE = "COLLEAGUE"
    HEALTHCARE_PROVIDER = "HEALTHCARE_PROVIDER"
    OTHER = "OTHER"


class EmergencyContactModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """User-registered emergency contacts for alert dispatch."""

    __tablename__ = "emergency_contacts"
    __table_args__ = {
        "comment": (
            "Emergency contacts registered by users. Max 5 per user enforced at service layer. "
            "Primary contact receives the first SMS dispatch on RED urgency."
        )
    }

    # ---- Foreign Key ----------------------------------------------------
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE", name="fk_emergency_contacts_user_id"),
        nullable=False,
        index=True,
        comment="Owning user UUID.",
    )

    # ---- Contact Details ------------------------------------------------
    contact_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Full name of the emergency contact person.",
    )
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="E.164 phone number for SMS dispatch.",
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        SAEnum(RelationshipType, name="relationship_type_enum", create_type=True),
        nullable=False,
        default=RelationshipType.OTHER,
        server_default=RelationshipType.OTHER.value,
        comment="Relationship of this contact to the patient.",
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        comment="True for the single primary contact who receives first-priority SMS.",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Optional free-text notes about this contact (e.g. 'Speaks Twi only').",
    )

    # ---- Relationships --------------------------------------------------
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="emergency_contacts",
    )

    def __repr__(self) -> str:
        return (
            f"<EmergencyContact id={self.id!r} "
            f"name={self.contact_name!r} "
            f"primary={self.is_primary}>"
        )
