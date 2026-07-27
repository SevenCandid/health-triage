"""Scoring Engine module.

Calculates risk score and maps rules to severity levels.

Rules are evaluated in ascending priority_order. The first matching
non-red-flag rule determines the session severity. If no rule matches,
the severity defaults to GREEN (self-care).
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.models.triage_rule import TriageRuleModel
from app.models.severity_level import UrgencyCode
from app.engine.condition_evaluator import evaluate_conditions

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Evaluates triage rules against user responses to assign clinical urgency."""

    def calculate_score(
        self,
        rules: List[TriageRuleModel],
        answers: Dict[str, Any],
    ) -> Tuple[UrgencyCode, Optional[TriageRuleModel]]:
        """Evaluates active non-emergency rules in priority order.

        Args:
            rules: All triage rules for the current symptom (including red-flags,
                   which are filtered out internally).
            answers: Mapping of node_id → answer_value from the session snapshot.

        Returns:
            A tuple of (UrgencyCode, matched_rule).
            Defaults to (UrgencyCode.GREEN, None) if no rule matches.

        Raises:
            RuntimeError: If a matching rule has no loaded severity_level relationship.
                          This indicates the caller did not eagerly load the relationship.
        """
        scoring_rules = sorted(
            [r for r in rules if r.is_active and not r.is_red_flag_override],
            key=lambda r: r.priority_order,
        )

        for rule in scoring_rules:
            if evaluate_conditions(
                conditions_payload=rule.rule_conditions,
                logic_operator=str(rule.logic_operator),
                answers=answers,
            ):
                # Guard: severity_level must be eagerly loaded
                if rule.severity_level is None:
                    raise RuntimeError(
                        f"Rule '{rule.rule_name}' matched but its severity_level "
                        f"relationship is not loaded. Ensure selectinload("
                        f"TriageRuleModel.severity_level) is used when querying rules."
                    )
                severity_code: UrgencyCode = rule.severity_level.code
                logger.info(f"Rule matched: {rule.rule_name!r} → {severity_code}")
                return severity_code, rule

        logger.info("No scoring rule matched — defaulting to GREEN.")
        return UrgencyCode.GREEN, None
