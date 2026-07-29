"""User Model — Domain Layer.

Represents authenticated user accounts. Stores credentials and preferences.
All personally identifiable information (PII) beyond credentials lives in
the HealthProfile entity to support data minimization (GDPR Article 5).

See /docs/DatabaseDesign.md and /docs/Privacy.md.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.language import LanguageModel
    from app.models.emergency_contact import EmergencyContactModel
    from app.models.health_conversation import HealthConversationModel
    from app.models.audit_log import AuditLogModel


class UserRole(str, enum.Enum):
    """User access role classifications."""

    PATIENT = "PATIENT"
    HEALTH_WORKER = "HEALTH_WORKER"
    ADMIN = "ADMIN"


class BiologicalSex(str, enum.Enum):
    """Biological sex classification for clinical triage weighting."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class BloodGroup(str, enum.Enum):
    """ABO + Rh blood group classifications."""

    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"
    UNKNOWN = "UNKNOWN"


class UserModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """User account table. Credentials, preferences, and role assignment."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("phone_number", name="uq_users_phone_number"),
        {"comment": "Authenticated user accounts. PII is split into health_profiles."},
    )

    # ---- Credentials & Identity -----------------------------------------
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="E.164 format phone number used as login identifier.",
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Optional email address for login/recovery.",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Argon2id password hash. Never store plaintext.",
    )
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role_enum", create_type=True),
        nullable=False,
        default=UserRole.PATIENT,
        server_default=UserRole.PATIENT.value,
        comment="Access control role for the user.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        comment="False if account is suspended or pending verification.",
    )
    phone_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC timestamp when phone was verified (OTP).",
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC timestamp when email was verified.",
    )
    profile_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="True if the user has completed their health profile.",
    )

    # ---- Health Profile Fields (denormalized for offline triage) ---------
    full_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        comment="Display name. Required for registration.",
    )
    age: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Age in years. Used for paediatric and geriatric rule weighting.",
    )
    biological_sex: Mapped[Optional[BiologicalSex]] = mapped_column(
        SAEnum(BiologicalSex, name="biological_sex_enum", create_type=True),
        nullable=True,
        comment="Biological sex for sex-linked clinical rule evaluation.",
    )
    blood_group: Mapped[Optional[BloodGroup]] = mapped_column(
        SAEnum(BloodGroup, name="blood_group_enum", create_type=True),
        nullable=True,
        comment="ABO + Rh blood group. Optional clinical context.",
    )

    # ---- Language Preference --------------------------------------------
    preferred_language_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("languages.code", ondelete="SET DEFAULT", onupdate="CASCADE"),
        nullable=False,
        default="en",
        server_default="en",
        comment="BCP 47 code of the user's preferred UI language.",
    )

    # ---- Relationships --------------------------------------------------
    preferred_language_ref: Mapped[Optional["LanguageModel"]] = relationship(
        "LanguageModel",
        back_populates="users",
        foreign_keys=[preferred_language_code],
    )
    emergency_contacts: Mapped[List["EmergencyContactModel"]] = relationship(
        "EmergencyContactModel",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="EmergencyContactModel.is_primary.desc()",
    )
    conversations: Mapped[List["HealthConversationModel"]] = relationship(
        "HealthConversationModel",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="HealthConversationModel.created_at.desc()",
    )
    audit_logs: Mapped[List["AuditLogModel"]] = relationship(
        "AuditLogModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} phone={self.phone_number!r} role={self.role}>"
