from collections.abc import Sequence
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure Base is the actual DeclarativeBase class
from src.database.models import Base
from src.exceptions.db_exceptions import NotFoundError

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session


    async def create(self, data: BaseModel) -> ModelType:
        """Create user and return without commit"""
        obj = self.model(**data.model_dump())
        self.session.add(obj)
        # raise Exception("boom")
        return obj

    async def get(self, obj_id: int) -> ModelType | None:
        """Returns a single model instance or None."""
        query = select(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        """Returns a sequence of model instances."""
        query = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(query)
        # result.scalars().all() returns a list which satisfies Sequence
        return result.scalars().all()

    async def update(self, obj_id: int, data: BaseModel) -> ModelType:
        """Update obj and return with commit"""
        update_data = data.model_dump(exclude_unset=True)
        query = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**update_data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()
        if not obj:
            error_message = f"User with id {obj_id} not found"
            raise NotFoundError(error_dict={"error": error_message})
        return obj

    async def delete(self, obj_id: int) -> bool:
        """Deletes an object and returns True if successful."""
        query = delete(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(query)
        return result.rowcount > 0
