"""API v1 Main Router — aggregates all sub-routers."""

from fastapi import APIRouter

from app.interfaces.api.v1 import (
    analytics,
    assessment,
    auth,
    consultation,
    emergency,
    health,
    sync,
    users,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(assessment.router)
api_router.include_router(users.router)
api_router.include_router(emergency.router)
api_router.include_router(sync.router)
api_router.include_router(consultation.router)
api_router.include_router(analytics.router)
