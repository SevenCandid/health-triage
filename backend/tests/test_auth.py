"""Authentication Endpoint Tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_new_user(async_client: AsyncClient) -> None:
    """POST /api/v1/auth/register should create user and return JWT token."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": "+233241234567",
            "password": "TestPass123!",
            "preferred_language": "en",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in_minutes"] == 60


@pytest.mark.asyncio
async def test_register_duplicate_phone_returns_400(async_client: AsyncClient) -> None:
    """POST /api/v1/auth/register with a duplicate phone number should return 400."""
    payload = {
        "phone_number": "+233241111111",
        "password": "TestPass123!",
        "preferred_language": "en",
    }
    await async_client.post("/api/v1/auth/register", json=payload)
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_valid_credentials(async_client: AsyncClient) -> None:
    """POST /api/v1/auth/login with valid credentials should return token."""
    phone = "+233249999999"
    password = "TestPass123!"
    await async_client.post(
        "/api/v1/auth/register",
        json={"phone_number": phone, "password": password, "preferred_language": "tw"},
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"phone_number": phone, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password_returns_400(async_client: AsyncClient) -> None:
    """POST /api/v1/auth/login with wrong password should return 400."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"phone_number": "+233249999999", "password": "WrongPass999!"},
    )
    assert response.status_code == 400
