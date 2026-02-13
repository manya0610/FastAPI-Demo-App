import logging
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.redis_client import RedisClientWrapper
from src.repo.postgres.user_repo import UserRepository
from src.schemas.user_schema import UserCreate, UserPublic, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self, session: AsyncSession, redis: RedisClientWrapper
    ) -> "UserService":
        self.session = session
        self.repo = UserRepository(session)
        self.redis = redis

    async def register_user(self, data: UserCreate) -> UserPublic:
        user_model = await self.repo.create(data)
        await self.session.commit()
        await self.session.refresh(user_model)
        user = UserPublic.model_validate(user_model)
        cache_key = f"user:{user.id}"
        await self.redis.setex(cache_key, 3600, user.model_dump_json())
        logger.info("user created, id=%s", user.id)
        return user

    async def get_user_profile(self, user_id: int) -> UserPublic | None:
        cache_key = f"user:{user_id}"

        # 1. Try Cache (Fastest)
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            user = UserPublic.model_validate_json(cached_data)
            logger.debug("cache hit for user, id=%s", user_id)
            return user

        # 2. Try DB
        logger.debug("cache miss for user, id=%s", user_id)
        user = await self.repo.get(user_id)
        if not user:
            return None

        # 3. Convert to Pydantic & Cache
        user = UserPublic.model_validate(user)
        await self.redis.setex(cache_key, 3600, user.model_dump_json())
        logger.debug("returning user from db, id=%s", user_id)
        return user

    async def list_active_users(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[UserPublic]:
        users = await self.repo.list(limit=limit, offset=offset)
        return [UserPublic.model_validate(u) for u in users]

    async def update_user_info(self, user_id: int, data: UserUpdate) -> UserPublic:
        cache_key = f"user:{user_id}"
        user_model = await self.repo.update(user_id, data)
        await self.session.commit()

        # Clear cache so next 'get' sees fresh data
        await self.redis.delete(cache_key)

        user = UserPublic.model_validate(user_model)
        await self.redis.setex(cache_key, 3600, user.model_dump_json())
        logger.info("user updated, id=%s", user_id)
        return user

    async def remove_user(self, user_id: int) -> bool:
        """Delete User"""
        success = await self.repo.delete(user_id)
        if success:
            await self.session.commit()
            logger.info("user deleted, id=%s", user_id)
            await self.redis.delete(f"user:{user_id}")
        return success
