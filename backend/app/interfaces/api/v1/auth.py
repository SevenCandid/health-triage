"""Authentication API Router — Register & Login."""

import logging
from fastapi import APIRouter, Depends, status, HTTPException

from app.interfaces.api.dependencies import get_auth_service, get_current_user_id, get_user_repo
from app.interfaces.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.use_cases.auth_service import AuthService
from app.interfaces.repositories.sqlalchemy_repos import SqlAlchemyUserRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user account with phone number and password. "
        "Returns a JWT access token on success."
    ),
)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Registers a new user and returns a bearer token pair."""
    try:
        result = await service.register(
            phone_number=payload.phone_number,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            preferred_language=payload.preferred_language,
        )
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in_minutes=result["expires_in_minutes"],
            user=result["user"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT token",
    description=(
        "Validates email or phone number and password credentials. "
        "Returns a JWT access and refresh token pair on successful authentication."
    ),
)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticates a user and returns a bearer token pair."""
    try:
        result = await service.login(
            identifier=payload.identifier,
            password=payload.password,
        )
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in_minutes=result["expires_in_minutes"],
            user=result["user"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh JWT tokens",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Issues a new token pair using a valid refresh token."""
    try:
        result = await service.refresh_token(payload.refresh_token)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in_minutes=result["expires_in_minutes"],
            user=result["user"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
)
async def logout(user_id: str = Depends(get_current_user_id)):
    """Logs out the user. Clients should discard tokens."""
    return {"message": "Successfully logged out."}

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user details",
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repo),
) -> UserResponse:
    """Returns the currently authenticated user's details."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found.")
    return UserResponse.model_validate(user)
