"""Assessment API v1 Router.

Provides endpoints for interactive triage assessment session lifecycles:
  - POST /api/v1/assessment/start
  - POST /api/v1/assessment/symptoms
  - POST /api/v1/assessment/answer
  - GET /api/v1/assessment/{session_id}
  - GET /api/v1/assessment/{session_id}/result
  - POST /api/v1/assessment/restart
"""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.api.dependencies import (
    get_triage_service,
    get_optional_user_id,
)
from app.interfaces.schemas.assessment import (
    AssessmentAnswerRequest,
    AssessmentAnswerResponse,
    AssessmentProgressResponse,
    AssessmentRestartRequest,
    AssessmentRestartResponse,
    AssessmentResultResponse,
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSymptomsRequest,
    AssessmentSymptomsResponse,
    NextQuestionDTO,
    QuestionOptionDTO,
)
from sqlalchemy import select
from app.models.symptom import SymptomModel
from app.services.triage_service import TriageService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assessment", tags=["Assessment API"])

def get_conversational_prefix(answer_count: int) -> str:
    prefixes = [
        "I understand. Let's look into this.",
        "Thank you, that's helpful.",
        "I'd like to understand this a little better.",
        "Got it. Just a few more questions.",
        "Thanks for sharing that.",
    ]
    if answer_count == 0:
        return ""
    idx = (answer_count - 1) % len(prefixes)
    return prefixes[idx] + " "

@router.post(
    "/start",
    response_model=AssessmentStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assessment session",
    description="Initializes a new interactive assessment session.",
)
async def start_assessment(
    payload: AssessmentStartRequest,
    service: Annotated[TriageService, Depends(get_triage_service)],
    user_id: Optional[str] = Depends(get_optional_user_id),
) -> AssessmentStartResponse:
    """Creates a new assessment session record."""
    sess, pending_symptom, pending_symptom_slug, pending_session_id = await service.start_conversation(
        language_code=payload.language_code,
        consultation_mode=payload.consultation_mode,
        created_offline=payload.created_offline,
        user_id=user_id,
    )
    return AssessmentStartResponse(
        session_id=sess.id,
        status=sess.status,
        language_code=sess.language_code,
        consultation_mode=sess.consultation_mode,
        created_at=sess.conducted_at,
        pending_symptom=pending_symptom,
        pending_symptom_slug=pending_symptom_slug,
        pending_session_id=pending_session_id,
    )


from app.services.symptom_understanding.symptom_normalizer import SymptomNormalizer

from app.services.ai.gemini_service import GeminiService
from app.interfaces.api.dependencies import get_gemini_service

