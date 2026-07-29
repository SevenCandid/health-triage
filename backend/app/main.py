"""Health Triage Assistant — FastAPI Application Entry Point.

This module initializes the FastAPI application with:
  - CORS middleware (configured for the React PWA frontend)
  - Global exception handlers (RFC 7807 problem details format)
  - Async lifespan lifecycle manager (startup/shutdown hooks)
  - Auto-creation of database tables on first startup (dev mode)
  - Database seeding of baseline rule trees and dev admin user
  - Inclusion of all API v1 routers
  - Polished Swagger UI and OpenAPI 3.1 documentation

Architecture: Clean Architecture + ASGI (Uvicorn/Gunicorn)
See /docs/BackendArchitecture.md for full design specification.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.base import Base
from app.infrastructure.database.seed import run_seeds
from app.infrastructure.database.session import async_session_factory, engine
from app.infrastructure.logging_config import setup_logging
from app.interfaces.api.middleware.exception_handler import register_exception_handlers
from app.interfaces.api.middleware.request_id_middleware import RequestIDMiddleware
from app.interfaces.api.v1.router import api_router

# Initialize structured logging before any other module-level code
setup_logging()
logger = logging.getLogger(__name__)


TAGS_METADATA = [
    {
        "name": "Health",
        "description": "Liveness and database connectivity probes for health monitoring.",
    },
    {
        "name": "Authentication",
        "description": "User registration, login, and JWT access token issuance endpoints.",
    },
    {
        "name": "Assessment API",
        "description": "Interactive symptom evaluation session workflow endpoints.",
    },
    {
        "name": "Triage",
        "description": "Clinical decision tree evaluation and rule tree configuration endpoints.",
    },
    {
        "name": "User Profile",
        "description": "Health profile and emergency contact management endpoints.",
    },
    {
        "name": "Emergency",
        "description": "GPS-tagged emergency dispatch alert triggering and SMS payload generation.",
    },
    {
        "name": "Sync",
        "description": "Offline outbox batch synchronization endpoints for PWA clients.",
    },
    {
        "name": "Consultation & Voice",
        "description": "Gemini AI explanation streaming and speech-to-text voice consultation endpoints.",
    },
    {
        "name": "Analytics",
        "description": "Anonymized aggregate triage statistics and clinical metrics dashboard.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI Async Lifespan Context Manager.

    Handles startup and shutdown events for the application lifecycle:
      - Startup: Creates all database tables (dev only), runs seed scripts.
      - Shutdown: Disposes the async database engine connection pool.
    """
    # ---- STARTUP ----
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")

    if settings.ENVIRONMENT == "production":
        import subprocess
        import sys
        from sqlalchemy import text
        logger.info("Production mode: Running Alembic migrations...")
        result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Alembic migrations completed successfully.")
        else:
            logger.error(f"Alembic migrations failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
            logger.info("Applying emergency fallback schema patch...")
            try:
                async with engine.begin() as conn:
                    # Drop the fk constraint safely if it exists (requires DO block in PG)
                    await conn.execute(text('''
                        DO $$
                        BEGIN
                            IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_assessment_responses_session_id' AND table_name = 'assessment_responses') THEN
                                ALTER TABLE assessment_responses DROP CONSTRAINT fk_assessment_responses_session_id;
                            END IF;
                        END $$;
                    '''))
                    await conn.execute(text("DELETE FROM assessment_responses"))
                    # Add column if it doesn't exist
                    await conn.execute(text('''
                        DO $$
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assessment_responses' AND column_name='conversation_id') THEN
                                ALTER TABLE assessment_responses ADD COLUMN conversation_id VARCHAR(36);
                                ALTER TABLE assessment_responses ALTER COLUMN conversation_id SET NOT NULL;
                            END IF;
                        END $$;
                    '''))
                    # Add symptom_id column if it doesn't exist
                    await conn.execute(text('''
                        DO $$
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assessment_responses' AND column_name='symptom_id') THEN
                                ALTER TABLE assessment_responses ADD COLUMN symptom_id VARCHAR(36);
                            END IF;
                        END $$;
                    '''))
                    # Drop old session_id column if it exists
                    await conn.execute(text('''
                        DO $$
                        BEGIN
                            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assessment_responses' AND column_name='session_id') THEN
                                ALTER TABLE assessment_responses DROP COLUMN session_id;
                            END IF;
                        END $$;
                    '''))
                logger.info("Emergency fallback schema patch applied successfully.")
            except Exception as e:
                logger.error(f"Emergency fallback failed: {e}")

    if settings.ENVIRONMENT in ("development", "testing"):
        logger.info("Dev mode: auto-creating database tables via SQLAlchemy metadata...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified/created.")

        # Run seed scripts to populate baseline data
        async with async_session_factory() as session:
            await run_seeds(session)

    # Always ensure PostgreSQL ENUMs are up to date on startup
    # We do this here outside of Alembic to bypass 'ALTER TYPE cannot run in transaction'
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            autocommit_conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
            if autocommit_conn.dialect.name == "postgresql":
                logger.info("Ensuring PostgreSQL Enum values exist...")
                for val in ['ACTIVE', 'ARCHIVED', 'SYNCED']:
                    try:
                        await autocommit_conn.execute(text(f"ALTER TYPE session_status_enum ADD VALUE IF NOT EXISTS '{val}'"))
                    except Exception as e:
                        logger.warning(f"Enum update for {val} failed (might already exist or PG < 12): {e}")
    except Exception as e:
        logger.error(f"Failed to update PostgreSQL enums on startup: {e}")

    logger.info("Application startup complete. Ready to accept requests.")

    yield  # Application serves requests here

    # ---- SHUTDOWN ----
    logger.info("Application shutdown initiated...")
    await engine.dispose()
    logger.info("Database connection pool disposed. Goodbye.")


# ---------------------------------------------------------------------------
# FastAPI Application Instantiation
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Health Triage Assistant API",
    version=settings.VERSION,
    description=(
        "### Offline-First Health Triage Assistant API\n\n"
        "Production-grade RESTful API serving clinical triage evaluation, emergency dispatch, "
        "health profile management, and PWA outbox sync.\n\n"
        "**Key Architectural Highlights:**\n"
        "- **Dual Intelligence**: Deterministic rule engine + optional Gemini AI enhancement\n"
        "- **Multilingual**: BCP 47 language tagging (English `en`, Twi `tw`)\n"
        "- **Clean Architecture**: Isolated domain models, services, and interface adapters\n"
        "- **RFC 7807 Errors**: Structured problem details error payloads\n"
    ),
    openapi_tags=TAGS_METADATA,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS Middleware — Allow React PWA frontend origins
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(RequestIDMiddleware)

# ---------------------------------------------------------------------------
# Global Exception Handlers (RFC 7807 Problem Details)
# ---------------------------------------------------------------------------
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# API v1 Routers
# ---------------------------------------------------------------------------
app.include_router(api_router)


# ---------------------------------------------------------------------------
# Root Health Probe (for k8s/docker liveness checks at /)
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def root_health_probe() -> JSONResponse:
    """Root liveness probe — returns 200 OK if DB is healthy, else 503."""
    try:
        async with async_session_factory() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error(f"Root health probe failed: {exc}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": "Database unavailable"}
        )

    return JSONResponse(
        content={
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "ok",
            "docs": "/docs" if settings.DEBUG else "disabled in production",
        }
    )
