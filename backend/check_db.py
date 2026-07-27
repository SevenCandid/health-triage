import asyncio
import sys
sys.path.insert(0, 'app')

async def main():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    DB_URL = "postgresql+asyncpg://postgres:Nexra2026@localhost:5432/health_triage"
    engine = create_async_engine(DB_URL)

    async with engine.connect() as conn:
        # List all tables
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' ORDER BY table_name"
        ))
        tables = [r[0] for r in result]
        print("Tables:", tables)

        if "assessment_sessions" in tables:
            result2 = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='assessment_sessions' ORDER BY ordinal_position"
            ))
            cols = [r[0] for r in result2]
            print("assessment_sessions columns:", cols)
        else:
            print("WARNING: assessment_sessions table does NOT exist!")

        if "triage_sessions" in tables:
            result3 = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='triage_sessions' ORDER BY ordinal_position"
            ))
            cols3 = [r[0] for r in result3]
            print("triage_sessions columns:", cols3)

asyncio.run(main())
