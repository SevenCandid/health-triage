"""Symptom Model.

A clinical symptom entry within a category. Each symptom is the
entry point for one or more triage decision trees and has translated
display names stored in the SymptomTranslation table.

See /docs/RuleEngineDesign.md — Section 2 Decision Tree Schema.
"""

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.symptom_category import SymptomCategoryModel
    from app.models.symptom_translation import SymptomTranslationModel
    from app.models.symptom_concern import SymptomConcernModel
    from app.models.triage_rule import TriageRuleModel
    from app.models.question import QuestionModel


class SymptomSeverityHint(str, enum.Enum):
    """Pre-evaluation severity hint used to visually flag potentially dangerous symptoms."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SymptomModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Clinical symptom entity. One symptom → one decision tree entry point."""

    __tablename__ = "symptoms"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_symptoms_slug"),
        {"comment": "Clinical symptoms that trigger triage decision tree evaluations."},
    )

    # ---- Foreign Key ----------------------------------------------------
    category_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("symptom_categories.id", ondelete="RESTRICT", name="fk_symptoms_category_id"),
        nullable=False,
        index=True,
        comment="Owning symptom category UUID.",
    )

    # ---- Columns --------------------------------------------------------
    slug: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-safe identifier, e.g. 'chest-pain', 'severe-bleeding'.",
    )
    name_en: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Symptom display name in English (canonical).",
    )
    description_en: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Brief clinical description in English.",
    )
    severity_hint: Mapped[SymptomSeverityHint] = mapped_column(
        SAEnum(SymptomSeverityHint, name="symptom_severity_hint_enum", create_type=True),
        nullable=False,
        default=SymptomSeverityHint.MODERATE,
        server_default=SymptomSeverityHint.MODERATE.value,
        comment="Pre-evaluation severity hint for UI badge coloring.",
    )
    is_red_flag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        comment="If True, selecting this symptom immediately triggers Emergency Centre.",
    )
    icd10_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        index=True,
        comment="ICD-10 code for clinical interoperability, e.g. 'R07.4'.",
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Sort order within the parent category.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        comment="Inactive symptoms are hidden from the UI picker.",
    )

    # ---- Relationships --------------------------------------------------
    category: Mapped["SymptomCategoryModel"] = relationship(
        "SymptomCategoryModel",
        back_populates="symptoms",
    )
    translations: Mapped[List["SymptomTranslationModel"]] = relationship(
        "SymptomTranslationModel",
        back_populates="symptom",
        cascade="all, delete-orphan",
    )
    symptom_concerns: Mapped[List["SymptomConcernModel"]] = relationship(
        "SymptomConcernModel",
        back_populates="symptom",
        cascade="all, delete-orphan",
    )
    triage_rules: Mapped[List["TriageRuleModel"]] = relationship(
        "TriageRuleModel",
        back_populates="symptom",
        cascade="all, delete-orphan",
    )
    questions: Mapped[List["QuestionModel"]] = relationship(
        "QuestionModel",
        back_populates="symptom",
        cascade="all, delete-orphan",
        order_by="QuestionModel.order_index",
    )

    def __repr__(self) -> str:
        return f"<Symptom slug={self.slug!r} severity={self.severity_hint} red_flag={self.is_red_flag}>"
