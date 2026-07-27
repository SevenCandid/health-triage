"""Recommendation Translation Model.

Per-language localized content for each Recommendation.
Follows the same EAV translation pattern as SymptomTranslation.

See /docs/FunctionalRequirements.md — FR-MLG-002.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.recommendation import RecommendationModel
    from app.models.language import LanguageModel


class RecommendationTranslationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Per-language localized content for a Recommendation."""

    __tablename__ = "recommendation_translations"
    __table_args__ = (
        UniqueConstraint(
            "recommendation_id",
            "language_code",
            name="uq_rec_translations_rec_lang",
        ),
        {
            "comment": (
                "Localized recommendation text per language. "
                "One row per recommendation-language pair."
            )
        },
    )

    # ---- Foreign Keys ---------------------------------------------------
    recommendation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "recommendations.id",
            ondelete="CASCADE",
            name="fk_rec_translations_recommendation_id",
        ),
        nullable=False,
        index=True,
        comment="Parent recommendation UUID.",
    )
    language_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey(
            "languages.code",
            ondelete="CASCADE",
            name="fk_rec_translations_lang_code",
        ),
        nullable=False,
        index=True,
        comment="BCP 47 language code.",
    )

    # ---- Localized Content ----------------------------------------------
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Localized recommendation text.",
    )
    voice_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="TTS-optimized version for voice consultation mode.",
    )

    # ---- Relationships --------------------------------------------------
    recommendation: Mapped["RecommendationModel"] = relationship(
        "RecommendationModel",
        back_populates="translations",
    )
    language: Mapped["LanguageModel"] = relationship(
        "LanguageModel",
        back_populates="recommendation_translations",
    )

    def __repr__(self) -> str:
        return (
            f"<RecommendationTranslation rec={self.recommendation_id!r} "
            f"lang={self.language_code!r}>"
        )
