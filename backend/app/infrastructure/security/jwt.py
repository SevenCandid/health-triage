"""JWT Token Creation & Decoding Security Utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import logging
import jwt
from app.config import settings

logger = logging.getLogger(__name__)


def create_access_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Creates a signed JWT access token.

    Args:
        subject: Token subject (typically user ID).
        extra_claims: Additional claims to embed in the payload.

    Returns:
        Signed JWT token string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token.

    Args:
        token: JWT string to decode.

    Returns:
        Decoded claims payload dict.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid or tampered.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def create_refresh_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Creates a signed JWT refresh token.

    Args:
        subject: Token subject (typically user ID).
        extra_claims: Additional claims to embed in the payload.

    Returns:
        Signed JWT refresh token string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT refresh token.

    Args:
        token: JWT string to decode.

    Returns:
        Decoded claims payload dict.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid or tampered.
        ValueError: If the token type is not 'refresh'.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type. Expected refresh token.")
    return payload
