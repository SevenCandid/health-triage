"""Seed Script for Health Concerns and Recommendations."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.severity_level import SeverityLevelModel, UrgencyCode
from app.models.health_concern import HealthConcernModel
from app.models.recommendation import RecommendationModel, RecommendationType
from app.models.recommendation_translation import RecommendationTranslationModel
from app.models.language import LanguageModel

logger = logging.getLogger(__name__)

CONCERNS_DATA = [
    {
        "slug": "cardiac-emergency",
        "severity_code": UrgencyCode.RED,
        "name_en": "Possible Cardiac Emergency",
        "name_tw": "Koma Yareɛ Akokoɔduo",
        "description_en": "Symptoms highly suggestive of acute myocardial infarction (heart attack) or unstable arrhythmia.",
        "requires_emergency_dispatch": True,
        "icd10_code": "I21.9",
        "recommendations": [
            {
                "type": RecommendationType.PRIMARY_ACTION,
                "content_en": "Call emergency services (112 or local equivalent) immediately. Do not drive yourself to the hospital.",
                "translations": {"tw": "Frɛ gyaegyae dwumadibea ntɛm ara (112). Nka adadam kɔ asopiti wo ara."}
            },
            {
                "type": RecommendationType.FIRST_AID_STEP,
                "content_en": "Sit down, rest, and try to remain calm. Chew a standard aspirin tablet if you are not allergic.",
                "translations": {"tw": "Tena ase, hom, na boa wo ho. We aspirin adaka baako sɛ wo nni ho yareɛ biara."}
            }
        ]
    },
    {
        "slug": "severe-respiratory-distress",
        "severity_code": UrgencyCode.RED,
        "name_en": "Severe Respiratory Distress",
        "name_tw": "Mframa-Gye ho Ahohiahia",
        "description_en": "Inability to breathe, use of accessory muscles, or cyanosis.",
        "requires_emergency_dispatch": True,
        "icd10_code": "J96.0",
        "recommendations": [
            {
                "type": RecommendationType.PRIMARY_ACTION,
                "content_en": "Seek immediate emergency care. Sit upright and loosen tight clothing.",
                "translations": {"tw": "Hwehwɛ emergency mmoa ntɛm. Tena tee na looso wo ntar a ɛmu yɛ den."}
            }
        ]
    },
    {
        "slug": "general-fever-mild",
        "severity_code": UrgencyCode.GREEN,
        "name_en": "Mild Fever",
        "name_tw": "Abiyedeɛ Ketewa",
        "description_en": "Elevated temperature under 38.5C without red flags.",
        "requires_emergency_dispatch": False,
        "icd10_code": "R50.9",
        "recommendations": [
            {
                "type": RecommendationType.SELF_CARE,
                "content_en": "Rest, drink plenty of fluids, and monitor your temperature.",
                "translations": {"tw": "Hom na nom nsuo pii, na hwɛ sɛnea wo nipadua ho hyeɛ teɛ."}
            }
        ]
    }
]


async def seed_recommendations(session: AsyncSession) -> None:
    logger.info("Seeding health concerns and recommendations...")
    for concern_data in CONCERNS_DATA:
        # Fetch severity level
        sev_result = await session.execute(
            select(SeverityLevelModel).where(SeverityLevelModel.code == concern_data["severity_code"])
        )
        sev_level = sev_result.scalar_one_or_none()
        if not sev_level:
            continue

        result = await session.execute(
            select(HealthConcernModel).where(HealthConcernModel.slug == concern_data["slug"])
        )
        concern = result.scalar_one_or_none()
        if not concern:
            concern = HealthConcernModel(
                slug=concern_data["slug"],
                name_en=concern_data["name_en"],
                name_tw=concern_data["name_tw"],
                description_en=concern_data["description_en"],
                requires_emergency_dispatch=concern_data["requires_emergency_dispatch"],
                icd10_code=concern_data["icd10_code"],
                severity_level_id=sev_level.id
            )
            session.add(concern)
            await session.flush()

        for rec_data in concern_data["recommendations"]:
            rec_result = await session.execute(
                select(RecommendationModel).where(
                    RecommendationModel.health_concern_id == concern.id,
                    RecommendationModel.recommendation_type == rec_data["type"],
                    RecommendationModel.content_en == rec_data["content_en"]
                )
            )
            if not rec_result.scalar_one_or_none():
                rec = RecommendationModel(
                    health_concern_id=concern.id,
                    recommendation_type=rec_data["type"],
                    content_en=rec_data["content_en"],
                    is_active=True
                )
                session.add(rec)
                await session.flush()

                # Translation
                for lang_code, trans_text in rec_data.get("translations", {}).items():
                    trans = RecommendationTranslationModel(
                        recommendation_id=rec.id,
                        language_code=lang_code,
                        content=trans_text
                    )
                    session.add(trans)
    await session.flush()
    logger.info("Health concerns and recommendations seeded.")
