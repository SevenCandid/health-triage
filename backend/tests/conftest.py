"""Pytest Fixtures & Configuration.

Sets up an isolated async test environment using:
  - SQLite in-memory (aiosqlite) as the test database
  - Overrides the get_async_db dependency with the test session
  - Provides a pre-configured httpx.AsyncClient for API testing
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.infrastructure.database.session import get_async_db
from app.main import app

# Use a fresh in-memory SQLite database per test session
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    """Creates all tables in the test in-memory database before test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Provides a clean async database session per test with automatic rollback."""
    async with TestSessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """Provides an authenticated async HTTP test client with DB override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
