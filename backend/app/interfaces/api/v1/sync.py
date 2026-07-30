"""Offline Outbox Sync API Router."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status

from app.interfaces.api.dependencies import (
    get_optional_user_id,
    get_sync_service,
)
from app.interfaces.schemas.sync import OutboxSyncRequest, OutboxSyncResponse, SyncedIdPair
from app.use_cases.sync_service import SyncService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post(
    "/outbox",
    response_model=OutboxSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk sync offline outbox sessions",
    description=(
        "Idempotently ingests a batch of offline triage session records from the "
        "client-side IndexedDB outbox queue. Deduplicates by session UUID. "
        "See /docs/OfflineStrategy.md — Section 3 (Outbox Pattern)."
    ),
)
async def sync_outbox(
    payload: OutboxSyncRequest,
    service: SyncService = Depends(get_sync_service),
    user_id: Optional[str] = Depends(get_optional_user_id),
) -> OutboxSyncResponse:
    """Processes offline outbox sync batch."""
    sessions_as_dicts = [
        s.model_dump() for s in payload.sessions
    ]
    result = await service.process_outbox(
        batch_id=payload.batch_id,
        sessions=sessions_as_dicts,
        user_id=user_id,
    )
    return OutboxSyncResponse(
        processed_count=result["processed_count"],
        synced_ids=[SyncedIdPair(**p) for p in result["synced_ids"]],
        errors=result["errors"],
    )


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.api.dependencies import get_async_db
from app.interfaces.schemas.sync import KnowledgeSyncResponse
from app.models.symptom import SymptomModel
from app.models.question import QuestionModel
from app.models.triage_rule import TriageRuleModel
from app.models.recommendation import RecommendationModel
import hashlib
import json

@router.get(
    "/knowledge",
    response_model=KnowledgeSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Download the complete triage knowledge base for offline use.",
    description="Returns all active Symptoms, Questions, Rules, and Recommendations.",
)
async def get_knowledge_sync(
    db: AsyncSession = Depends(get_async_db),
) -> KnowledgeSyncResponse:
    """Fetches the entire rule engine dataset for offline evaluation."""
    
    # 1. Fetch raw ORM entities
    symptoms = (await db.execute(select(SymptomModel))).scalars().all()
    questions = (await db.execute(select(QuestionModel))).scalars().all()
    
    from sqlalchemy.orm import selectinload
    rules = (await db.execute(
        select(TriageRuleModel)
        .where(TriageRuleModel.is_active == True)
        .options(selectinload(TriageRuleModel.severity_level))
    )).scalars().all()
    
    recommendations = (await db.execute(
        select(RecommendationModel)
        .options(selectinload(RecommendationModel.translations))
    )).scalars().all()

    # 2. Serialize to dictionaries
    def serialize_model(instance):
        return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}

    # Custom serialization for questions to include options
    def serialize_question(q):
        d = serialize_model(q)
        # Assuming the ORM relationship might not be eagerly loaded, we just use raw query
        return d

    # For options, we can either fetch them separately or eagerly load. 
    # For simplicity, let's fetch options directly.
    from app.models.question_option import QuestionOptionModel
    options = (await db.execute(select(QuestionOptionModel))).scalars().all()
    
    q_dict = {serialize_model(q)["id"]: serialize_model(q) for q in questions}
    for q in q_dict.values():
        q["options"] = []
    
    for opt in options:
        opt_d = serialize_model(opt)
        q_id = opt_d["question_id"]
        if q_id in q_dict:
            q_dict[q_id]["options"].append(opt_d)

    symptoms_list = [serialize_model(s) for s in symptoms]
    questions_list = list(q_dict.values())
    
    rules_list = []
    for r in rules:
        r_dict = serialize_model(r)
        # Add the string enum code so the client doesn't need a separate mapping table
        if r.severity_level:
            r_dict["severity_code"] = r.severity_level.code.value
        rules_list.append(r_dict)
        
    recommendations_list = []
    for r in recommendations:
        r_dict = serialize_model(r)
        if hasattr(r, 'translations') and r.translations:
            r_dict['translations'] = [serialize_model(t) for t in r.translations]
        else:
            r_dict['translations'] = []
        recommendations_list.append(r_dict)

    # 3. Generate a version hash based on the content (including updated_at timestamps to detect changes)
    def _extract_versions(entities_list):
        # Fallback to created_at if updated_at is None or doesn't exist
        return [f"{e['id']}_{e.get('updated_at', e.get('created_at', ''))}" for e in entities_list]

    content_str = json.dumps({
        "s": _extract_versions(symptoms_list),
        "q": _extract_versions(questions_list),
        "r": _extract_versions(rules_list),
        "rec": _extract_versions(recommendations_list)
    }, sort_keys=True, default=str)
    version = hashlib.md5(content_str.encode("utf-8")).hexdigest()

    return KnowledgeSyncResponse(
        rule_set_version=version,
        symptoms=symptoms_list,
        questions=questions_list,
        triage_rules=rules_list,
        recommendations=recommendations_list,
    )
