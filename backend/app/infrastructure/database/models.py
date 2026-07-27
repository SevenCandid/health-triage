"""SQLAlchemy 2.0 Relational Models Specification.

Maps to database tables defined in /docs/DatabaseDesign.md.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.user import UserModel

def utc_now() -> datetime:
    """Returns current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

class HealthProfileModel(Base):
    """User personal health profiles table mapping."""

    __tablename__ = "health_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    biological_sex: Mapped[str] = mapped_column(String(20), nullable=False)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    chronic_conditions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    known_allergies: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel")


class RuleTreeModel(Base):
    """Versioned clinical decision rule trees table mapping."""

    __tablename__ = "rule_trees"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    version: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tree_structure: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    triage_sessions: Mapped[List["TriageSessionModel"]] = relationship(
        "TriageSessionModel", back_populates="rule_tree"
    )


class TriageSessionModel(Base):
    """Patient triage session logs table mapping."""

    __tablename__ = "triage_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    rule_tree_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("rule_trees.id"), nullable=True
    )
    urgency_level: Mapped[str] = mapped_column(String(10), index=True, nullable=False) # RED, ORANGE, YELLOW, GREEN
    primary_symptom: Mapped[str] = mapped_column(String(100), nullable=False)
    symptom_details: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    ai_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language_code: Mapped[str] = mapped_column(String(5), default="en", nullable=False)
    created_offline: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    conducted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    user: Mapped[Optional["UserModel"]] = relationship("UserModel")
    rule_tree: Mapped[Optional["RuleTreeModel"]] = relationship(
        "RuleTreeModel", back_populates="triage_sessions"
    )
    emergency_log: Mapped[Optional["EmergencyLogModel"]] = relationship(
        "EmergencyLogModel", back_populates="triage_session", uselist=False
    )


class EmergencyLogModel(Base):
    """Emergency trigger logs and GPS telemetry mapping."""

    __tablename__ = "emergency_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    triage_session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("triage_sessions.id"), nullable=False, unique=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DISPATCHED", nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    triage_session: Mapped["TriageSessionModel"] = relationship(
        "TriageSessionModel", back_populates="emergency_log"
    )
