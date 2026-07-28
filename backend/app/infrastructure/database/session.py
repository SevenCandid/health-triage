"""Async SQLAlchemy 2.0 Engine & Session Management Module."""

from typing import AsyncGenerator
import logging
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

logger = logging.getLogger(__name__)

import re
import ssl as _ssl

def _build_engine_args(url: str) -> tuple[str, dict]:
    """Strip sslmode/channel_binding query params and return connect_args for asyncpg."""
    connect_args: dict = {}
    if "postgresql+asyncpg" in url:
        if "sslmode=require" in url or "sslmode=prefer" in url:
            connect_args["ssl"] = _ssl.create_default_context()
        url = re.sub(r"[?&]sslmode=[^&]*", "", url)
        url = re.sub(r"[?&]channel_binding=[^&]*", "", url)
        url = re.sub(r"[?&]$", "", url)
    return url, connect_args

_db_url, _connect_args = _build_engine_args(settings.DATABASE_URL)

# Configure Async Engine
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider yielding async SQLAlchemy DB sessions per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session rolled back due to exception: {exc}")
            raise
        finally:
            await session.close()
