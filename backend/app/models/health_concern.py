"""Health Concern Model.

Represents a high-level clinical health concern (e.g. "Possible Cardiac Event",
"Respiratory Distress") that groups related symptoms. A concern maps to a
specific recommended severity level and action protocol.

Health Concerns are the output concepts produced by the rule engine.
Each TriageRule maps a symptom pattern → a HealthConcern → a SeverityLevel.

See /docs/RuleEngineDesign.md — Section 4 Evaluator Algorithm.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.severity_level import SeverityLevelModel
    from app.models.symptom_concern import SymptomConcernModel
    from app.models.recommendation import RecommendationModel
    from app.models.triage_rule import TriageRuleModel


class HealthConcernModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A named clinical health concern with associated severity and recommendations."""

    __tablename__ = "health_concerns"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_health_concerns_slug"),
        {
            "comment": (
                "Named clinical health concerns produced by rule engine evaluation. "
                "Each concern is linked to a severity level and recommendation set."
            )
        },
    )

    # ---- Foreign Key ----------------------------------------------------
    severity_level_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("severity_levels.id", ondelete="RESTRICT", name="fk_health_concerns_severity_id"),
        nullable=False,
        index=True,
        comment="Default severity level assigned when this concern is identified.",
    )

    # ---- Columns --------------------------------------------------------
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-safe identifier, e.g. 'possible-cardiac-event'.",
    )
    name_en: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Concern name in English, e.g. 'Possible Cardiac Event'.",
    )
    name_tw: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Concern name in Twi.",
    )
    description_en: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Clinical description used in AI explanation context.",
    )
    requires_emergency_dispatch: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="If True, immediately opens Emergency Centre on identification.",
    )
    icd10_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        index=True,
        comment="ICD-10 code for clinical interoperability.",
    )

    # ---- Relationships --------------------------------------------------
    severity_level: Mapped["SeverityLevelModel"] = relationship(
        "SeverityLevelModel",
        back_populates="health_concerns",
    )
    symptom_concerns: Mapped[List["SymptomConcernModel"]] = relationship(
        "SymptomConcernModel",
        back_populates="health_concern",
        cascade="all, delete-orphan",
    )
    recommendations: Mapped[List["RecommendationModel"]] = relationship(
        "RecommendationModel",
        back_populates="health_concern",
        cascade="all, delete-orphan",
    )
    triage_rules: Mapped[List["TriageRuleModel"]] = relationship(
        "TriageRuleModel",
        back_populates="health_concern",
    )

    def __repr__(self) -> str:
        return (
            f"<HealthConcern slug={self.slug!r} "
            f"emergency={self.requires_emergency_dispatch}>"
        )
