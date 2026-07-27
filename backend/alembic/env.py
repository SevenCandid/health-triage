"""Alembic Migration Environment — Async SQLAlchemy 2.0.

Configures the Alembic migration runner to use asyncio with the
application's async SQLAlchemy engine and imports Base.metadata
so autogenerate can detect model changes.

See /docs/DatabaseDesign.md — Section 5 Alembic Workflow.
"""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Load Alembic .ini config section
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all SQLAlchemy models so autogenerate picks up changes
from app.models.base import Base  # noqa: E402
import app.infrastructure.database.models  # noqa: E402, F401 — registers legacy models
import app.models.user
import app.models.emergency_contact
import app.models.assessment_session
import app.models.audit_log
import app.models.health_concern
import app.models.language
import app.models.question
import app.models.question_option
import app.models.recommendation
import app.models.recommendation_translation
import app.models.severity_level
import app.models.symptom
import app.models.symptom_category
import app.models.symptom_concern
import app.models.symptom_translation
import app.models.triage_rule

target_metadata = Base.metadata

# Read DATABASE_URL from environment (overrides alembic.ini sqlalchemy.url if set)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./health_triage.db"
)


def run_migrations_offline() -> None:
    """Run Alembic migrations in 'offline' mode (SQL script generation)."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations inside a synchronous database connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations within the event loop."""
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run Alembic migrations in 'online' mode using asyncio."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
