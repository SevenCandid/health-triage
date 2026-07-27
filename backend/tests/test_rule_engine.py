"""Unit tests for the Clinical Rule Engine components.

Covers:
- Normal assessment flow
- Emergency red-flag override
- Invalid input / Session not found
- Missing answers / next question identification
- Rule conflicts & priority ordering
"""

import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timezone

from app.models.assessment_session import AssessmentSessionModel, SessionStatus
from app.models.symptom import SymptomModel, SymptomSeverityHint
from app.models.question import QuestionModel, QuestionType
from app.models.question_option import QuestionOptionModel
from app.models.triage_rule import TriageRuleModel, RuleLogicOperator
from app.models.severity_level import SeverityLevelModel, UrgencyCode
from app.models.recommendation import RecommendationModel, RecommendationType
from app.models.health_concern import HealthConcernModel

from app.engine.rule_engine import RuleEngine
from app.engine.emergency_engine import EmergencyEngine
from app.engine.question_engine import QuestionEngine
from app.engine.scoring_engine import ScoringEngine
from app.engine.recommendation_engine import RecommendationEngine
from app.services.triage_service import TriageService


@pytest.fixture
def mock_symptom():
    return SymptomModel(
        id=str(uuid.uuid4()),
        category_id=str(uuid.uuid4()),
        slug="chest-pain",
        name_en="Chest Pain",
        severity_hint=SymptomSeverityHint.CRITICAL,
        is_red_flag=False
    )


@pytest.fixture
def mock_questions(mock_symptom):
    q1 = QuestionModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        node_id="cp_duration",
        question_text_en="How long have you had chest pain?",
        question_type=QuestionType.SINGLE_SELECT,
        order_index=1,
        options=[
            QuestionOptionModel(
                id=str(uuid.uuid4()),
                option_value="less_than_24h",
                label_en="Less than 24h",
                order_index=1
            )
        ]
    )
    q2 = QuestionModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        node_id="cp_breathlessness",
        question_text_en="Do you have shortness of breath?",
        question_type=QuestionType.BOOLEAN,
        order_index=2,
        options=[]
    )
    return [q1, q2]


@pytest.fixture
def mock_severity_levels():
    return {
        UrgencyCode.RED: SeverityLevelModel(id=str(uuid.uuid4()), code=UrgencyCode.RED, label_en="Emergency", badge_color_hex="#FF0000", timeframe_minutes=0),
        UrgencyCode.ORANGE: SeverityLevelModel(id=str(uuid.uuid4()), code=UrgencyCode.ORANGE, label_en="High Urgency", badge_color_hex="#FFA500", timeframe_minutes=60),
        UrgencyCode.GREEN: SeverityLevelModel(id=str(uuid.uuid4()), code=UrgencyCode.GREEN, label_en="Low Urgency", badge_color_hex="#00FF00", timeframe_minutes=4320),
    }


@pytest.fixture
def mock_concern(mock_severity_levels):
    return HealthConcernModel(
        id=str(uuid.uuid4()),
        slug="cardiac-event",
        name_en="Possible Cardiac Event",
        severity_level_id=mock_severity_levels[UrgencyCode.RED].id
    )


