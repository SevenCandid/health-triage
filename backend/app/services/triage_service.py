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

from app.models.health_conversation import HealthConversationModel, ConversationSymptomModel, ConversationStatus, ConsultationMode
from app.models.assessment_response import AssessmentResponseModel
from app.models.symptom import SymptomModel
from app.models.question import QuestionModel
from app.models.triage_rule import TriageRuleModel
from app.models.recommendation import RecommendationModel
from app.models.severity_level import SeverityLevelModel
from app.infrastructure.database.models import RuleTreeModel, HealthProfileModel

from app.engine.rule_engine import RuleEngine, TriageEvaluationResult

logger = logging.getLogger(__name__)


class TriageService:
    """Service layer that manages assessment session lifecycles and invokes RuleEngine."""

    def __init__(self, db_session: AsyncSession, gemini_service=None) -> None:
        self.session = db_session
        self.engine = RuleEngine()
        self.gemini_service = gemini_service

    async def start_conversation(
        self,
        language_code: str = "en",
        consultation_mode: ConsultationMode = ConsultationMode.TEXT,
        created_offline: bool = False,
        user_id: Optional[str] = None
    ) -> tuple[HealthConversationModel, Optional[str]]:
        """Creates and persists a new health conversation."""
        logger.info(f"Starting new health conversation. Mode: {consultation_mode}, Lang: {language_code}")
        
        pending_symptom = None
        pending_symptom_slug = None
        if user_id:
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_sess_res = await self.session.execute(
                select(HealthConversationModel)
                .options(selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.symptom))
                .where(
                    HealthConversationModel.user_id == user_id,
                    HealthConversationModel.conducted_at >= seven_days_ago,
                    HealthConversationModel.is_deleted == False
                )
                .order_by(HealthConversationModel.conducted_at.desc())
                .limit(1)
            )
            recent_sess = recent_sess_res.scalar_one_or_none()
            if recent_sess and recent_sess.symptoms:
                sym = recent_sess.symptoms[0].symptom
                pending_symptom = sym.name_en
                pending_symptom_slug = sym.slug
                pending_session_id = recent_sess.id

        conv = HealthConversationModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            status=ConversationStatus.ACTIVE,
            consultation_mode=consultation_mode,
            language_code=language_code,
            created_offline=created_offline,
            conducted_at=datetime.now(timezone.utc),
            raw_answers_snapshot={}
        )
        self.session.add(conv)
        await self.session.flush()
        await self.session.refresh(conv)
        return conv, pending_symptom, pending_symptom_slug, pending_session_id if pending_symptom else None

    async def add_symptom(
        self,
        conversation_id: str,
        symptom_slug: str
    ) -> tuple[HealthConversationModel, SymptomModel, TriageEvaluationResult]:
        """Adds a new symptom to an active health conversation and runs initial evaluation."""
        logger.info(f"Adding symptom '{symptom_slug}' to conversation {conversation_id}")        
        conv_res = await self.session.execute(
            select(HealthConversationModel)
            .options(selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.symptom))
            .where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False,
            )
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")

        sym_res = await self.session.execute(
            select(SymptomModel).where(SymptomModel.slug == symptom_slug)
        )
        sym = sym_res.scalar_one_or_none()
        if not sym:
            raise ValueError(f"Symptom '{symptom_slug}' not found.")

        # Check if symptom is already in conversation
        for cs in conv.symptoms:
            if cs.symptom_id == sym.id:
                eval_result = await self.evaluate_conversation(conversation_id, sym.id)
                return conv, sym, eval_result

        # Create new ConversationSymptom
        conv_symp = ConversationSymptomModel(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            symptom_id=sym.id
        )
        conv.symptoms.append(conv_symp)
        self.session.add(conv_symp)
        await self.session.flush()

        eval_result = await self.evaluate_conversation(conversation_id, sym.id)
        return conv, sym, eval_result

    async def record_answer(
        self,
        conversation_id: str,
        node_id: str,
        answer_value: str,
        answer_raw_text: Optional[str] = None
    ) -> tuple[HealthConversationModel, TriageEvaluationResult]:
        """Records a user answer for a specific symptom and re-evaluates the conversation."""
        logger.info(f"Recording answer '{node_id}'='{answer_value}' for conversation {conversation_id}")
        conv_res = await self.session.execute(
            select(HealthConversationModel)
            .options(selectinload(HealthConversationModel.symptoms))
            .where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False,
            )
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")

        # Find symptom_id from question node
        symptom_ids = [cs.symptom_id for cs in conv.symptoms]
        q_res = await self.session.execute(
            select(QuestionModel).where(
                QuestionModel.symptom_id.in_(symptom_ids),
                QuestionModel.node_id == node_id
            )
        )
        q = q_res.scalar_one_or_none()
        symptom_id = q.symptom_id if q else None

        snapshot = dict(conv.raw_answers_snapshot or {})
        snapshot[node_id] = answer_value
        conv.raw_answers_snapshot = snapshot

        response_entry = AssessmentResponseModel(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            symptom_id=symptom_id,
            question_id=q.id if q else None,
            node_id=node_id,
            answer_value=answer_value,
            answer_raw_text=answer_raw_text,
            answered_at=datetime.now(timezone.utc)
        )
        self.session.add(response_entry)
        await self.session.flush()

        eval_result = await self.evaluate_conversation(conversation_id, symptom_id)
        return conv, eval_result

    async def get_progress(self, conversation_id: str) -> tuple[HealthConversationModel, int]:
        """Retrieves session progress and count of recorded answers."""
        conv_res = await self.session.execute(
            select(HealthConversationModel)
            .options(selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.symptom))
            .where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False,
            )
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")

        answers_count = len(conv.raw_answers_snapshot or {})
        return conv, answers_count

    async def get_result(self, conversation_id: str) -> tuple[HealthConversationModel, TriageEvaluationResult]:
        """Loads and calculates the current or final result of a conversation."""
        conv_res = await self.session.execute(
            select(HealthConversationModel)
            .options(selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.symptom))
            .where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False,
            )
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")

        eval_result = await self.evaluate_conversation(conversation_id, None)
        
        # If the assessment is completed, generate an AI summary
        if eval_result.next_question is None and self.gemini_service:
            if not conv.ai_explanation:
                # Need to generate and save it
                transcript = f"Symptoms evaluated: {', '.join([cs.symptom.name_en for cs in conv.symptoms])}"
                # Add a brief representation of answers
                answers_text = []
                for k, v in (conv.raw_answers_snapshot or {}).items():
                    answers_text.append(f"{k}: {v}")
                if answers_text:
                    transcript += f" | Answers: {', '.join(answers_text)}"
                    
                profile_context = None
                if conv.user_id:
                    profile_res = await self.session.execute(
                        select(HealthProfileModel).where(HealthProfileModel.user_id == conv.user_id)
                    )
                    profile = profile_res.scalar_one_or_none()
                    if profile:
                        parts = []
                        if profile.age: parts.append(f"Age: {profile.age}")
                        if profile.biological_sex: parts.append(f"Sex: {profile.biological_sex}")
                        if profile.blood_group: parts.append(f"Blood Group: {profile.blood_group}")
                        if profile.chronic_conditions: parts.append(f"Chronic Conditions: {', '.join(profile.chronic_conditions)}")
                        if profile.known_allergies: parts.append(f"Allergies: {', '.join(profile.known_allergies)}")
                        if parts:
                            profile_context = " | ".join(parts)
                            
                explanation = self.gemini_service.generate_explanation(
                    conversation_context=transcript,
                    recommendation_summary=eval_result.explanation,
                    is_emergency=eval_result.is_emergency,
                    language_code=conv.language_code,
                    profile_context=profile_context
                )
                conv.ai_explanation = explanation
                self.session.add(conv)
                await self.session.flush()
                await self.session.commit()
            
            # Override the rule engine explanation with the AI one
            eval_result.explanation = conv.ai_explanation

        return conv, eval_result

    async def restart_conversation(self, conversation_id: str) -> HealthConversationModel:
        """Restarts an assessment session by creating a new conversation with identical parameters."""
        logger.info(f"Restarting conversation {conversation_id}")
        conv_res = await self.session.execute(
            select(HealthConversationModel).where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False,
            )
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")

        conv.status = ConversationStatus.ARCHIVED

        new_conv = HealthConversationModel(
            id=str(uuid.uuid4()),
            user_id=conv.user_id,
            status=ConversationStatus.ACTIVE,
            consultation_mode=conv.consultation_mode,
            language_code=conv.language_code,
            created_offline=conv.created_offline,
            conducted_at=datetime.now(timezone.utc),
            raw_answers_snapshot={}
        )
        self.session.add(new_conv)
        await self.session.flush()
        await self.session.refresh(new_conv)
        return new_conv

    async def resolve_conversation(self, conversation_id: str) -> None:
        """Marks a conversation as ARCHIVED so it doesn't show up in recent contexts."""
        conv_res = await self.session.execute(
            select(HealthConversationModel).where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False
            )
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")
        conv.status = ConversationStatus.ARCHIVED
        await self.session.flush()

    async def evaluate_conversation(
        self,
        conversation_id: str,
        active_symptom_id: Optional[str]
    ) -> TriageEvaluationResult:
        """Loads session and related DB entities, then evaluates rules."""
        result = await self.session.execute(
            select(HealthConversationModel)
            .options(
                selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.symptom)
            )
            .where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False,
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")

        active_symptom = None
        all_symptom_ids = [cs.symptom_id for cs in conv.symptoms]

        if active_symptom_id:
            active_symptom = next((cs for cs in conv.symptoms if cs.symptom_id == active_symptom_id), None)

        # Load questions for all symptoms
        all_questions = {}
        if all_symptom_ids:
            q_result = await self.session.execute(
                select(QuestionModel)
                .options(selectinload(QuestionModel.options))
                .where(
                    QuestionModel.symptom_id.in_(all_symptom_ids),
                    QuestionModel.is_deleted == False,
                )
                .order_by(QuestionModel.order_index)
            )
            for q in q_result.scalars():
                if q.symptom_id not in all_questions:
                    all_questions[q.symptom_id] = []
                all_questions[q.symptom_id].append(q)

        # Load active rules for all symptoms
        all_rules = {}
        if all_symptom_ids:
            rule_result = await self.session.execute(
                select(TriageRuleModel)
                .options(
                    selectinload(TriageRuleModel.severity_level),
                    selectinload(TriageRuleModel.health_concern),
                )
                .where(
                    TriageRuleModel.symptom_id.in_(all_symptom_ids),
                    TriageRuleModel.is_active == True,
                    TriageRuleModel.is_deleted == False,
                )
            )
            for r in rule_result.scalars():
                if r.symptom_id not in all_rules:
                    all_rules[r.symptom_id] = []
                all_rules[r.symptom_id].append(r)

        # Load recommendations scoped to the health concerns referenced by these rules.
        concern_ids = set()
        for rules in all_rules.values():
            for r in rules:
                if r.health_concern_id:
                    concern_ids.add(r.health_concern_id)

        if concern_ids:
            rec_query = select(RecommendationModel).options(
                selectinload(RecommendationModel.translations)
            ).where(
                RecommendationModel.health_concern_id.in_(concern_ids),
                RecommendationModel.is_active == True,
            )
        else:
            rec_query = select(RecommendationModel).options(
                selectinload(RecommendationModel.translations)
            ).where(
                RecommendationModel.is_active == True,
            ).limit(20)
        
        rec_result = await self.session.execute(rec_query)
        all_recommendations = list(rec_result.scalars().all())

        # Run rule engine
        eval_result = self.engine.evaluate_conversation(
            conversation=conv,
            active_symptom=active_symptom,
            all_questions=all_questions,
            all_rules=all_rules,
            all_recommendations=all_recommendations
        )

        if not eval_result.next_question and self.gemini_service and self.gemini_service.is_available:
            dynamic_keys = [k for k in (conv.raw_answers_snapshot or {}).keys() if k.startswith("dynamic_ai_")]
            if len(dynamic_keys) < 2:
                transcript = await self.get_conversation_transcript(conversation_id)
                context_str = ""
                for msg in transcript.get("messages", []):
                    role = "Assistant" if msg["role"] == "SYSTEM" else "User"
                    context_str += f"{role}: {msg['content']}\n"
                
                ai_question = self.gemini_service.generate_dynamic_question(context_str, conv.language_code)
                if ai_question:
                    next_idx = len(dynamic_keys) + 1
                    eval_result.next_question = {
                        "id": str(uuid.uuid4()),
                        "node_id": f"dynamic_ai_{next_idx}",
                        "question_text_en": ai_question,
                        "question_text_tw": ai_question,
                        "question_type": "FREE_TEXT",
                        "options": []
                    }

        # Update session status if complete or emergency
        if not eval_result.next_question:
            conv.status = ConversationStatus.COMPLETED
            await self.session.flush()

        return eval_result

    async def get_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[HealthConversationModel]:
        """Retrieves paginated health conversation history for a user."""
        result = await self.session.execute(
            select(HealthConversationModel)
            .options(
                selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.symptom),
                selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.severity_level)
            )
            .where(
                HealthConversationModel.user_id == user_id,
                HealthConversationModel.is_deleted == False,
            )
            .order_by(HealthConversationModel.conducted_at.desc())
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

    async def get_conversation_transcript(self, conversation_id: str) -> dict:
        conv_res = await self.session.execute(
            select(HealthConversationModel)
            .options(selectinload(HealthConversationModel.symptoms).selectinload(ConversationSymptomModel.symptom))
            .where(
                HealthConversationModel.id == conversation_id,
                HealthConversationModel.is_deleted == False
            )
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise ValueError(f"Health conversation '{conversation_id}' not found.")

        resp_res = await self.session.execute(
            select(AssessmentResponseModel)
            .where(AssessmentResponseModel.conversation_id == conversation_id)
            .order_by(AssessmentResponseModel.answered_at)
        )
        responses = list(resp_res.scalars().all())

        messages = []
        messages.append({
            "role": "SYSTEM",
            "content": "Hi! I'm FirstAid+. What symptoms are you experiencing today?"
        })

        if conv.symptoms:
            symptoms_list = ", ".join([cs.symptom.name_en for cs in conv.symptoms])
            messages.append({
                "role": "USER",
                "content": symptoms_list
            })

            # Fetch questions so we can match their text
            symptom_ids = [cs.symptom_id for cs in conv.symptoms]
            q_res = await self.session.execute(
                select(QuestionModel)
                .options(selectinload(QuestionModel.options))
                .where(
                    QuestionModel.symptom_id.in_(symptom_ids)
                )
            )
            questions_by_node = {q.node_id: q for q in q_res.scalars()}

            for resp in responses:
                q = questions_by_node.get(resp.node_id)
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
            "session_id": conv.id,
            "status": conv.status.value if conv.status else None,
            "symptoms": [cs.symptom.name_en for cs in conv.symptoms] if conv.symptoms else [],
            "messages": messages
        }