@router.post(
    "/symptoms",
    response_model=AssessmentSymptomsResponse,
    summary="Set primary symptom for assessment",
    description="Accepts primary symptom selection and returns the first follow-up question.",
)
async def set_symptoms(
    payload: AssessmentSymptomsRequest,
    service: Annotated[TriageService, Depends(get_triage_service)],
    gemini_service: Annotated[GeminiService, Depends(get_gemini_service)],
) -> AssessmentSymptomsResponse:
    """Associates a primary symptom with the assessment session and evaluates initial question or red flag."""
    try:
        normalizer = SymptomNormalizer()
        input_text = payload.user_text or payload.symptom_slug
        
        # Determine language for extraction
        sess, _ = await service.get_progress(payload.session_id)
        
        normalized_slug = normalizer.normalize_with_ai(input_text, sess.language_code, gemini_service)
        
        # If AI and fuzzy matching fail, but the input was a valid slug (e.g. from UI buttons), use it
        if not normalized_slug and payload.symptom_slug in normalizer.dictionary:
            normalized_slug = payload.symptom_slug
            
        if not normalized_slug:
            raise ValueError("I couldn't understand that symptom. Could you rephrase it?")
            
        sess, sym, eval_result = await service.add_symptom(
            conversation_id=payload.session_id,
            symptom_slug=normalized_slug,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    next_q_dto = None
    if eval_result.next_question:
        nq = eval_result.next_question
        ans_count = len(sess.raw_answers_snapshot) if sess.raw_answers_snapshot else 0
        prefix = get_conversational_prefix(ans_count)
        
        question_text_en = prefix + nq["question_text_en"]
        question_text_tw = nq.get("question_text_tw")
        
        # Translate if Twi is requested and we have gemini available
        if sess.language_code == "tw" and gemini_service.is_available:
            question_text_tw = gemini_service.translate_question(question_text_en, sess.language_code)

        next_q_dto = NextQuestionDTO(
            id=nq["id"],
            node_id=nq["node_id"],
            question_text_en=question_text_en,
            question_text_tw=question_text_tw,
            question_type=nq["question_type"],
            options=[QuestionOptionDTO(**opt) for opt in nq.get("options", [])],
        )

    return AssessmentSymptomsResponse(
        session_id=sess.id,
        symptom_slug=sym.slug,
        next_question=next_q_dto,
        is_emergency=eval_result.is_emergency,
        severity=eval_result.severity,
    )


@router.post(
    "/answer",
    response_model=AssessmentAnswerResponse,
    summary="Submit question answer",
    description="Records a question response and returns the next question or final result.",
)
async def submit_answer(
    payload: AssessmentAnswerRequest,
    service: Annotated[TriageService, Depends(get_triage_service)],
    gemini_service: Annotated[GeminiService, Depends(get_gemini_service)],
) -> AssessmentAnswerResponse:
    """Submits a single question node answer and advances assessment progress."""
    try:
        sess, eval_result = await service.record_answer(
            conversation_id=payload.session_id,
            node_id=payload.node_id,
            answer_value=payload.answer_value,
            answer_raw_text=payload.answer_raw_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    next_q_dto = None
    if eval_result.next_question:
        nq = eval_result.next_question
        ans_count = len(sess.raw_answers_snapshot) if sess.raw_answers_snapshot else 0
        prefix = get_conversational_prefix(ans_count)
        
        question_text_en = prefix + nq["question_text_en"]
        question_text_tw = nq.get("question_text_tw")
        
        # Translate if Twi is requested and we have gemini available
        if sess.language_code == "tw" and gemini_service.is_available:
            question_text_tw = gemini_service.translate_question(question_text_en, sess.language_code)

        next_q_dto = NextQuestionDTO(
            id=nq["id"],
            node_id=nq["node_id"],
            question_text_en=question_text_en,
            question_text_tw=question_text_tw,
            question_type=nq["question_type"],
            options=[QuestionOptionDTO(**opt) for opt in nq.get("options", [])],
        )

    result_dto = None
    is_completed = eval_result.next_question is None
    if is_completed:
        result_dto = AssessmentResultResponse(
            session_id=sess.id,
            severity=eval_result.severity,
            recommendations=eval_result.recommendations,
            explanation=eval_result.explanation,
            is_emergency=eval_result.is_emergency,
            conducted_at=sess.conducted_at,
        )

    return AssessmentAnswerResponse(
        session_id=sess.id,
        is_completed=is_completed,
        next_question=next_q_dto,
        result=result_dto,
    )


@router.get(
    "/history",
    summary="Get assessment history",
)
async def get_assessment_history(
    page: int = 1,
    size: int = 20,
    user_id: Optional[str] = Depends(get_optional_user_id),
    service: TriageService = Depends(get_triage_service),
):
    """Retrieves paginated triage session history for the current user."""
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        offset = (page - 1) * size
        sessions = await service.get_history(user_id, limit=size, offset=offset)
        
        items = []
        for s in sessions:
            primary_symptom = s.symptoms[0] if s.symptoms else None
            symptom_model = primary_symptom.symptom if primary_symptom else None
            severity_model = primary_symptom.severity_level if primary_symptom else None

            items.append({
                "id": s.id,
                "status": s.status.value if hasattr(s.status, "value") else s.status,
                "severity_level_id": primary_symptom.severity_level_id if primary_symptom else None,
                "severity_code": severity_model.code if severity_model else None,
                "title": f"Conversation about {symptom_model.name_en}" if symptom_model else "General Health Conversation",
                "consultation_mode": s.consultation_mode.value if hasattr(s.consultation_mode, "value") else s.consultation_mode,
                "created_at": s.conducted_at.isoformat() if hasattr(s.conducted_at, "isoformat") else str(s.conducted_at),
            })
            
        return {
            "items": items,
            "total": len(items),
            "page": page,
            "size": size
        }
    except Exception as exc:
        import logging
        logging.getLogger(__name__).exception("Error fetching assessment history: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {exc}",
        )


@router.get(
    "/{session_id}",
    response_model=AssessmentProgressResponse,
    summary="Retrieve assessment progress",
    description="Gets the current status and answer count of an assessment session.",
)
async def get_assessment_progress(
    session_id: str,
    service: Annotated[TriageService, Depends(get_triage_service)],
) -> AssessmentProgressResponse:
    """Retrieves session status and progress details."""
    try:
        sess, answers_count = await service.get_progress(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return AssessmentProgressResponse(
        session_id=sess.id,
        status=sess.status,
        symptom_id=sess.symptoms[0].symptom_id if sess.symptoms else None,
        answers_count=answers_count,
        conducted_at=sess.conducted_at,
        created_offline=sess.created_offline,
    )


@router.get(
    "/{session_id}/result",
    response_model=AssessmentResultResponse,
    summary="Retrieve assessment result",
    description="Gets the evaluated severity, recommendations, and emergency status for a session.",
)
async def get_assessment_result(
    session_id: str,
    service: Annotated[TriageService, Depends(get_triage_service)],
) -> AssessmentResultResponse:
    """Evaluates and returns the final or current clinical triage result for a session."""
    try:
        sess, eval_result = await service.get_result(session_id)
        symptom_name = None
        if sess.symptoms:
            symptom_name = sess.symptoms[0].symptom.name_en if sess.symptoms[0].symptom else None
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return AssessmentResultResponse(
        session_id=sess.id,
        severity=eval_result.severity,
        recommendations=eval_result.recommendations,
        explanation=eval_result.explanation,
        is_emergency=eval_result.is_emergency,
        conducted_at=sess.conducted_at,
        symptom_name=symptom_name,
        raw_answers=sess.raw_answers_snapshot,
    )


@router.post(
    "/restart",
    response_model=AssessmentRestartResponse,
    summary="Restart an assessment",
    description="Marks the previous session as abandoned and creates a fresh session.",
)
async def restart_assessment(
    payload: AssessmentRestartRequest,
    service: Annotated[TriageService, Depends(get_triage_service)],
) -> AssessmentRestartResponse:
    """Restarts an assessment flow."""
    try:
        new_sess = await service.restart_conversation(payload.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return AssessmentRestartResponse(
        new_session_id=new_sess.id,
        status=new_sess.status,
    )


@router.post(
    "/{session_id}/resolve",
    summary="Resolve a past assessment session",
    description="Archives the session so it is no longer considered active/pending.",
)
async def resolve_assessment(
    session_id: str,
    service: Annotated[TriageService, Depends(get_triage_service)],
):
    """Marks a session as resolved/archived."""
    try:
        await service.resolve_conversation(session_id)
        return {"status": "success"}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))



@router.get(
    "/{session_id}/conversation",
    summary="Get conversation transcript",
)
async def get_conversation_transcript(
    session_id: str,
    service: TriageService = Depends(get_triage_service),
):
    """Retrieves full text transcript of the conversation session."""
    try:
        return await service.get_conversation_transcript(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

