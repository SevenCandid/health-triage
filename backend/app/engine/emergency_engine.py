"""Emergency Engine module.

Evaluates red-flag override rules before standard triage scoring logic.
If any red-flag rule matches, evaluation short-circuits immediately and
returns EMERGENCY (RED) severity — no further scoring is performed.
"""

import logging
from typing import Any, Dict, List, Optional

from app.models.triage_rule import TriageRuleModel
from app.engine.condition_evaluator import evaluate_conditions

logger = logging.getLogger(__name__)


class EmergencyEngine:
    """Evaluates high-priority emergency red flag rules."""

    def evaluate_red_flags(
        self,
        rules: List[TriageRuleModel],
        answers: Dict[str, Any],
    ) -> Optional[TriageRuleModel]:
        """Evaluates active red-flag override rules against patient answers.

        Rules are evaluated in ascending priority_order (lowest number first).
        The first matching red-flag rule is returned immediately.

        Returns:
            The matching TriageRuleModel if any red flag is triggered, else None.
        """
        red_flag_rules = sorted(
            [r for r in rules if r.is_active and r.is_red_flag_override],
            key=lambda r: r.priority_order,
        )

        for rule in red_flag_rules:
            if evaluate_conditions(
                conditions_payload=rule.rule_conditions,
                logic_operator=str(rule.logic_operator),
                answers=answers,
            ):
                logger.warning(f"Red-flag rule matched: {rule.rule_name!r}")
                return rule

        return None
