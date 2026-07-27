"""Seed Script for Symptom Categories."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.symptom_category import SymptomCategoryModel, BodySystem

logger = logging.getLogger(__name__)

CATEGORIES_DATA = [
    {"name_en": "General", "name_tw": "Nipadua mu nyinaa", "slug": "general", "body_system": BodySystem.OTHER, "icon_name": "activity", "display_order": 1, "is_emergency_fast_track": False},
    {"name_en": "Respiratory", "name_tw": "Mframa fa", "slug": "respiratory", "body_system": BodySystem.RESPIRATORY, "icon_name": "wind", "display_order": 2, "is_emergency_fast_track": False},
    {"name_en": "Cardiovascular", "name_tw": "Koma ne mogya akyi", "slug": "cardiovascular", "body_system": BodySystem.CARDIOVASCULAR, "icon_name": "heart", "display_order": 3, "is_emergency_fast_track": False},
    {"name_en": "Digestive", "name_tw": "Yam ne aduane guam", "slug": "digestive", "body_system": BodySystem.GASTROINTESTINAL, "icon_name": "droplet", "display_order": 4, "is_emergency_fast_track": False},
    {"name_en": "Neurological", "name_tw": "Amemene ne ntini", "slug": "neurological", "body_system": BodySystem.NEUROLOGICAL, "icon_name": "brain", "display_order": 5, "is_emergency_fast_track": False},
    {"name_en": "Musculoskeletal", "name_tw": "Nnompe ne ntini", "slug": "musculoskeletal", "body_system": BodySystem.MUSCULOSKELETAL, "icon_name": "accessibility", "display_order": 6, "is_emergency_fast_track": False},
    {"name_en": "Skin", "name_tw": "Wurape", "slug": "skin", "body_system": BodySystem.DERMATOLOGICAL, "icon_name": "sparkles", "display_order": 7, "is_emergency_fast_track": False},
    {"name_en": "Eye", "name_tw": "Ani", "slug": "eye", "body_system": BodySystem.OPHTHALMOLOGICAL, "icon_name": "eye", "display_order": 8, "is_emergency_fast_track": False},
    {"name_en": "Ear, Nose & Throat", "name_tw": "Aso, Hwene ne Mene", "slug": "ent", "body_system": BodySystem.ENT, "icon_name": "volume-2", "display_order": 9, "is_emergency_fast_track": False},
    {"name_en": "Urinary", "name_tw": "Dwonsɔ fa", "slug": "urinary", "body_system": BodySystem.UROLOGICAL, "icon_name": "filter", "display_order": 10, "is_emergency_fast_track": False},
    {"name_en": "Women's Health", "name_tw": "Mmaa apɔwmuden", "slug": "womens-health", "body_system": BodySystem.REPRODUCTIVE, "icon_name": "venus", "display_order": 11, "is_emergency_fast_track": False},
    {"name_en": "Child Health", "name_tw": "Mmofra apɔwmuden", "slug": "child-health", "body_system": BodySystem.OTHER, "icon_name": "baby", "display_order": 12, "is_emergency_fast_track": False},
    {"name_en": "Mental Health", "name_tw": "Adwene mu apɔwmuden", "slug": "mental-health", "body_system": BodySystem.MENTAL_HEALTH, "icon_name": "smile", "display_order": 13, "is_emergency_fast_track": False},
    {"name_en": "Injuries & Emergencies", "name_tw": "Akwanhyia ne Akokoɔduo", "slug": "injuries-emergencies", "body_system": BodySystem.OTHER, "icon_name": "shield-alert", "display_order": 14, "is_emergency_fast_track": True}
]


async def seed_categories(session: AsyncSession) -> None:
    logger.info("Seeding symptom categories...")
    for cat_data in CATEGORIES_DATA:
        result = await session.execute(
            select(SymptomCategoryModel).where(SymptomCategoryModel.slug == cat_data["slug"])
        )
        if not result.scalar_one_or_none():
            cat = SymptomCategoryModel(**cat_data)
            session.add(cat)
    await session.flush()
    logger.info("Symptom categories seeded.")
