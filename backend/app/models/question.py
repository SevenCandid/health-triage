"""Question Model.

Represents an individual decision tree node question belonging to a Symptom's
evaluation flow. Questions are presented sequentially during a triage session
and each has one or more QuestionOptions to choose from.

Mirrors the node schema defined in /docs/RuleEngineDesign.md Section 2.
"""

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.symptom import SymptomModel
    from app.models.question_option import QuestionOptionModel


class QuestionType(str, enum.Enum):
    """Type of answer UI control rendered for this question."""

    SINGLE_SELECT = "SINGLE_SELECT"    # Radio buttons — one answer
    MULTI_SELECT = "MULTI_SELECT"      # Checkboxes — multiple allowed
    BOOLEAN = "BOOLEAN"                # Yes / No only
    NUMERIC = "NUMERIC"                # Numeric slider or input
    TEXT = "TEXT"                      # Free-text input (voice-transcribed)


class QuestionModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A clinical decision-tree node question within a symptom evaluation flow."""

    __tablename__ = "questions"
    __table_args__ = {
        "comment": (
            "Decision tree node questions for symptom evaluation flows. "
            "Ordered by order_index within each symptom tree."
        )
    }

    # ---- Foreign Key ----------------------------------------------------
    symptom_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("symptoms.id", ondelete="CASCADE", name="fk_questions_symptom_id"),
        nullable=False,
        index=True,
        comment="Symptom decision tree this question belongs to.",
    )

    # ---- Columns --------------------------------------------------------
    node_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Stable node ID matching the JSON rule tree structure, e.g. 'node_chest_pain_qualifier'.",
    )
    question_text_en: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Question text in English (canonical).",
    )
    question_text_tw: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Question text in Twi.",
    )
    voice_prompt_en: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="TTS-optimized English question for voice mode.",
    )
    voice_prompt_tw: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="TTS-optimized Twi question for voice mode.",
    )
    question_type: Mapped[QuestionType] = mapped_column(
        SAEnum(QuestionType, name="question_type_enum", create_type=True),
        nullable=False,
        default=QuestionType.SINGLE_SELECT,
        server_default=QuestionType.SINGLE_SELECT.value,
        comment="UI control type for rendering the answer widget.",
    )
    is_red_flag_trigger: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="If True, certain answers to this question trigger immediate RED urgency.",
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        comment="If True, patient must answer before proceeding.",
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
        comment="Display order within this symptom's decision tree.",
    )
    help_text_en: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional clinical help text shown below the question.",
    )

    # ---- Relationships --------------------------------------------------
    symptom: Mapped["SymptomModel"] = relationship(
        "SymptomModel",
        back_populates="questions",
    )
    options: Mapped[List["QuestionOptionModel"]] = relationship(
        "QuestionOptionModel",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOptionModel.order_index",
    )

    def __repr__(self) -> str:
        return (
            f"<Question node_id={self.node_id!r} "
            f"type={self.question_type} "
            f"order={self.order_index}>"
        )
