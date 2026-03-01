from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure Base is the actual DeclarativeBase class
from src.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, obj_id: int) -> ModelType | None:
        """Returns a single model instance or None."""
        query = select(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        """Returns a sequence of model instances."""
        query = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(query)
        # result.scalars().all() returns a list which satisfies Sequence
        return result.scalars().all()

    async def delete(self, obj_id: int) -> bool:
        """Deletes an object and returns True if successful."""
        query = delete(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
