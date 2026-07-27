"""Seed Script for Severity Levels."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.severity_level import SeverityLevelModel, UrgencyCode

logger = logging.getLogger(__name__)

SEVERITY_LEVELS_DATA = [
    {
        "code": UrgencyCode.GREEN,
        "label_en": "Low Urgency",
        "label_tw": "Yareɛ Ketewa",
        "description_en": "Non-urgent symptoms. Can typically be managed with self-care or standard clinic visits.",
        "badge_color_hex": "#10B981",
        "timeframe_minutes": 4320,  # 72 hours
        "requires_emergency_dispatch": False,
        "display_order": 4
    },
    {
        "code": UrgencyCode.YELLOW,
        "label_en": "Medium Urgency",
        "label_tw": "Yareɛ a Ɛhĩa Mmoa",
        "description_en": "Urgent symptoms. We recommend consulting a healthcare provider within 24 hours.",
        "badge_color_hex": "#F59E0B",
        "timeframe_minutes": 1440,  # 24 hours
        "requires_emergency_dispatch": False,
        "display_order": 3
    },
    {
        "code": UrgencyCode.ORANGE,
        "label_en": "High Urgency",
        "label_tw": "Yareɛ a Ɛho Hĩa Ntɛm",
        "description_en": "Very urgent symptoms. Seek immediate hospital evaluation or consult clinical staff within 60 minutes.",
        "badge_color_hex": "#F97316",
        "timeframe_minutes": 60,
        "requires_emergency_dispatch": False,
        "display_order": 2
    },
    {
        "code": UrgencyCode.RED,
        "label_en": "Emergency",
        "label_tw": "Akokoɔduo / Gyaegyae",
        "description_en": "Life-threatening emergency. Immediate intervention, call emergency services or go to ER.",
        "badge_color_hex": "#EF4444",
        "timeframe_minutes": 0,
        "requires_emergency_dispatch": True,
        "display_order": 1
    }
]


async def seed_severity_levels(session: AsyncSession) -> None:
    logger.info("Seeding severity levels...")
    for level_data in SEVERITY_LEVELS_DATA:
        result = await session.execute(
            select(SeverityLevelModel).where(SeverityLevelModel.code == level_data["code"])
        )
        if not result.scalar_one_or_none():
            lvl = SeverityLevelModel(**level_data)
            session.add(lvl)
    await session.flush()
    logger.info("Severity levels seeded.")
