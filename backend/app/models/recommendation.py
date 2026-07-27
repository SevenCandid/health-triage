"""Recommendation Model.

A clinical recommendation associated with a HealthConcern.
One concern may have multiple recommendations (e.g. primary action,
first aid steps, self-care guidance), differentiated by type.

See /docs/RuleEngineDesign.md — Section 1 Severity Classifications.
"""

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.health_concern import HealthConcernModel
    from app.models.recommendation_translation import RecommendationTranslationModel


class RecommendationType(str, enum.Enum):
    """Classification of the recommendation content type."""

    PRIMARY_ACTION = "PRIMARY_ACTION"      # The main call-to-action (e.g. "Call 112 now")
    FIRST_AID_STEP = "FIRST_AID_STEP"      # Ordered first aid instructions
    SELF_CARE = "SELF_CARE"                # Home self-care guidance
    MONITORING = "MONITORING"              # Symptom monitoring instructions
    REFERRAL = "REFERRAL"                  # When/where to seek further care
    DO_NOT = "DO_NOT"                      # Things to avoid (e.g. "Do not give food/water")


class RecommendationModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Clinical recommendation linked to a HealthConcern."""

    __tablename__ = "recommendations"
    __table_args__ = {
        "comment": (
            "Clinical recommendations displayed on triage result cards. "
            "Multiple recommendation types per health concern are supported."
        )
    }

    # ---- Foreign Key ----------------------------------------------------
    health_concern_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("health_concerns.id", ondelete="CASCADE", name="fk_recommendations_concern_id"),
        nullable=False,
        index=True,
        comment="Parent health concern UUID.",
    )

    # ---- Columns --------------------------------------------------------
    recommendation_type: Mapped[RecommendationType] = mapped_column(
        SAEnum(RecommendationType, name="recommendation_type_enum", create_type=True),
        nullable=False,
        index=True,
        comment="Classifies the recommendation for rendering in the correct UI section.",
    )
    content_en: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Recommendation text in English (canonical).",
    )
    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Display order for FIRST_AID_STEP type recommendations.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        comment="Inactive recommendations are excluded from result cards.",
    )
    source_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Clinical evidence source (e.g. 'WHO First Aid Guidelines 2021, p.42').",
    )

    # ---- Relationships --------------------------------------------------
    health_concern: Mapped["HealthConcernModel"] = relationship(
        "HealthConcernModel",
        back_populates="recommendations",
    )
    translations: Mapped[List["RecommendationTranslationModel"]] = relationship(
        "RecommendationTranslationModel",
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Recommendation type={self.recommendation_type} "
            f"order={self.step_order}>"
        )
