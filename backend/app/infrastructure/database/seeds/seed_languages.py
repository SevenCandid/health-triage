"""Seed Script for Languages."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.language import LanguageModel

logger = logging.getLogger(__name__)

LANGUAGES_DATA = [
    {
        "code": "en",
        "name_en": "English",
        "name_native": "English",
        "is_active": True,
        "supports_voice": True,
    },
    {
        "code": "tw",
        "name_en": "Twi",
        "name_native": "Akan (Twi)",
        "is_active": True,
        "supports_voice": True,
    }
]


async def seed_languages(session: AsyncSession) -> None:
    logger.info("Seeding languages...")
    for lang_data in LANGUAGES_DATA:
        result = await session.execute(
            select(LanguageModel).where(LanguageModel.code == lang_data["code"])
        )
        if not result.scalar_one_or_none():
            lang = LanguageModel(**lang_data)
            session.add(lang)
    await session.flush()
    logger.info("Languages seeded successfully.")
