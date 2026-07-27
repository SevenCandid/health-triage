import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.infrastructure.database.seeds.seed_master import seed_all_knowledge_base
from app.config import settings

logging.basicConfig(level=logging.INFO)

async def test():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        await seed_all_knowledge_base(session)

asyncio.run(test())
