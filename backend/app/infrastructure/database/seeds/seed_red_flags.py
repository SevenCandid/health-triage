"""Seed Script for Triage Red Flags and Override Rules."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.symptom import SymptomModel
from app.models.severity_level import SeverityLevelModel, UrgencyCode
from app.models.health_concern import HealthConcernModel
from app.models.triage_rule import TriageRuleModel, RuleLogicOperator

logger = logging.getLogger(__name__)

RED_FLAG_RULES = [
    # Severe bleeding red flag
    {
        "symptom_slug": "severe-bleeding",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "severe-respiratory-distress",  # fallback or linked concern
        "rule_name": "Uncontrolled Active Bleeding",
        "rule_conditions": [],  # Empty means matches immediately
        "is_red_flag_override": True,
        "priority_order": 1
    },
    # Chest pain with associated symptoms red flag
    {
        "symptom_slug": "chest-pain",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "cardiac-emergency",
        "rule_name": "Chest Pain with Associated Cardiac Red Flags",
        "rule_conditions": [
            {
                "node_id": "cp_associated_symptoms",
                "answer_value": "true",
                "negated": False
            }
        ],
        "is_red_flag_override": True,
        "priority_order": 1
    },
    # Paediatric fever red flag
    {
        "symptom_slug": "fever",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "severe-respiratory-distress",  # linked general emergency concern
        "rule_name": "Infant High Fever (Under 3 Months)",
        "rule_conditions": [
            {
                "node_id": "fv_infant_check",
                "answer_value": "true",
                "negated": False
            }
        ],
        "is_red_flag_override": True,
        "priority_order": 1
    }
]


async def seed_red_flags(session: AsyncSession) -> None:
    logger.info("Seeding emergency red-flag override rules...")
    for rule_data in RED_FLAG_RULES:
        sym_res = await session.execute(
            select(SymptomModel).where(SymptomModel.slug == rule_data["symptom_slug"])
        )
        sym = sym_res.scalar_one_or_none()
        if not sym:
            continue

        sev_res = await session.execute(
            select(SeverityLevelModel).where(SeverityLevelModel.code == rule_data["severity_code"])
        )
        sev = sev_res.scalar_one_or_none()
        if not sev:
            continue

        concern_res = await session.execute(
            select(HealthConcernModel).where(HealthConcernModel.slug == rule_data["concern_slug"])
        )
        concern = concern_res.scalar_one_or_none()
        concern_id = concern.id if concern else None

        res = await session.execute(
            select(TriageRuleModel).where(
                TriageRuleModel.symptom_id == sym.id,
                TriageRuleModel.rule_name == rule_data["rule_name"]
            )
        )
        if not res.scalar_one_or_none():
            rule = TriageRuleModel(
                symptom_id=sym.id,
                severity_level_id=sev.id,
                health_concern_id=concern_id,
                rule_name=rule_data["rule_name"],
                rule_conditions=rule_data["rule_conditions"],
                logic_operator=RuleLogicOperator.AND,
                priority_order=rule_data["priority_order"],
                is_red_flag_override=rule_data["is_red_flag_override"],
                is_active=True
            )
            session.add(rule)
    await session.flush()
    logger.info("Emergency red-flag override rules seeded.")
