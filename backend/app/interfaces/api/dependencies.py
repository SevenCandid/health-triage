"""Dependency Injection Providers.

Centralizes all FastAPI dependency factories for service and repository
instances, enforcing Clean Architecture injection patterns.

Usage in routers:
    from app.interfaces.api.dependencies import get_triage_service
    ...
    async def route(service = Depends(get_triage_service)):
"""

import logging
from typing import Annotated, AsyncGenerator, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_async_db
from app.infrastructure.security.jwt import decode_access_token
from app.interfaces.repositories.sqlalchemy_repos import (
    SqlAlchemyEmergencyLogRepository,
    SqlAlchemyHealthProfileRepository,
    SqlAlchemyRuleTreeRepository,
    SqlAlchemyTriageSessionRepository,
    SqlAlchemyUserRepository,
)
from app.use_cases.analytics_service import AnalyticsService
from app.use_cases.auth_service import AuthService
from app.use_cases.emergency_service import EmergencyService
from app.use_cases.profile_service import ProfileService
from app.use_cases.sync_service import SyncService
from app.services.triage_service import TriageService

logger = logging.getLogger(__name__)
security_scheme = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Database Session (provided by session.py via FastAPI DI)
# ---------------------------------------------------------------------------
DbSession = Annotated[AsyncSession, Depends(get_async_db)]


# ---------------------------------------------------------------------------
# Repository Providers (constructed fresh per request using DB session)
# ---------------------------------------------------------------------------
def get_user_repo(db: DbSession) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(db)


def get_health_profile_repo(db: DbSession) -> SqlAlchemyHealthProfileRepository:
    return SqlAlchemyHealthProfileRepository(db)


def get_triage_session_repo(db: DbSession) -> SqlAlchemyTriageSessionRepository:
    return SqlAlchemyTriageSessionRepository(db)


def get_rule_tree_repo(db: DbSession) -> SqlAlchemyRuleTreeRepository:
    return SqlAlchemyRuleTreeRepository(db)


def get_emergency_log_repo(db: DbSession) -> SqlAlchemyEmergencyLogRepository:
    return SqlAlchemyEmergencyLogRepository(db)


# ---------------------------------------------------------------------------
# Service Providers (use cases that receive repo instances)
# ---------------------------------------------------------------------------
def get_auth_service(
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repo=user_repo)


def get_triage_service(db: DbSession) -> TriageService:
    return TriageService(db_session=db)


def get_profile_service(
    profile_repo: SqlAlchemyHealthProfileRepository = Depends(get_health_profile_repo),
) -> ProfileService:
    return ProfileService(profile_repo=profile_repo)


def get_emergency_service(
    emergency_repo: SqlAlchemyEmergencyLogRepository = Depends(get_emergency_log_repo),
) -> EmergencyService:
    return EmergencyService(emergency_repo=emergency_repo)


def get_sync_service(
    triage_repo: SqlAlchemyTriageSessionRepository = Depends(get_triage_session_repo),
) -> SyncService:
    return SyncService(triage_repo=triage_repo)


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()



# ---------------------------------------------------------------------------
# JWT Authentication Dependency
# ---------------------------------------------------------------------------
async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> str:
    """Decodes the bearer JWT and returns the authenticated user ID.

    Raises:
        HTTPException 401: If no token or invalid token is provided.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide an Authorization: Bearer <token> header.",
        )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload["sub"]
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )


# Optional auth: returns user_id or None (for anonymous-allowed endpoints)
async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[str]:
    """Returns the user ID from the JWT if present, otherwise None."""
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return payload.get("sub")
    except jwt.InvalidTokenError:
        return None
