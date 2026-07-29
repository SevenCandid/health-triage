"""Async Triage Service for executing full rule-engine evaluation against database entities.

Architecture Note:
  This service holds a raw AsyncSession to perform all queries directly.
  A future refactor should introduce IAssessmentSessionRepository to fully
  decouple the service from the ORM (see audit report P1).
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment_session import AssessmentSessionModel, SessionStatus, ConsultationMode
from app.models.assessment_response import AssessmentResponseModel
from app.models.symptom import SymptomModel
from app.models.question import QuestionModel
from app.models.triage_rule import TriageRuleModel
from app.models.recommendation import RecommendationModel
from app.models.severity_level import SeverityLevelModel
from app.infrastructure.database.models import RuleTreeModel

from app.engine.rule_engine import RuleEngine, TriageEvaluationResult

logger = logging.getLogger(__name__)


class TriageService:
    """Service layer that manages assessment session lifecycles and invokes RuleEngine."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.session = db_session
        self.engine = RuleEngine()

    async def start_session(
        self,
        language_code: str = "en",
        consultation_mode: ConsultationMode = ConsultationMode.TEXT,
        created_offline: bool = False,
        user_id: Optional[str] = None
    ) -> tuple[AssessmentSessionModel, Optional[str]]:
        """Creates and persists a new assessment session."""
        logger.info(f"Starting new assessment session. Mode: {consultation_mode}, Lang: {language_code}")
        
        pending_symptom = None
        pending_symptom_slug = None
        if user_id:
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_sess_res = await self.session.execute(
                select(AssessmentSessionModel)
                .where(
                    AssessmentSessionModel.user_id == user_id,
                    AssessmentSessionModel.conducted_at >= seven_days_ago,
                    AssessmentSessionModel.symptom_id.isnot(None),
                    AssessmentSessionModel.is_deleted == False
                )
                .order_by(AssessmentSessionModel.conducted_at.desc())
                .limit(1)
            )
            recent_sess = recent_sess_res.scalar_one_or_none()
            if recent_sess and recent_sess.symptom_id:
                sym_res = await self.session.execute(
                    select(SymptomModel).where(SymptomModel.id == recent_sess.symptom_id)
                )
                sym = sym_res.scalar_one_or_none()
                if sym:
                    pending_symptom = sym.name_en
                    pending_symptom_slug = sym.slug
                    pending_session_id = recent_sess.id

        sess = AssessmentSessionModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            status=SessionStatus.ACTIVE,
            consultation_mode=consultation_mode,
            language_code=language_code,
            created_offline=created_offline,
            conducted_at=datetime.now(timezone.utc),
            raw_answers_snapshot={}
        )
        self.session.add(sess)
        await self.session.flush()
        await self.session.refresh(sess)
        return sess, pending_symptom, pending_symptom_slug, pending_session_id

    async def set_symptoms(
        self,
        session_id: str,
        symptom_slug: str
    ) -> tuple[AssessmentSessionModel, SymptomModel, TriageEvaluationResult]:
        """Sets the primary symptom for an active assessment session and runs initial evaluation."""
        logger.info(f"Setting symptom '{symptom_slug}' for session {session_id}")        
        sess_res = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == session_id,
                AssessmentSessionModel.is_deleted == False,  # noqa: E712
            )
        )
        sess = sess_res.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Assessment session '{session_id}' not found.")

        sym_res = await self.session.execute(
            select(SymptomModel).where(SymptomModel.slug == symptom_slug)
        )
        sym = sym_res.scalar_one_or_none()
        if not sym:
            raise ValueError(f"Symptom '{symptom_slug}' not found.")

        sess.symptom_id = sym.id
        await self.session.flush()

        eval_result = await self.evaluate_assessment_session(session_id)
        return sess, sym, eval_result

    async def record_answer(
        self,
        session_id: str,
        node_id: str,
        answer_value: str,
        answer_raw_text: Optional[str] = None
    ) -> tuple[AssessmentSessionModel, TriageEvaluationResult]:
        """Records a user answer to a question node and re-evaluates the session."""
        logger.info(f"Recording answer node '{node_id}'='{answer_value}' for session {session_id}")
        sess_res = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == session_id,
                AssessmentSessionModel.is_deleted == False,  # noqa: E712
            )
        )
        sess = sess_res.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Assessment session '{session_id}' not found.")

        if not sess.symptom_id:
            raise ValueError(f"Assessment session '{session_id}' has no primary symptom set.")

        snapshot = dict(sess.raw_answers_snapshot or {})
        snapshot[node_id] = answer_value
        sess.raw_answers_snapshot = snapshot

        # Also store individual AssessmentResponse entry
        q_res = await self.session.execute(
            select(QuestionModel).where(
                QuestionModel.symptom_id == sess.symptom_id,
                QuestionModel.node_id == node_id
            )
        )
        q = q_res.scalar_one_or_none()

        response_entry = AssessmentResponseModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            question_id=q.id if q else None,
            node_id=node_id,
            answer_value=answer_value,
            answer_raw_text=answer_raw_text,
            answered_at=datetime.now(timezone.utc)
        )
        self.session.add(response_entry)
        await self.session.flush()

        eval_result = await self.evaluate_assessment_session(session_id)
        return sess, eval_result

    async def get_progress(self, session_id: str) -> tuple[AssessmentSessionModel, int]:
        """Retrieves session progress and count of recorded answers."""
        sess_res = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == session_id,
                AssessmentSessionModel.is_deleted == False,  # noqa: E712
            )
        )
        sess = sess_res.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Assessment session '{session_id}' not found.")

        answers_count = len(sess.raw_answers_snapshot or {})
        return sess, answers_count

    async def get_result(self, session_id: str) -> tuple[AssessmentSessionModel, TriageEvaluationResult]:
        """Loads and calculates the current or final result of a session."""
        sess_res = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == session_id,
                AssessmentSessionModel.is_deleted == False,  # noqa: E712
            )
        )
        sess = sess_res.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Assessment session '{session_id}' not found.")

        if not sess.symptom_id:
            raise ValueError(f"Assessment session '{session_id}' has no primary symptom set.")

        eval_result = await self.evaluate_assessment_session(session_id)
        return sess, eval_result

    async def restart_session(self, session_id: str) -> AssessmentSessionModel:
        """Restarts an assessment session by creating a new session with identical parameters."""
        logger.info(f"Restarting assessment session {session_id}")
        sess_res = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == session_id,
                AssessmentSessionModel.is_deleted == False,  # noqa: E712
            )
        )
        sess = sess_res.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Assessment session '{session_id}' not found.")

        # Mark previous session as ARCHIVED
        sess.status = SessionStatus.ARCHIVED

        # Create new session
        new_sess = AssessmentSessionModel(
            id=str(uuid.uuid4()),
            user_id=sess.user_id,
            status=SessionStatus.ACTIVE,
            consultation_mode=sess.consultation_mode,
            language_code=sess.language_code,
            created_offline=sess.created_offline,
            conducted_at=datetime.now(timezone.utc),
            raw_answers_snapshot={}
        )
        self.session.add(new_sess)
        await self.session.flush()
        await self.session.refresh(new_sess)
        return new_sess

    async def resolve_session(self, session_id: str) -> None:
        """Marks a session as ARCHIVED so it doesn't show up in recent contexts."""
        sess_res = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == session_id,
                AssessmentSessionModel.is_deleted == False
            )
        )
        sess = sess_res.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Assessment session '{session_id}' not found.")
        sess.status = SessionStatus.ARCHIVED
        await self.session.flush()

    async def evaluate_assessment_session(
        self,
        assessment_session_id: str
    ) -> TriageEvaluationResult:
        """Loads session and related DB entities, then evaluates rules."""
        result = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == assessment_session_id,
                AssessmentSessionModel.is_deleted == False,  # noqa: E712
            )
        )
        sess = result.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Assessment session '{assessment_session_id}' not found.")

        if not sess.symptom_id:
            raise ValueError(f"Assessment session '{assessment_session_id}' has no primary symptom set.")

        # Load questions for symptom (eagerly load options to avoid lazy-load in async context)
        q_result = await self.session.execute(
            select(QuestionModel)
            .options(selectinload(QuestionModel.options))
            .where(
                QuestionModel.symptom_id == sess.symptom_id,
                QuestionModel.is_deleted == False,  # noqa: E712
            )
            .order_by(QuestionModel.order_index)
        )
        questions = list(q_result.scalars().all())

        # Load active rules for symptom (eagerly load severity_level and health_concern)
        rule_result = await self.session.execute(
            select(TriageRuleModel)
            .options(
                selectinload(TriageRuleModel.severity_level),
                selectinload(TriageRuleModel.health_concern),
            )
            .where(
                TriageRuleModel.symptom_id == sess.symptom_id,
                TriageRuleModel.is_active == True,  # noqa: E712
                TriageRuleModel.is_deleted == False,  # noqa: E712
            )
        )
        rules = list(rule_result.scalars().all())

        # Load recommendations scoped to the health concerns referenced by these rules.
        # This avoids a full-table scan as the knowledge base grows.
        concern_ids = list(
            {r.health_concern_id for r in rules if r.health_concern_id}
        )
        if concern_ids:
            rec_query = select(RecommendationModel).where(
                RecommendationModel.health_concern_id.in_(concern_ids),
                RecommendationModel.is_active == True,  # noqa: E712
            )
        else:
            # No rules have a health concern — load generic active recommendations
            rec_query = select(RecommendationModel).where(
                RecommendationModel.is_active == True,  # noqa: E712
            ).limit(20)
        rec_result = await self.session.execute(rec_query)
        recommendations = list(rec_result.scalars().all())

        # Run rule engine
        eval_result = self.engine.evaluate(
            session=sess,
            questions=questions,
            rules=rules,
            recommendations=recommendations
        )

        # Update session status if complete or emergency
        if not eval_result.next_question:
            sess.status = SessionStatus.COMPLETED
            if eval_result.severity:
                # Update severity level id if present in database
                sev_res = await self.session.execute(
                    select(SeverityLevelModel).where(SeverityLevelModel.code == eval_result.severity)
                )
                sev = sev_res.scalar_one_or_none()
                if sev:
                    sess.severity_level_id = sev.id
            await self.session.flush()

        return eval_result

    async def get_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[AssessmentSessionModel]:
        """Retrieves paginated triage session history for a user."""
        result = await self.session.execute(
            select(AssessmentSessionModel)
            .options(
                selectinload(AssessmentSessionModel.symptom),
                selectinload(AssessmentSessionModel.severity_level),
            )
            .where(
                AssessmentSessionModel.user_id == user_id,
                AssessmentSessionModel.is_deleted == False,
            )
            .order_by(AssessmentSessionModel.conducted_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_active_rule_tree(self) -> Optional[RuleTreeModel]:
        """Retrieves the currently active versioned clinical rule tree."""
        result = await self.session.execute(
            select(RuleTreeModel)
            .where(RuleTreeModel.is_active == True)
            .order_by(RuleTreeModel.published_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_conversation_transcript(self, session_id: str) -> dict:
        sess_res = await self.session.execute(
            select(AssessmentSessionModel).where(
                AssessmentSessionModel.id == session_id,
                AssessmentSessionModel.is_deleted == False
            )
        )
        sess = sess_res.scalar_one_or_none()
        if not sess:
            raise ValueError(f"Session '{session_id}' not found.")

        symptom_name = None
        symptom_slug = None
        if sess.symptom_id:
            sym_res = await self.session.execute(
                select(SymptomModel).where(SymptomModel.id == sess.symptom_id)
            )
            sym = sym_res.scalar_one_or_none()
            if sym:
                symptom_name = sym.name_en
                symptom_slug = sym.slug

        resp_res = await self.session.execute(
            select(AssessmentResponseModel)
            .where(AssessmentResponseModel.session_id == session_id)
            .order_by(AssessmentResponseModel.answered_at)
        )
        responses = list(resp_res.scalars().all())

        messages = []
        messages.append({
            "role": "SYSTEM",
            "content": "Hi! I'm your Triage Assistant. What symptoms are you experiencing today?"
        })

        if symptom_name:
            messages.append({
                "role": "USER",
                "content": symptom_name
            })

            for resp in responses:
                q_res = await self.session.execute(
                    select(QuestionModel)
                    .options(selectinload(QuestionModel.options))
                    .where(
                        QuestionModel.symptom_id == sess.symptom_id,
                        QuestionModel.node_id == resp.node_id
                    )
                )
                q = q_res.scalar_one_or_none()
                if q:
                    messages.append({
                        "role": "SYSTEM",
                        "content": q.question_text_en
                    })
                    display_ans = resp.answer_raw_text or resp.answer_value
                    if q.options:
                        selected_opts = [o.label_en for o in q.options if o.option_value == resp.answer_value]
                        if selected_opts:
                            display_ans = selected_opts[0]
                    messages.append({
                        "role": "USER",
                        "content": display_ans
                    })

        return {
            "session_id": sess.id,
            "status": sess.status.value if sess.status else None,
            "symptom_name": symptom_name,
            "symptom_slug": symptom_slug,
            "messages": messages
        }
