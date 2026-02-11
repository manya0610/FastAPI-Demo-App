from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repo.user_repo import UserRepository
from src.schemas.user_schema import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> "UserService":
        self.session = session
        self.repo = UserRepository(session)

    async def register_user(self, data: UserCreate) -> User:
        """Create User and commit to db"""
        user = await self.repo.create(data)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_profile(self, user_id: int) -> User | None:
        """Fetch User from DB"""
        # Business logic could go here (e.g., check if user is active)
        return await self.repo.get(user_id)

    async def list_active_users(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[User]:
        """Fetch list of Users"""
        return await self.repo.list(limit=limit, offset=offset)

    async def update_user_info(self, user_id: int, data: UserUpdate) -> User:
        """Update User and Commit"""
        user = await self.repo.update(user_id, data)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def remove_user(self, user_id: int) -> bool:
        """Delete User"""
        success = await self.repo.delete(user_id)
        if success:
            await self.session.commit()
        return success
