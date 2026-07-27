"""Full integration tests for the Assessment API layer.

Covers all 6 required endpoints:
- POST /api/v1/assessment/start
- POST /api/v1/assessment/symptoms
- POST /api/v1/assessment/answer
- GET /api/v1/assessment/{session_id}
- GET /api/v1/assessment/{session_id}/result
- POST /api/v1/assessment/restart
"""

import pytest
from httpx import AsyncClient
from app.infrastructure.database.seed import run_seeds


@pytest.fixture(autouse=True)
async def seed_test_database(db_session):
    """Populate database with baseline seed data before running tests."""
    await run_seeds(db_session)


@pytest.mark.asyncio
async def test_assessment_full_flow(async_client: AsyncClient) -> None:
    """Tests the full assessment lifecycle: start -> symptoms -> answer -> progress -> result -> restart."""

    # 1. Start Session
    start_resp = await async_client.post(
        "/api/v1/assessment/start",
        json={"language_code": "en", "consultation_mode": "TEXT", "created_offline": False}
    )
    assert start_resp.status_code == 201
    start_data = start_resp.json()
    session_id = start_data["session_id"]
    assert start_data["status"] == "IN_PROGRESS"

    # 2. Set Symptoms
    symptoms_resp = await async_client.post(
        "/api/v1/assessment/symptoms",
        json={"session_id": session_id, "symptom_slug": "chest-pain"}
    )
    assert symptoms_resp.status_code == 200
    symptoms_data = symptoms_resp.json()
    assert symptoms_data["symptom_slug"] == "chest-pain"
    assert symptoms_data["next_question"] is not None

    next_q_node = symptoms_data["next_question"]["node_id"]

    # 3. Submit Answer
    answer_resp = await async_client.post(
        "/api/v1/assessment/answer",
        json={"session_id": session_id, "node_id": next_q_node, "answer_value": "less_than_24h"}
    )
    assert answer_resp.status_code == 200
    answer_data = answer_resp.json()
    assert answer_data["session_id"] == session_id

    # 4. Get Assessment Progress
    progress_resp = await async_client.get(f"/api/v1/assessment/{session_id}")
    assert progress_resp.status_code == 200
    progress_data = progress_resp.json()
    assert progress_data["session_id"] == session_id
    assert progress_data["answers_count"] == 1

    # 5. Get Assessment Result
    result_resp = await async_client.get(f"/api/v1/assessment/{session_id}/result")
    assert result_resp.status_code == 200
    result_data = result_resp.json()
    assert result_data["session_id"] == session_id
    assert "severity" in result_data
    assert "recommendations" in result_data

    # 6. Restart Assessment
    restart_resp = await async_client.post(
        "/api/v1/assessment/restart",
        json={"session_id": session_id}
    )
    assert restart_resp.status_code == 200
    restart_data = restart_resp.json()
    assert restart_data["new_session_id"] != session_id
    assert restart_data["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_assessment_nonexistent_session_returns_404(async_client: AsyncClient) -> None:
    """Tests 404 response when querying invalid session ID."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await async_client.get(f"/api/v1/assessment/{fake_id}")
    assert resp.status_code == 404
