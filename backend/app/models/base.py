"""Canonical SQLAlchemy 2.0 Declarative Base for domain models.

This Base is the single source of truth for Alembic metadata scanning.
All models in app/models/ inherit from this Base.

The legacy Base in app/infrastructure/database/base.py is kept for
backward compatibility with the foundation layer — do not mix them.
"""

from sqlalchemy.orm import DeclarativeBase, registry


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 Declarative Base for all domain models.

    Provides:
      - Unified metadata object for Alembic migrations
      - Type annotation map for Mapped[...] columns
      - Registry for relationship resolution
    """

    registry = registry()
