"""Symptom Category Model.

Groups symptoms into clinical domains (e.g. Cardiovascular, Respiratory,
Neurological). Categories drive the initial symptom picker UI and route
the user into the appropriate decision tree branch.

See /docs/RuleEngineDesign.md — Section 2 Decision Tree Schema.
"""

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SAEnum, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.symptom import SymptomModel


class BodySystem(str, enum.Enum):
    """Clinical body system classification for symptom grouping."""

    CARDIOVASCULAR = "CARDIOVASCULAR"
    RESPIRATORY = "RESPIRATORY"
    NEUROLOGICAL = "NEUROLOGICAL"
    GASTROINTESTINAL = "GASTROINTESTINAL"
    MUSCULOSKELETAL = "MUSCULOSKELETAL"
    DERMATOLOGICAL = "DERMATOLOGICAL"
    ENDOCRINE = "ENDOCRINE"
    REPRODUCTIVE = "REPRODUCTIVE"
    UROLOGICAL = "UROLOGICAL"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    OPHTHALMOLOGICAL = "OPHTHALMOLOGICAL"
    ENT = "ENT"
    HAEMATOLOGICAL = "HAEMATOLOGICAL"
    INFECTIOUS = "INFECTIOUS"
    OTHER = "OTHER"


class SymptomCategoryModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Clinical symptom category (body system grouping)."""

    __tablename__ = "symptom_categories"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_symptom_categories_slug"),
        {"comment": "Clinical category groupings for symptom picker UI and decision tree routing."},
    )

    # ---- Columns --------------------------------------------------------
    name_en: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Category display name in English.",
    )
    name_tw: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Category display name in Twi.",
    )
    slug: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-safe kebab-case identifier, e.g. 'chest-pain'.",
    )
    body_system: Mapped[BodySystem] = mapped_column(
        SAEnum(BodySystem, name="body_system_enum", create_type=True),
        nullable=False,
        index=True,
        comment="Clinical body system this category belongs to.",
    )
    icon_name: Mapped[Optional[str]] = mapped_column(
        String(60),
        nullable=True,
        comment="Material / Lucide icon name for UI rendering.",
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Sort order for symptom picker display.",
    )
    is_emergency_fast_track: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="If True, this category bypasses standard flow and opens Emergency Centre immediately.",
    )

    # ---- Relationships --------------------------------------------------
    symptoms: Mapped[List["SymptomModel"]] = relationship(
        "SymptomModel",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="SymptomModel.display_order",
    )

    def __repr__(self) -> str:
        return f"<SymptomCategory slug={self.slug!r} system={self.body_system}>"
