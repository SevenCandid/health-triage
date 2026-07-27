"""Question Option Model.

Represents a selectable answer option for a Question node.
Each option may lead to the next question (via next_node_id), terminate
the decision tree with a severity result, or trigger a red flag.

Mirrors the `options[]` array in /docs/RuleEngineDesign.md Section 2.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.question import QuestionModel
    from app.models.severity_level import SeverityLevelModel


class QuestionOptionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A selectable answer option for a decision-tree Question node."""

    __tablename__ = "question_options"
    __table_args__ = {
        "comment": (
            "Answer options for clinical decision tree questions. "
            "Option may route to next question, terminate, or trigger emergency."
        )
    }

    # ---- Foreign Keys ---------------------------------------------------
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE", name="fk_question_options_question_id"),
        nullable=False,
        index=True,
        comment="Parent question UUID.",
    )
    terminal_severity_level_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey(
            "severity_levels.id",
            ondelete="SET NULL",
            name="fk_question_options_severity_id",
        ),
        nullable=True,
        index=True,
        comment="Severity level produced if this is a terminal option. NULL if non-terminal.",
    )

    # ---- Option Content -------------------------------------------------
    option_value: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Machine-readable answer value stored in AssessmentResponse.",
    )
    label_en: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Option display label in English.",
    )
    label_tw: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Option display label in Twi.",
    )

    # ---- Routing --------------------------------------------------------
    next_node_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Node ID of the next question if this option is selected. NULL if terminal.",
    )
    is_terminal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="True if selecting this option ends the decision tree evaluation.",
    )
    is_red_flag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="True if selecting this option immediately triggers RED urgency override.",
    )

    # ---- Display --------------------------------------------------------
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Display order of this option within its parent question.",
    )

    # ---- Relationships --------------------------------------------------
    question: Mapped["QuestionModel"] = relationship(
        "QuestionModel",
        back_populates="options",
    )
    terminal_severity_level: Mapped[Optional["SeverityLevelModel"]] = relationship(
        "SeverityLevelModel",
        foreign_keys=[terminal_severity_level_id],
    )

    def __repr__(self) -> str:
        return (
            f"<QuestionOption value={self.option_value!r} "
            f"terminal={self.is_terminal} "
            f"red_flag={self.is_red_flag}>"
        )
