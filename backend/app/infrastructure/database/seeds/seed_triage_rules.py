"""Seed Script for Triage Rules (Scoring logic)."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.symptom import SymptomModel
from app.models.severity_level import SeverityLevelModel, UrgencyCode
from app.models.triage_rule import TriageRuleModel, RuleLogicOperator
from app.models.health_concern import HealthConcernModel

logger = logging.getLogger(__name__)

# Basic rules to catch non-red-flag severities
TRIAGE_RULES = [
    # Headache rules
    {
        "symptom_slug": "headache",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "general-fever-mild",
        "rule_name": "Thunderclap Headache",
        "rule_conditions": [{"node_id": "ha_onset", "answer_value": "sudden", "negated": False}],
        "priority_order": 1
    },
    {
        "symptom_slug": "headache",
        "severity_code": UrgencyCode.ORANGE,
        "concern_slug": "general-fever-mild",
        "rule_name": "Severe Headache",
        "rule_conditions": [{"node_id": "ha_severity", "answer_value": "severe", "negated": False}],
        "priority_order": 2
    },
    {
        "symptom_slug": "headache",
        "severity_code": UrgencyCode.YELLOW,
        "concern_slug": "general-fever-mild",
        "rule_name": "Moderate Headache",
        "rule_conditions": [{"node_id": "ha_severity", "answer_value": "moderate", "negated": False}],
        "priority_order": 3
    },

    # Cough rules
    {
        "symptom_slug": "cough",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "severe-respiratory-distress",
        "rule_name": "Coughing Blood",
        "rule_conditions": [{"node_id": "co_blood", "answer_value": "yes", "negated": False}],
        "priority_order": 1
    },
    {
        "symptom_slug": "cough",
        "severity_code": UrgencyCode.ORANGE,
        "concern_slug": "severe-respiratory-distress",
        "rule_name": "Chronic Cough",
        "rule_conditions": [{"node_id": "co_duration", "answer_value": "more_than_8_weeks", "negated": False}],
        "priority_order": 2
    },

    # Fever rules
    {
        "symptom_slug": "fever",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "general-fever-mild",
        "rule_name": "High Fever with Confusion",
        "rule_conditions": [
            {"node_id": "fv_temp", "answer_value": "high", "negated": False},
            {"node_id": "fv_other", "answer_value": "confusion", "negated": False}
        ],
        "priority_order": 1
    },
    {
        "symptom_slug": "fever",
        "severity_code": UrgencyCode.ORANGE,
        "concern_slug": "general-fever-mild",
        "rule_name": "High Fever",
        "rule_conditions": [{"node_id": "fv_temp", "answer_value": "high", "negated": False}],
        "priority_order": 2
    },
    
    # Abdominal Pain rules
    {
        "symptom_slug": "abdominal-pain",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "general-fever-mild",
        "rule_name": "Severe RLQ Pain",
        "rule_conditions": [
            {"node_id": "ap_location", "answer_value": "right_lower", "negated": False},
            {"node_id": "ap_severity", "answer_value": "severe", "negated": False}
        ],
        "priority_order": 1
    },
    
    # Palpitations
    {
        "symptom_slug": "palpitations",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "cardiac-emergency",
        "rule_name": "Constant Palpitations",
        "rule_conditions": [{"node_id": "pa_duration", "answer_value": "constant", "negated": False}],
        "priority_order": 1
    },
    
    # Shortness of Breath
    {
        "symptom_slug": "shortness-of-breath",
        "severity_code": UrgencyCode.RED,
        "concern_slug": "severe-respiratory-distress",
        "rule_name": "Sudden SOB at Rest",
        "rule_conditions": [
            {"node_id": "sob_onset", "answer_value": "sudden", "negated": False},
            {"node_id": "sob_rest", "answer_value": "yes", "negated": False}
        ],
        "priority_order": 1
    }
]

async def seed_triage_rules(session: AsyncSession) -> None:
    logger.info("Seeding general triage rules...")
    count = 0
    for rule_data in TRIAGE_RULES:
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
                is_red_flag_override=False,
                is_active=True
            )
            session.add(rule)
            count += 1
    await session.flush()
    logger.info(f"General triage rules seeded: {count} new records added.")
