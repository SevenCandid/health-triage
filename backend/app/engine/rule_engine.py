"""Rule Engine Coordinator.

Main entry point for coordinating clinical triage rule evaluation.
Delegates to sub-engines to evaluate red flags, determine next questions,
calculate scores, and map recommendation protocols.

Evaluation order:
  1. EmergencyEngine  — red-flag override rules (short-circuits to RED)
  2. QuestionEngine   — determines if more questions are needed
  3. ScoringEngine    — calculates severity from scoring rules
  4. RecommendationEngine — retrieves matching recommendations
  5. DecisionEngine   — maps severity to clinical action protocol
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.models.assessment_session import AssessmentSessionModel
from app.models.question import QuestionModel
from app.models.triage_rule import TriageRuleModel
from app.models.recommendation import RecommendationModel
from app.models.severity_level import UrgencyCode

from app.engine.emergency_engine import EmergencyEngine
from app.engine.question_engine import QuestionEngine
from app.engine.scoring_engine import ScoringEngine
from app.engine.recommendation_engine import RecommendationEngine
from app.engine.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)


class ActionProtocolDTO(BaseModel):
    """Clinical action protocol derived from the evaluated urgency level."""

    action: str
    timeframe_hours: int
    guidance: str


class TriageEvaluationResult(BaseModel):
    """Structured response payload containing the triage evaluation result."""

    severity: UrgencyCode
    recommendations: List[str]
    explanation: str
    is_emergency: bool
    action_protocol: Optional[ActionProtocolDTO] = None
    next_question: Optional[Dict[str, Any]] = None


class RuleEngine:
    """Coordinates the execution of clinical triage evaluation."""

    def __init__(self) -> None:
        self.emergency_engine = EmergencyEngine()
        self.question_engine = QuestionEngine()
        self.scoring_engine = ScoringEngine()
        self.recommendation_engine = RecommendationEngine()
        self.decision_engine = DecisionEngine()

    def evaluate(
        self,
        session: AssessmentSessionModel,
        questions: List[QuestionModel],
        rules: List[TriageRuleModel],
        recommendations: List[RecommendationModel],
    ) -> TriageEvaluationResult:
        """Evaluates the current state of an assessment session.

        Checks for red flags, determines if more questions are needed,
        calculates clinical score, and loads recommendations.

        Args:
            session: The active AssessmentSession with raw_answers_snapshot loaded.
            questions: All QuestionModel records for this symptom (options eagerly loaded).
            rules: All TriageRuleModel records for this symptom (severity_level eagerly loaded).
            recommendations: Pre-filtered RecommendationModel records relevant to this symptom.

        Returns:
            A fully populated TriageEvaluationResult.
        """
        logger.info(f"Evaluating triage session: {session.id}")
        answers: Dict[str, Any] = session.raw_answers_snapshot or {}

        # -------------------------------------------------------------------
        # 1. Evaluate Emergency Override Rules (short-circuit on red flag)
        # -------------------------------------------------------------------
        emergency_match = self.emergency_engine.evaluate_red_flags(rules, answers)
        if emergency_match:
            logger.warning(f"Red flag trigger match: {emergency_match.rule_name!r}")
            recs = self.recommendation_engine.get_recommendations_for_concern(
                recommendations, emergency_match.health_concern_id
            )
            protocol = self.decision_engine.get_action_protocol(UrgencyCode.RED)
            return TriageEvaluationResult(
                severity=UrgencyCode.RED,
                recommendations=recs or [
                    "Call emergency services immediately or go to the nearest emergency department."
                ],
                explanation=(
                    f"Emergency Triggered: {emergency_match.rule_name}. "
                    f"{emergency_match.notes or ''}"
                ).strip(),
                is_emergency=True,
                action_protocol=ActionProtocolDTO(**protocol),
                next_question=None,
            )

        # -------------------------------------------------------------------
        # 2. Check for next unanswered question
        # -------------------------------------------------------------------
        next_q = self.question_engine.determine_next_question(questions, answers)
        if next_q:
            logger.info(f"Assessment incomplete. Next question node: {next_q.node_id!r}")
            return TriageEvaluationResult(
                severity=UrgencyCode.GREEN,
                recommendations=["Please answer the follow-up questions to complete triage."],
                explanation="Triage in progress. More information required.",
                is_emergency=False,
                action_protocol=None,
                next_question={
                    "id": next_q.id,
                    "node_id": next_q.node_id,
                    "question_text_en": next_q.question_text_en,
                    "question_text_tw": next_q.question_text_tw,
                    "question_type": next_q.question_type.value,
                    "options": [
                        {
                            "id": opt.id,
                            "option_value": opt.option_value,
                            "label_en": opt.label_en,
                            "label_tw": opt.label_tw,
                        }
                        for opt in next_q.options
                    ],
                },
            )

        # -------------------------------------------------------------------
        # 3. Calculate regular triage score
        # -------------------------------------------------------------------
        severity, matched_rule = self.scoring_engine.calculate_score(rules, answers)
        concern_id = matched_rule.health_concern_id if matched_rule else None
        explanation = (
            matched_rule.notes
            if (matched_rule and matched_rule.notes)
            else "Symptom evaluation completed."
        )

        # -------------------------------------------------------------------
        # 4. Retrieve recommendations for the matched health concern
        # -------------------------------------------------------------------
        recs = self.recommendation_engine.get_recommendations_for_concern(
            recommendations, concern_id
        )
        if not recs:
            recs = ["Monitor your symptoms. Seek medical advice if they worsen or persist."]

        # -------------------------------------------------------------------
        # 5. Map severity to clinical action protocol
        # -------------------------------------------------------------------
        protocol = self.decision_engine.get_action_protocol(severity)

        return TriageEvaluationResult(
            severity=severity,
            recommendations=recs,
            explanation=explanation,
            is_emergency=(severity == UrgencyCode.RED),
            action_protocol=ActionProtocolDTO(**protocol),
            next_question=None,
        )
