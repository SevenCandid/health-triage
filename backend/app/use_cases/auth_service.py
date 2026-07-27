"""Authentication Service — Use Case Layer.

Orchestrates user registration, login, and token issuance.
Business logic is invoked through concrete repository instances
injected at construction time.

See /docs/BackendArchitecture.md — Section 2.2 Use Cases Layer.
"""

import logging
from typing import Optional

from app.domain.repositories.interfaces import IUserRepository
from app.infrastructure.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.infrastructure.security.password import hash_password, verify_password
from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Handles user account registration and JWT-based authentication."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def register(
        self,
        phone_number: str,
        password: str,
        full_name: str,
        email: Optional[str] = None,
        preferred_language: str = "en",
    ) -> dict:
        """Registers a new user account and returns a JWT token pair.

        Args:
            phone_number: Unique user phone in E.164 format.
            password: Plain text password (will be hashed with Argon2id).
            full_name: User's full name.
            email: Optional unique email address.
            preferred_language: ISO language code ('en' or 'tw').

        Returns:
            Dict containing access_token, refresh_token, user metadata.

        Raises:
            ValueError: If the phone number or email is already registered.
        """
        existing = await self._user_repo.get_by_phone(phone_number)
        if existing:
            raise ValueError(f"Phone number '{phone_number}' is already registered.")
            
        if email:
            existing_email = await self._user_repo.get_by_email(email)
            if existing_email:
                raise ValueError(f"Email '{email}' is already registered.")

        password_hash = hash_password(password)
        user = await self._user_repo.create(
            phone_number=phone_number,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            preferred_language=preferred_language,
        )
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        logger.info(f"New user registered: id={user.id}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "user": user,
        }

    async def login(self, identifier: str, password: str) -> dict:
        """Authenticates a user and returns a JWT token pair.

        Args:
            identifier: User's registered phone number or email address.
            password: Plain text password to verify.

        Returns:
            Dict containing access_token, refresh_token, and user metadata.

        Raises:
            ValueError: If credentials are invalid.
        """
        user = await self._user_repo.get_by_identifier(identifier)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials.")

        if not user.is_active:
            raise ValueError("User account is deactivated.")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        logger.info(f"User authenticated: id={user.id}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "user": user,
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        """Issues a new access and refresh token pair using a valid refresh token.
        
        Args:
            refresh_token: The JWT refresh token string.
            
        Returns:
            Dict containing new access_token, refresh_token, and user metadata.
            
        Raises:
            ValueError: If the token is invalid, expired, or user not found/active.
        """
        import jwt
        try:
            payload = decode_refresh_token(refresh_token)
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token expired.")
        except (jwt.InvalidTokenError, ValueError):
            raise ValueError("Invalid refresh token.")
            
        user_id = payload["sub"]
        user = await self._user_repo.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise ValueError("User not found or deactivated.")
            
        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)
        logger.info(f"Token refreshed for user: id={user.id}")
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "user": user,
        }
