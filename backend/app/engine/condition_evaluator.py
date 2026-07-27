"""Condition Evaluator — Shared Engine Utility.

Provides the canonical rule condition matching logic used by both
EmergencyEngine and ScoringEngine to avoid code duplication.

A condition object has the shape:
    {
        "node_id": str,        # The question node ID
        "answer_value": str,   # The expected answer value
        "negated": bool        # If True, the match is inverted
    }

Logic:
  - If no conditions exist → the rule is a catch-all and always matches.
  - Multiple conditions use AND (all must match) or OR (any must match)
    based on the rule's logic_operator field.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def evaluate_conditions(
    conditions_payload: Any,
    logic_operator: str,
    answers: Dict[str, Any],
) -> bool:
    """Evaluates a rule's condition set against a patient's answers.

    Args:
        conditions_payload: The raw rule_conditions value from the DB.
            Can be a dict with a "conditions" key, a list of condition
            dicts, or None/empty (catch-all).
        logic_operator: "AND" or "OR" — how multiple conditions are combined.
        answers: Mapping of node_id → answer_value from the session snapshot.

    Returns:
        True if the conditions are satisfied, False otherwise.
    """
    # Normalise the conditions payload into a flat list
    if not conditions_payload:
        return True  # Catch-all rule — matches every time

    if isinstance(conditions_payload, dict) and "conditions" in conditions_payload:
        cond_list: List[Dict[str, Any]] = conditions_payload["conditions"]
    elif isinstance(conditions_payload, list):
        cond_list = conditions_payload
    else:
        cond_list = []

    if not cond_list:
        return True  # Empty list is still a catch-all

    matches: List[bool] = []
    for cond in cond_list:
        node_id: str = cond.get("node_id", "")
        target_val: str = str(cond.get("answer_value", "")).lower()
        negated: bool = bool(cond.get("negated", False))

        if node_id not in answers:
            matched = False
        else:
            user_val = str(answers[node_id]).lower()
            matched = user_val == target_val

        if negated:
            matched = not matched

        matches.append(matched)
        logger.debug(
            f"Condition eval: node={node_id!r} target={target_val!r} "
            f"negated={negated} matched={matched}"
        )

    if str(logic_operator).upper() == "OR":
        return any(matches)
    return all(matches)
