"""Health Endpoint Tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_probe(async_client: AsyncClient) -> None:
    """GET / should return 200 OK with service info."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "service" in data


@pytest.mark.asyncio
async def test_api_health_check(async_client: AsyncClient) -> None:
    """GET /api/v1/health should return 200 OK with database status."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["environment"] == "development"


@pytest.mark.asyncio
async def test_openapi_schema_available(async_client: AsyncClient) -> None:
    """GET /openapi.json should return 200 OK in debug mode."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Health Triage Assistant API"
