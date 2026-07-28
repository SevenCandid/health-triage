"""Database Seed Script.

Inserts the initial baseline clinical rule tree and a system admin account
so the application is immediately functional after a fresh schema migration.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.database.models import RuleTreeModel
from app.models.user import UserModel
from app.infrastructure.security.password import hash_password

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Baseline rule tree: a minimal, illustrative decision tree structure.
# The real clinical rules will be loaded via the rule engine design in Phase 2.
# See /docs/RuleEngineDesign.md for the full JSON schema specification.
# ---------------------------------------------------------------------------
BASELINE_RULE_TREE: dict = {
    "version": "1.0.0",
    "description": "Baseline triage rule tree - MVP (see RuleEngineDesign.md for full schema)",
    "initialNodeId": "node_chief_complaint",
    "nodes": {
        "node_chief_complaint": {
            "id": "node_chief_complaint",
            "question": {
                "en": "What is your main symptom?",
                "tw": "Dɛn na ehia wo?"
            },
            "redFlagTrigger": False,
            "options": [
                {
                    "label": {"en": "Chest pain", "tw": "Yam yam"},
                    "nextNodeId": "node_chest_pain_qualifier",
                    "terminalResult": None
                },
                {
                    "label": {"en": "Fever", "tw": "Abiyede"},
                    "nextNodeId": "node_fever_qualifier",
                    "terminalResult": None
                },
                {
                    "label": {"en": "Severe bleeding", "tw": "Mogya tu"},
                    "nextNodeId": None,
                    "isRedFlag": True,
                    "terminalResult": {
                        "urgency": "RED",
                        "primaryAction": {
                            "en": "EMERGENCY: Apply direct pressure and call 112 immediately.",
                            "tw": "GYAEGYAE: Ma mogya no ho tumi na frɛ 112 ntɛm ara."
                        },
                        "timeframeHours": 0
                    }
                },
                {
                    "label": {"en": "Other", "tw": "Bɔne foforɔ"},
                    "nextNodeId": None,
                    "terminalResult": {
                        "urgency": "GREEN",
                        "primaryAction": {
                            "en": "Monitor symptoms and visit a clinic if they worsen.",
                            "tw": "Hwɛ wo yareɛ na kɔ asopiti sɛ ɛseɛ."
                        },
                        "timeframeHours": 72
                    }
                }
            ]
        },
        "node_chest_pain_qualifier": {
            "id": "node_chest_pain_qualifier",
            "question": {
                "en": "Is the chest pain accompanied by shortness of breath, arm pain, or sweating?",
                "tw": "Na wo yam yam no ka ho aho mframa, nsa yam, anaasɛ ahuhuro?"
            },
            "redFlagTrigger": True,
            "options": [
                {
                    "label": {"en": "Yes", "tw": "Yiw"},
                    "nextNodeId": None,
                    "isRedFlag": True,
                    "terminalResult": {
                        "urgency": "RED",
                        "primaryAction": {
                            "en": "EMERGENCY: These symptoms may indicate a heart attack. Call 112 now.",
                            "tw": "GYAEGYAE: Yareɛ yi betumi aba koma yareɛ. Frɛ 112 seisei!"
                        },
                        "timeframeHours": 0
                    }
                },
                {
                    "label": {"en": "No", "tw": "Daabi"},
                    "nextNodeId": None,
                    "terminalResult": {
                        "urgency": "ORANGE",
                        "primaryAction": {
                            "en": "Very Urgent: Go to a hospital today for evaluation.",
                            "tw": "NTƐM: Kɔ asopiti nnɛ na wɔnhwɛ wo."
                        },
                        "timeframeHours": 4
                    }
                }
            ]
        },
        "node_fever_qualifier": {
            "id": "node_fever_qualifier",
            "question": {
                "en": "How long have you had the fever?",
                "tw": "Abiyede no abɔ wo mmerɛ ahe?"
            },
            "redFlagTrigger": False,
            "options": [
                {
                    "label": {"en": "More than 3 days", "tw": "Nnɛ mmiɛnsa kyɛ"},
                    "nextNodeId": None,
                    "terminalResult": {
                        "urgency": "YELLOW",
                        "primaryAction": {
                            "en": "Urgent: Visit a clinic today. Stay hydrated.",
                            "tw": "NTƐM: Kɔ asopiti nnɛ. Nom nsuo pii."
                        },
                        "timeframeHours": 24
                    }
                },
                {
                    "label": {"en": "Less than 3 days", "tw": "Nnɛ mmiɛnsa ansa"},
                    "nextNodeId": None,
                    "terminalResult": {
                        "urgency": "GREEN",
                        "primaryAction": {
                            "en": "Non-Urgent: Rest, stay hydrated, and monitor. See a doctor if it worsens.",
                            "tw": "Hom, nom nsuo, na hwɛ wo ho. Kɔ dokita bi so sɛ ɛseɛ."
                        },
                        "timeframeHours": 72
                    }
                }
            ]
        }
    }
}


async def seed_rule_trees(session: AsyncSession) -> None:
    """Seeds the initial baseline clinical rule tree if none exists."""
    result = await session.execute(select(RuleTreeModel).limit(1))
    existing = result.scalar_one_or_none()
    if existing:
        logger.info("Rule trees already seeded — skipping.")
        return

    rule_tree = RuleTreeModel(
        id=str(uuid.uuid4()),
        version=BASELINE_RULE_TREE["version"],
        description=BASELINE_RULE_TREE["description"],
        tree_structure=BASELINE_RULE_TREE,
        is_active=True,
        published_at=datetime.now(timezone.utc),
    )
    session.add(rule_tree)
    await session.commit()
    logger.info(f"Seeded baseline rule tree version={rule_tree.version}")


async def seed_admin_user(session: AsyncSession) -> None:
    """Seeds a default admin/test user account for development."""
    result = await session.execute(
        select(UserModel).where(UserModel.phone_number == "+000000000000")
    )
    existing = result.scalar_one_or_none()
    if existing:
        logger.info("Admin user already seeded — skipping.")
        return

    admin = UserModel(
        id=str(uuid.uuid4()),
        phone_number="+000000000000",
        full_name="System Admin",
        password_hash=hash_password("AdminPass123!"),
        preferred_language_code="en",
        is_active=True,
    )
    session.add(admin)
    await session.commit()
    logger.info(f"Seeded development admin user id={admin.id}")


from app.infrastructure.database.seeds.seed_master import seed_all_knowledge_base


async def run_seeds(session: AsyncSession) -> None:
    """Executes all seed functions in dependency order."""
    logger.info("Running database seed scripts...")
    await seed_rule_trees(session)
    await seed_all_knowledge_base(session)  # seeds languages first
    await seed_admin_user(session)           # needs languages.code='en' to exist
    logger.info("Database seed scripts completed.")

