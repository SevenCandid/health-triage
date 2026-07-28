"""Run all database seeds against the configured DATABASE_URL.
Uses merge (upsert-style) via session.merge so re-runs are safe."""
import asyncio
import logging
import sys
sys.path.insert(0, '.')

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s %(message)s")

async def main():
    from app.infrastructure.database.session import async_session_factory
    from app.infrastructure.database.seed import seed_rule_trees, seed_admin_user
    from app.infrastructure.database.seeds.seed_master import seed_all_knowledge_base

    # Use a fresh session for each stage so prior partial commits don't pollute state
    print("Stage 1: Seeding rule trees...")
    async with async_session_factory() as s1:
        await seed_rule_trees(s1)

    print("Stage 2: Seeding knowledge base (languages, symptoms, questions...)...")
    async with async_session_factory() as s2:
        await seed_all_knowledge_base(s2)

    print("Stage 3: Seeding admin user...")
    async with async_session_factory() as s3:
        await seed_admin_user(s3)

    print("All seeds complete.")

asyncio.run(main())
