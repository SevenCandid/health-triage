"""Language Model.

Stores all supported UI and voice languages. The Language table acts as
the foreign-key anchor for all i18n translation tables throughout the system.

Supported languages (initial): English (en), Twi (tw)
Extensible to: Hausa (ha), Yoruba (yo), Swahili (sw), French (fr)

See /docs/FunctionalRequirements.md — FR-MLG-001 through FR-MLG-004.
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.symptom_translation import SymptomTranslationModel
    from app.models.recommendation_translation import RecommendationTranslationModel


class LanguageModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Supported UI and voice languages catalogue."""

    __tablename__ = "languages"
    __table_args__ = (
        UniqueConstraint("code", name="uq_languages_code"),
        {"comment": "Supported application languages. Extended via migration, never via seed."},
    )

    # ---- Columns --------------------------------------------------------
    code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="BCP 47 language tag, e.g. 'en', 'tw', 'ha'.",
    )
    name_en: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        comment="Language name in English, e.g. 'English', 'Twi'.",
    )
    name_native: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        comment="Language name in the native script, e.g. 'Twi', 'English'.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        comment="Whether this language is currently enabled in the UI.",
    )
    supports_voice: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        comment="Whether voice input / TTS is supported for this language.",
    )

    # ---- Relationships ---------------------------------------------------
    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        back_populates="preferred_language_ref",
        foreign_keys="UserModel.preferred_language_code",
    )
    symptom_translations: Mapped[List["SymptomTranslationModel"]] = relationship(
        "SymptomTranslationModel",
        back_populates="language",
        cascade="all, delete-orphan",
    )
    recommendation_translations: Mapped[List["RecommendationTranslationModel"]] = relationship(
        "RecommendationTranslationModel",
        back_populates="language",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Language code={self.code!r} name={self.name_en!r}>"
