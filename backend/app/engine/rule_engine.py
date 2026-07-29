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

from app.models.health_conversation import HealthConversationModel, ConversationSymptomModel
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

    def evaluate_conversation(
        self,
        conversation: HealthConversationModel,
        active_symptom: Optional[ConversationSymptomModel],
        all_questions: Dict[str, List[QuestionModel]],
        all_rules: Dict[str, List[TriageRuleModel]],
        all_recommendations: List[RecommendationModel],
    ) -> TriageEvaluationResult:
        """Evaluates the current state of a health conversation across all symptoms.

        Checks for red flags, determines if more questions are needed,
        calculates clinical score, and loads recommendations.

        Args:
            conversation: The active HealthConversation with raw_answers_snapshot loaded.
            active_symptom: The current symptom being actively evaluated/questioned.
            all_questions: Map of symptom_id -> QuestionModel records.
            all_rules: Map of symptom_id -> TriageRuleModel records.
            all_recommendations: Pre-filtered RecommendationModel records.

        Returns:
            A fully populated TriageEvaluationResult aggregated across all symptoms.
        """
        logger.info(f"Evaluating health conversation: {conversation.id}")
        answers: Dict[str, Any] = conversation.raw_answers_snapshot or {}

        # We will aggregate these across all symptoms
        highest_severity_level = 0
        final_severity = UrgencyCode.GREEN
        is_emergency = False
        all_recs = []
        explanations = []

        # Map severities to numeric values to find the maximum
        severity_ranks = {
            UrgencyCode.GREEN: 1,
            UrgencyCode.YELLOW: 2,
            UrgencyCode.ORANGE: 3,
            UrgencyCode.RED: 4,
        }

        # First, see if the active symptom needs more questions.
        # We only ask questions for the active symptom.
        if active_symptom:
            sym_id = active_symptom.symptom_id
            questions = all_questions.get(sym_id, [])
            
            next_q = self.question_engine.determine_next_question(questions, answers)
            if next_q:
                logger.info(f"Conversation incomplete. Next question node: {next_q.node_id!r}")
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

        # If there are no next questions, or no active symptom, we evaluate EVERYTHING.
        concern_ids = set()

        for conv_symp in conversation.symptoms:
            sym_id = conv_symp.symptom_id
            rules = all_rules.get(sym_id, [])

            # 1. Emergency Rules
            emergency_match = self.emergency_engine.evaluate_red_flags(rules, answers)
            if emergency_match:
                logger.warning(f"Red flag trigger match: {emergency_match.rule_name!r}")
                is_emergency = True
                final_severity = UrgencyCode.RED
                highest_severity_level = 4
                if emergency_match.health_concern_id:
                    concern_ids.add(emergency_match.health_concern_id)
                explanations.append(f"[{conv_symp.symptom.name_en}] Emergency: {emergency_match.rule_name}")
                continue

            # 2. Regular Scoring
            severity, matched_rule = self.scoring_engine.calculate_score(rules, answers)
            if matched_rule and matched_rule.health_concern_id:
                concern_ids.add(matched_rule.health_concern_id)
            
            if matched_rule and matched_rule.notes:
                explanations.append(f"[{conv_symp.symptom.name_en}] {matched_rule.notes}")

            # Update highest severity
            rank = severity_ranks.get(severity, 1)
            if rank > highest_severity_level:
                highest_severity_level = rank
                final_severity = severity

        if not explanations:
            explanations.append("Your responses indicate signs that warrant the chosen recommendation to ensure proper health management.")

        # 3. Recommendations
        for concern_id in concern_ids:
            recs = self.recommendation_engine.get_recommendations_for_concern(
                all_recommendations, concern_id
            )
            all_recs.extend(recs)
        
        # Deduplicate recommendations
        unique_recs = []
        for r in all_recs:
            if r not in unique_recs:
                unique_recs.append(r)

        if not unique_recs:
            if is_emergency:
                unique_recs = ["Call emergency services immediately or go to the nearest emergency department."]
            else:
                unique_recs = ["Monitor your symptoms. Seek medical advice if they worsen or persist."]

        # 4. Action Protocol
        protocol = self.decision_engine.get_action_protocol(final_severity)

        return TriageEvaluationResult(
            severity=final_severity,
            recommendations=unique_recs,
            explanation=" | ".join(explanations),
            is_emergency=is_emergency,
            action_protocol=ActionProtocolDTO(**protocol),
            next_question=None,
        )
