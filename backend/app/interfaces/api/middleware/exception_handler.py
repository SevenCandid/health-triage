"""Global Exception Handling Middleware.

Catches all application-level exceptions and converts them into
RFC 7807 Problem Details JSON responses.

See /docs/Security.md and /docs/APIReference.md — Section 3.3.
"""

import logging
from typing import Any

import jwt
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attaches all global exception handlers to the FastAPI application."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        logger.warning(f"ValueError on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "type": "https://api.healthtriage.org/errors/bad-request",
                "title": "Bad Request",
                "status": 400,
                "detail": str(exc),
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError) -> JSONResponse:
        logger.warning(f"PermissionError on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=403,
            content={
                "type": "https://api.healthtriage.org/errors/forbidden",
                "title": "Forbidden",
                "status": 403,
                "detail": str(exc),
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(jwt.ExpiredSignatureError)
    async def jwt_expired_handler(
        request: Request, exc: jwt.ExpiredSignatureError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "type": "https://api.healthtriage.org/errors/token-expired",
                "title": "Token Expired",
                "status": 401,
                "detail": "Your access token has expired. Please log in again.",
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(jwt.InvalidTokenError)
    async def jwt_invalid_handler(
        request: Request, exc: jwt.InvalidTokenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "type": "https://api.healthtriage.org/errors/invalid-token",
                "title": "Invalid Token",
                "status": 401,
                "detail": "The provided authentication token is invalid.",
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "type": "https://api.healthtriage.org/errors/internal-server-error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred. Please try again later.",
                "instance": str(request.url.path),
            },
        )
