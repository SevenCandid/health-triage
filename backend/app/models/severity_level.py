"""Severity Level Model.

Configuration table defining the four clinical urgency tiers (RED, ORANGE,
YELLOW, GREEN) adapted from the Manchester Triage System.

Each severity level carries its UI presentation metadata (badge color,
icon, timeframe) separately from the Python enum so that non-developer
clinical admins can update display labels without code changes.

See /docs/RuleEngineDesign.md — Section 1 Severity Classifications.
"""

import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SAEnum, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.health_concern import HealthConcernModel
    from app.models.triage_rule import TriageRuleModel


class UrgencyCode(str, enum.Enum):
    """The four canonical clinical urgency codes.

    These must mirror app/domain/value_objects/urgency_level.py exactly.
    """

    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class SeverityLevelModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Clinical severity / urgency level configuration record."""

    __tablename__ = "severity_levels"
    __table_args__ = (
        UniqueConstraint("code", name="uq_severity_levels_code"),
        {
            "comment": (
                "Configuration table for the four MTS urgency levels. "
                "Exactly four rows — one per UrgencyCode enum value."
            )
        },
    )

    # ---- Columns --------------------------------------------------------
    code: Mapped[UrgencyCode] = mapped_column(
        SAEnum(UrgencyCode, name="urgency_code_enum", create_type=True),
        nullable=False,
        unique=True,
        index=True,
        comment="Canonical urgency code (RED/ORANGE/YELLOW/GREEN).",
    )
    label_en: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        comment="Display label in English, e.g. 'Emergency', 'Very Urgent'.",
    )
    label_tw: Mapped[Optional[str]] = mapped_column(
        String(60),
        nullable=True,
        comment="Display label in Twi.",
    )
    description_en: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Clinical description shown in triage result card.",
    )
    badge_color_hex: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
        comment="CSS hex color for UI urgency badge, e.g. '#DC2626'.",
    )
    timeframe_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Maximum recommended care timeframe in minutes (0 = immediate).",
    )
    requires_emergency_dispatch: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="True only for RED — triggers GPS, SMS, and Emergency Centre.",
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Sort order for admin dashboard severity filter display.",
    )

    # ---- Relationships --------------------------------------------------
    health_concerns: Mapped[List["HealthConcernModel"]] = relationship(
        "HealthConcernModel",
        back_populates="severity_level",
    )
    triage_rules: Mapped[List["TriageRuleModel"]] = relationship(
        "TriageRuleModel",
        back_populates="severity_level",
    )

    def __repr__(self) -> str:
        return (
            f"<SeverityLevel code={self.code} "
            f"timeframe={self.timeframe_minutes}min>"
        )
