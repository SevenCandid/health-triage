import asyncio
import json
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.infrastructure.database.session import async_session_factory
from app.models.symptom import SymptomModel
from app.models.triage_rule import TriageRuleModel
from app.models.question import QuestionModel
from app.models.recommendation import RecommendationModel
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.encoders import jsonable_encoder

async def dump():
    async with async_session_factory() as session:
        # 1. Load Symptoms
        stmt = select(SymptomModel).where(SymptomModel.is_active == True)
        result = await session.execute(stmt)
        symptoms = result.scalars().all()
        
        # 2. Load Triage Rules
        stmt = select(TriageRuleModel).where(TriageRuleModel.is_active == True)
        result = await session.execute(stmt)
        rules = result.scalars().all()
        
        # 3. Load Questions
        stmt = select(QuestionModel).options(selectinload(QuestionModel.options))
        result = await session.execute(stmt)
        questions = result.scalars().all()
        
        # 4. Load Recommendations
        stmt = select(RecommendationModel)
        result = await session.execute(stmt)
        recommendations = result.scalars().all()
        
        data = {
            "rule_set_version": "bundled-v1",
            "symptoms": jsonable_encoder(symptoms),
            "questions": jsonable_encoder(questions),
            "triage_rules": jsonable_encoder(rules),
            "recommendations": jsonable_encoder(recommendations),
        }
        
        json_data = json.dumps(data, indent=2)
        
        out_path = os.path.join(os.path.dirname(__file__), '../frontend/public/data/knowledge.json')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f"Successfully dumped to {out_path}")

if __name__ == '__main__':
    asyncio.run(dump())
