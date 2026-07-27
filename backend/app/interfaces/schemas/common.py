"""Common Pydantic v2 Schemas — Health Check & Problem Details."""

from typing import Optional
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Health check endpoint response schema."""

    status: str = "ok"
    service: str
    version: str
    environment: str
    database: str = "unknown"


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details error response schema."""

    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
