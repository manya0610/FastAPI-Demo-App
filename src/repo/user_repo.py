from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.exceptions.db_exceptions import NotFoundError
from src.repo.base_repo import BaseRepository
from src.schemas.user_schema import UserCreate, UserUpdate


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> "UserRepository":
        super().__init__(User, session)

    async def create(self, data: UserCreate) -> User:
        """Create user and return without commit"""
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user_id: int, data: UserUpdate) -> User:
        """Update user and return without commit"""
        update_data = data.model_dump(exclude_unset=True)
        query = (
            update(User).where(User.id == user_id).values(**update_data).returning(User)
        )
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            error_message = f"User with id {user_id} not found"
            raise NotFoundError(error_dict={
                "error" : error_message
            })
        return user
