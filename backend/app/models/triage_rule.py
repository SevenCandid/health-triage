"""Triage Rule Model.

Encodes a single clinical triage decision rule:
  "IF symptom [symptom_id] is present
   AND qualifier answers match [rule_conditions]
   THEN classify as [severity_level_id]
   AND identify concern [health_concern_id]"

Rules are evaluated by the Python rule engine in priority order.
The first matching rule wins (short-circuit evaluation).

See /docs/RuleEngineDesign.md — Section 3 Decision Tree Logic.
"""

import enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String, Text, text, JSON
# Removed JSONB from dialects.postgresql import
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.symptom import SymptomModel
    from app.models.severity_level import SeverityLevelModel
    from app.models.health_concern import HealthConcernModel


class RuleLogicOperator(str, enum.Enum):
    """Logical operator applied to rule_conditions when multiple conditions exist."""

    AND = "AND"
    OR = "OR"


class TriageRuleModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A single clinical triage evaluation rule.

    Condition matching uses JSONB for flexibility — conditions are a list
    of {node_id, answer_value} dicts that must all match (AND) or any must
    match (OR) based on logic_operator.
    """

    __tablename__ = "triage_rules"
    __table_args__ = {
        "comment": (
            "Clinical decision rules evaluated by the rule engine. "
            "Lower priority_order values are evaluated first."
        )
    }

    # ---- Foreign Keys ---------------------------------------------------
    symptom_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("symptoms.id", ondelete="RESTRICT", name="fk_triage_rules_symptom_id"),
        nullable=False,
        index=True,
        comment="Primary symptom this rule applies to.",
    )
    severity_level_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("severity_levels.id", ondelete="RESTRICT", name="fk_triage_rules_severity_id"),
        nullable=False,
        index=True,
        comment="Severity level assigned when this rule matches.",
    )
    health_concern_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("health_concerns.id", ondelete="SET NULL", name="fk_triage_rules_concern_id"),
        nullable=True,
        index=True,
        comment="Health concern identified when this rule matches (optional).",
    )

    # ---- Rule Definition ------------------------------------------------
    rule_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Human-readable rule name for admin UI, e.g. 'Chest Pain + Dyspnoea → RED'.",
    )
    rule_conditions: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment=(
            "JSONB list of condition objects: "
            "[{node_id: str, answer_value: str, negated: bool}]. "
            "Empty list = match always (catch-all rule)."
        ),
    )
    logic_operator: Mapped[RuleLogicOperator] = mapped_column(
        SAEnum(RuleLogicOperator, name="rule_logic_operator_enum", create_type=True),
        nullable=False,
        default=RuleLogicOperator.AND,
        server_default=RuleLogicOperator.AND.value,
        comment="AND = all conditions must match; OR = any condition must match.",
    )
    priority_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        server_default="100",
        index=True,
        comment="Evaluation priority — lower values are checked first.",
    )
    is_red_flag_override: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="If True, this rule short-circuits all other rules and returns RED immediately.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
        comment="Inactive rules are excluded from evaluation.",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Clinical rationale or source reference for this rule.",
    )

    # ---- Relationships --------------------------------------------------
    symptom: Mapped["SymptomModel"] = relationship(
        "SymptomModel",
        back_populates="triage_rules",
    )
    severity_level: Mapped["SeverityLevelModel"] = relationship(
        "SeverityLevelModel",
        back_populates="triage_rules",
    )
    health_concern: Mapped[Optional["HealthConcernModel"]] = relationship(
        "HealthConcernModel",
        back_populates="triage_rules",
    )

    def __repr__(self) -> str:
        return (
            f"<TriageRule name={self.rule_name!r} "
            f"priority={self.priority_order} "
            f"red_flag={self.is_red_flag_override}>"
        )
