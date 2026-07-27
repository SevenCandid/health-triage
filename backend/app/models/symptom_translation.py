"""Symptom Translation Model.

Stores localized display strings for each Symptom in each Language.
Implements the EAV (Entity-Attribute-Value) translation pattern so
the primary Symptom table remains language-agnostic.

See /docs/FunctionalRequirements.md — FR-MLG-002 Dynamic i18n.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.symptom import SymptomModel
    from app.models.language import LanguageModel


class SymptomTranslationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Per-language localization strings for a Symptom entry."""

    __tablename__ = "symptom_translations"
    __table_args__ = (
        UniqueConstraint(
            "symptom_id",
            "language_code",
            name="uq_symptom_translations_symptom_lang",
        ),
        {
            "comment": (
                "One row per symptom-language pair. "
                "Provides translated name and description for symptom picker UI."
            )
        },
    )

    # ---- Foreign Keys ---------------------------------------------------
    symptom_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("symptoms.id", ondelete="CASCADE", name="fk_symptom_translations_symptom_id"),
        nullable=False,
        index=True,
        comment="Symptom this translation belongs to.",
    )
    language_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("languages.code", ondelete="CASCADE", name="fk_symptom_translations_lang_code"),
        nullable=False,
        index=True,
        comment="BCP 47 language code for this translation.",
    )

    # ---- Localized Content ----------------------------------------------
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Localized symptom display name.",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Localized brief clinical description shown in the symptom picker.",
    )
    voice_prompt: Mapped[Optional[str]] = mapped_column(
        String(300),
        nullable=True,
        comment="TTS-optimized text for voice consultation mode in this language.",
    )

    # ---- Relationships --------------------------------------------------
    symptom: Mapped["SymptomModel"] = relationship(
        "SymptomModel",
        back_populates="translations",
    )
    language: Mapped["LanguageModel"] = relationship(
        "LanguageModel",
        back_populates="symptom_translations",
    )

    def __repr__(self) -> str:
        return (
            f"<SymptomTranslation symptom_id={self.symptom_id!r} "
            f"lang={self.language_code!r}>"
        )
