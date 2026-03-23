from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repo.postgres.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> "UserRepository":
        super().__init__(User, session)


    async def get_by_username(self, username: str) -> User | None:
        """Fetch the raw SQLAlchemy model by username."""
        query = select(User).where(User.name == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
