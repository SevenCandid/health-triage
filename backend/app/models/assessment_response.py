"""Assessment Response Model.

Records a single question-answer pair within an AssessmentSession.
One row per question answered — provides the complete decision tree
traversal trail for rule engine re-evaluation and audit.

See /docs/RuleEngineDesign.md — Section 4 Evaluator Algorithm.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.health_conversation import HealthConversationModel
    from app.models.question import QuestionModel
    from app.models.question_option import QuestionOptionModel
    from app.models.symptom import SymptomModel


class AssessmentResponseModel(UUIDPrimaryKeyMixin, Base):
    """Individual question-answer record within an assessment session."""

    __tablename__ = "assessment_responses"
    __table_args__ = {
        "comment": (
            "One row per question answered during a triage session. "
            "Provides full audit trail for rule engine evaluation and AI explanation."
        )
    }

    # ---- Foreign Keys ---------------------------------------------------
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "health_conversations.id",
            ondelete="CASCADE",
            name="fk_assessment_responses_conversation_id",
        ),
        nullable=False,
        index=True,
        comment="Parent health conversation UUID.",
    )
    symptom_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey(
            "symptoms.id",
            ondelete="SET NULL",
            name="fk_assessment_responses_symptom_id",
        ),
        nullable=True,
        index=True,
        comment="Symptom this response pertains to.",
    )
    question_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey(
            "questions.id",
            ondelete="SET NULL",
            name="fk_assessment_responses_question_id",
        ),
        nullable=True,
        index=True,
        comment="Question that was answered. NULL if question was deleted after session.",
    )
    selected_option_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey(
            "question_options.id",
            ondelete="SET NULL",
            name="fk_assessment_responses_option_id",
        ),
        nullable=True,
        index=True,
        comment="QuestionOption selected. NULL for free-text or numeric responses.",
    )

    # ---- Answer Data ----------------------------------------------------
    node_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Node ID from the decision tree (matches question.node_id).",
    )
    answer_value: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Selected answer value (option_value, free-text, or numeric string).",
    )
    answer_raw_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Voice transcription raw text for VOICE mode responses.",
    )
    triggered_red_flag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="True if this answer triggered a red-flag override.",
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="UTC timestamp when this answer was recorded.",
    )

    # ---- Relationships --------------------------------------------------
    conversation: Mapped["HealthConversationModel"] = relationship(
        "HealthConversationModel",
        back_populates="responses",
    )
    symptom: Mapped[Optional["SymptomModel"]] = relationship(
        "SymptomModel",
        foreign_keys=[symptom_id],
    )
    question: Mapped[Optional["QuestionModel"]] = relationship(
        "QuestionModel",
        foreign_keys=[question_id],
    )
    selected_option: Mapped[Optional["QuestionOptionModel"]] = relationship(
        "QuestionOptionModel",
        foreign_keys=[selected_option_id],
    )

    def __repr__(self) -> str:
        return (
            f"<AssessmentResponse node={self.node_id!r} "
            f"value={self.answer_value!r} "
            f"red_flag={self.triggered_red_flag}>"
        )
