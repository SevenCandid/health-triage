"""Generic Repository Interfaces and Concrete SQLAlchemy implementations for Domain Models.

Enforces Dependency Inversion Principle using a Repository pattern for CRUD.
"""

from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

T = TypeVar("T", bound=Base)


class IRepository(Generic[T]):
    """Generic interface for standard persistence operations."""

    async def get_by_id(self, id: str) -> Optional[T]:
        raise NotImplementedError

    async def list(self, limit: int = 20, offset: int = 0) -> List[T]:
        raise NotImplementedError

    async def create(self, entity: T) -> T:
        raise NotImplementedError

    async def update(self, entity: T) -> T:
        raise NotImplementedError

    async def delete(self, id: str) -> bool:
        raise NotImplementedError


class SqlAlchemyRepository(IRepository[T], Generic[T]):
    """Concrete async SQLAlchemy implementation of repository pattern."""

    def __init__(self, session: AsyncSession, model_class: Type[T]) -> None:
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: str) -> Optional[T]:
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, limit: int = 20, offset: int = 0) -> List[T]:
        result = await self.session.execute(
            select(self.model_class).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: T) -> T:
        await self.session.flush()
        return entity

    async def delete(self, id: str) -> bool:
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False
