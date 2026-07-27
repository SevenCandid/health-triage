"""Master Seed Orchestrator.

Invokes all individual seed files sequentially within a transactional boundary.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.seeds.seed_languages import seed_languages
from app.infrastructure.database.seeds.seed_categories import seed_categories
from app.infrastructure.database.seeds.seed_severity_levels import seed_severity_levels
from app.infrastructure.database.seeds.seed_recommendations import seed_recommendations
from app.infrastructure.database.seeds.seed_symptoms import seed_symptoms
from app.infrastructure.database.seeds.seed_questions import seed_questions
from app.infrastructure.database.seeds.seed_question_options import seed_question_options
from app.infrastructure.database.seeds.seed_triage_rules import seed_triage_rules
from app.infrastructure.database.seeds.seed_red_flags import seed_red_flags

logger = logging.getLogger(__name__)


async def seed_all_knowledge_base(session: AsyncSession) -> None:
    """Executes all seed scripts sequentially in the correct order."""
    logger.info("Starting Master Seed execution for Medical Knowledge Base...")
    try:
        await seed_languages(session)
        await seed_categories(session)
        await seed_severity_levels(session)
        await seed_recommendations(session)
        await seed_symptoms(session)
        await seed_questions(session)
        await seed_question_options(session)
        await seed_triage_rules(session)
        await seed_red_flags(session)
        await session.commit()
        logger.info("Master Seed execution completed successfully.")
    except Exception as exc:
        logger.error(f"Master Seed execution failed: {exc}")
        await session.rollback()
        raise