@pytest.fixture
def mock_rules(mock_symptom, mock_severity_levels, mock_concern):
    r_red_flag = TriageRuleModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        severity_level_id=mock_severity_levels[UrgencyCode.RED].id,
        severity_level=mock_severity_levels[UrgencyCode.RED],
        health_concern_id=mock_concern.id,
        rule_name="Red Flag: Chest Pain + Breathlessness",
        rule_conditions=[{"node_id": "cp_breathlessness", "answer_value": "true"}],
        logic_operator=RuleLogicOperator.AND,
        priority_order=1,
        is_red_flag_override=True,
        is_active=True
    )
    r_normal_high = TriageRuleModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        severity_level_id=mock_severity_levels[UrgencyCode.ORANGE].id,
        severity_level=mock_severity_levels[UrgencyCode.ORANGE],
        health_concern_id=mock_concern.id,
        rule_name="Recent Chest Pain",
        rule_conditions=[{"node_id": "cp_duration", "answer_value": "less_than_24h"}],
        logic_operator=RuleLogicOperator.AND,
        priority_order=10,
        is_red_flag_override=False,
        is_active=True
    )
    r_conflict_low = TriageRuleModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        severity_level_id=mock_severity_levels[UrgencyCode.GREEN].id,
        severity_level=mock_severity_levels[UrgencyCode.GREEN],
        health_concern_id=mock_concern.id,
        rule_name="Conflicting Low Priority Rule",
        rule_conditions=[{"node_id": "cp_duration", "answer_value": "less_than_24h"}],
        logic_operator=RuleLogicOperator.AND,
        priority_order=50,
        is_red_flag_override=False,
        is_active=True
    )
    return [r_red_flag, r_normal_high, r_conflict_low]


@pytest.fixture
def mock_recommendations(mock_concern):
    return [
        RecommendationModel(
            id=str(uuid.uuid4()),
            health_concern_id=mock_concern.id,
            recommendation_type=RecommendationType.PRIMARY_ACTION,
            content_en="Call 112 immediately for emergency evaluation.",
            is_active=True
        )
    ]


def test_emergency_override(mock_symptom, mock_questions, mock_rules, mock_recommendations):
    """Test emergency red-flag override when breathlessness is true."""
    engine = RuleEngine()
    session = AssessmentSessionModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        raw_answers_snapshot={"cp_duration": "less_than_24h", "cp_breathlessness": "true"}
    )

    result = engine.evaluate(session, mock_questions, mock_rules, mock_recommendations)

    assert result.is_emergency is True
    assert result.severity == UrgencyCode.RED
    assert "Red Flag" in result.explanation
    assert len(result.recommendations) > 0
    assert result.next_question is None


def test_missing_answers_returns_next_question(mock_symptom, mock_questions, mock_rules, mock_recommendations):
    """Test that missing answers returns the next unanswered question."""
    engine = RuleEngine()
    session = AssessmentSessionModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        raw_answers_snapshot={}  # No answers provided yet
    )

    result = engine.evaluate(session, mock_questions, mock_rules, mock_recommendations)

    assert result.is_emergency is False
    assert result.next_question is not None
    assert result.next_question["node_id"] == "cp_duration"


def test_normal_assessment(mock_symptom, mock_questions, mock_rules, mock_recommendations):
    """Test normal assessment when all questions answered without red flags."""
    engine = RuleEngine()
    session = AssessmentSessionModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        raw_answers_snapshot={"cp_duration": "less_than_24h", "cp_breathlessness": "false"}
    )

    result = engine.evaluate(session, mock_questions, mock_rules, mock_recommendations)

    assert result.is_emergency is False
    assert result.severity == UrgencyCode.ORANGE
    assert result.next_question is None


def test_rule_conflict_resolution(mock_symptom, mock_questions, mock_rules, mock_recommendations):
    """Test that when two rules match, the one with lower priority_order (higher precedence) wins."""
    engine = RuleEngine()
    # Rules list has priority 10 (ORANGE) and priority 50 (GREEN), both matching cp_duration = less_than_24h
    session = AssessmentSessionModel(
        id=str(uuid.uuid4()),
        symptom_id=mock_symptom.id,
        raw_answers_snapshot={"cp_duration": "less_than_24h", "cp_breathlessness": "false"}
    )

    result = engine.evaluate(session, mock_questions, mock_rules, mock_recommendations)

    assert result.severity == UrgencyCode.ORANGE


@pytest.mark.asyncio
async def test_invalid_input_session_not_found(db_session):
    """Test async TriageService handling invalid assessment_session_id."""
    service = TriageService(db_session)
    fake_id = str(uuid.uuid4())

    with pytest.raises(ValueError, match="not found"):
        await service.evaluate_assessment_session(fake_id)
