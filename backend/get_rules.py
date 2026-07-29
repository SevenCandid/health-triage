import asyncio
from sqlalchemy import select
from app.infrastructure.database.session import async_session_factory
from app.models.triage_rule import TriageRuleModel
import json

async def run():
    async with async_session_factory() as db:
        rules = (await db.execute(select(TriageRuleModel).limit(2))).scalars().all()
        for r in rules:
            d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
            print(json.dumps(d, default=str))

if __name__ == "__main__":
    asyncio.run(run())
