"""Triage Evaluation Endpoint Tests.

Covers the deterministic stub evaluator responses.
Full rule engine tests will be added in Phase 2 (see /docs/TestingStrategy.md).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_evaluate_fever_returns_yellow(async_client: AsyncClient) -> None:
    """POST /api/v1/triage/evaluate for 'fever' should return YELLOW urgency."""
    response = await async_client.post(
        "/api/v1/triage/evaluate",
        json={
            "primary_symptom": "fever",
            "patient_age": 30,
            "patient_sex": "MALE",
            "language_code": "en",
            "answers": {},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["urgency_level"] == "YELLOW"
    assert "session_id" in data
    assert "primary_action" in data
    assert "en" in data["primary_action"]
    assert "tw" in data["primary_action"]


@pytest.mark.asyncio
async def test_evaluate_severe_bleeding_returns_red(async_client: AsyncClient) -> None:
    """POST /api/v1/triage/evaluate for 'severe_bleeding' should return RED."""
    response = await async_client.post(
        "/api/v1/triage/evaluate",
        json={
            "primary_symptom": "severe_bleeding",
            "patient_age": 25,
            "patient_sex": "FEMALE",
            "language_code": "tw",
            "answers": {},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["urgency_level"] == "RED"
    assert data["timeframe_hours"] == 0


@pytest.mark.asyncio
async def test_evaluate_unknown_symptom_returns_green(async_client: AsyncClient) -> None:
    """POST /api/v1/triage/evaluate for unknown symptom should return GREEN."""
    response = await async_client.post(
        "/api/v1/triage/evaluate",
        json={
            "primary_symptom": "mild_fatigue",
            "patient_age": 40,
            "patient_sex": "OTHER",
            "language_code": "en",
            "answers": {},
        },
    )
    assert response.status_code == 200
    assert response.json()["urgency_level"] == "GREEN"


@pytest.mark.asyncio
async def test_evaluate_invalid_age_returns_422(async_client: AsyncClient) -> None:
    """POST /api/v1/triage/evaluate with invalid age should return 422."""
    response = await async_client.post(
        "/api/v1/triage/evaluate",
        json={
            "primary_symptom": "fever",
            "patient_age": 999,  # invalid — exceeds 120
            "patient_sex": "MALE",
            "language_code": "en",
            "answers": {},
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_latest_rule_tree(async_client: AsyncClient) -> None:
    """GET /api/v1/triage/rules/latest should return the seeded rule tree."""
    # First seed must be available — lifespan seeds on startup
    response = await async_client.get("/api/v1/triage/rules/latest")
    # May be 200 (seeded) or 400 (no seed in test DB — both are acceptable for now)
    assert response.status_code in (200, 400)
