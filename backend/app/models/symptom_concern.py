"""Symptom–Concern Association Model.

Pure join table recording the many-to-many relationship between
Symptoms and HealthConcerns, with an additional `weight` column
indicating how strongly a symptom correlates with the concern.

Higher weight values indicate stronger diagnostic association.
Used by the rule engine to score composite health concern matches.

See /docs/RuleEngineDesign.md — Section 4 Evaluator Algorithm.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.symptom import SymptomModel
    from app.models.health_concern import HealthConcernModel


class SymptomConcernModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Many-to-many join between Symptoms and HealthConcerns with weighting."""

    __tablename__ = "symptom_concerns"
    __table_args__ = (
        UniqueConstraint(
            "symptom_id",
            "health_concern_id",
            name="uq_symptom_concerns_pair",
        ),
        {
            "comment": (
                "Association table mapping symptoms to health concerns. "
                "Weight (0.0–1.0) represents diagnostic association strength."
            )
        },
    )

    # ---- Foreign Keys ---------------------------------------------------
    symptom_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("symptoms.id", ondelete="CASCADE", name="fk_symptom_concerns_symptom_id"),
        nullable=False,
        index=True,
        comment="Symptom UUID.",
    )
    health_concern_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("health_concerns.id", ondelete="CASCADE", name="fk_symptom_concerns_concern_id"),
        nullable=False,
        index=True,
        comment="HealthConcern UUID.",
    )

    # ---- Association Metadata -------------------------------------------
    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="Diagnostic association weight (0.0 = weak, 1.0 = definitive).",
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Evaluation priority order for this symptom within the concern.",
    )

    # ---- Relationships --------------------------------------------------
    symptom: Mapped["SymptomModel"] = relationship(
        "SymptomModel",
        back_populates="symptom_concerns",
    )
    health_concern: Mapped["HealthConcernModel"] = relationship(
        "HealthConcernModel",
        back_populates="symptom_concerns",
    )

    def __repr__(self) -> str:
        return (
            f"<SymptomConcern symptom={self.symptom_id!r} "
            f"concern={self.health_concern_id!r} weight={self.weight}>"
        )
