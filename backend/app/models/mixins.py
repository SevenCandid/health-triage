"""Reusable SQLAlchemy 2.0 Model Mixins.

Provides composable mixin classes that inject standard column sets
(UUID PKs, timestamps, soft deletes) into any ORM model via inheritance.

Usage:
    class MyModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
        __tablename__ = "my_table"
        ...

Design rationale: Mixins use declared_attr and mapped_column() with
SQLAlchemy 2.0 typing so that type checkers see all columns correctly.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


def _utc_now() -> datetime:
    """Returns current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class UUIDPrimaryKeyMixin:
    """Injects a UUID string primary key column named `id`.

    Uses String(36) for cross-database compatibility (SQLite + PostgreSQL).
    In production on PostgreSQL, consider using native UUID type via
    TypeDecorator for true UUID storage — see /docs/CodingStandards.md.
    """

    @declared_attr
    def id(cls) -> Mapped[str]:  # noqa: N805
        return mapped_column(
            String(36),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            index=True,
            comment="Primary key — UUID v4 string representation.",
        )


class TimestampMixin:
    """Injects `created_at` and `updated_at` timezone-aware timestamp columns.

    - `created_at`: Set once on INSERT via server_default.
    - `updated_at`: Updated on every UPDATE via onupdate.
    """

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:  # noqa: N805
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=_utc_now,
            server_default=func.now(),
            comment="UTC timestamp when the record was created.",
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:  # noqa: N805
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=_utc_now,
            server_default=func.now(),
            onupdate=_utc_now,
            comment="UTC timestamp of the most recent update.",
        )


class SoftDeleteMixin:
    """Injects soft-delete support via `is_deleted` flag and `deleted_at` timestamp.

    Soft-deleted records are retained in the database for audit compliance
    but excluded from all standard query filters.

    Usage pattern in repositories:
        .where(ModelClass.is_deleted == False)

    See /docs/Privacy.md — Right to Erasure: hard delete replaces soft delete
    for users exercising GDPR Article 17 rights.
    """

    @declared_attr
    def is_deleted(cls) -> Mapped[bool]:  # noqa: N805
        return mapped_column(
            Boolean,
            nullable=False,
            default=False,
            server_default=text("false"),
            index=True,
            comment="Soft-delete flag. True means the record is logically deleted.",
        )

    @declared_attr
    def deleted_at(cls) -> Mapped[Optional[datetime]]:  # noqa: N805
        return mapped_column(
            DateTime(timezone=True),
            nullable=True,
            default=None,
            comment="UTC timestamp when this record was soft-deleted. NULL if active.",
        )

    def soft_delete(self) -> None:
        """Marks this record as soft-deleted with current UTC timestamp."""
        self.is_deleted = True
        self.deleted_at = _utc_now()

    def restore(self) -> None:
        """Restores a soft-deleted record to active status."""
        self.is_deleted = False
        self.deleted_at = None
