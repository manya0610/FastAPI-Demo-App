import logging
from collections.abc import AsyncGenerator

import redis.asyncio as redis
from redis import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_url = f"redis://{host}:{port}/{db}"
        self.client: redis.Redis | None = None

    async def connect(self):
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            # Verify connection
            await self.client.ping()
            logger.info("Redis is connected")
        except (ConnectionError, TimeoutError):
            logger.exception("Redis is unavailable")

    async def close(self):
        if self.client:
            await self.client.close()


# Global instance
redis_manager = RedisManager()


# Dependency for FastAPI
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    if redis_manager.client is None:
        await redis_manager.connect()
    yield redis_manager.client


class RedisClientWrapper:
    def __init__(self, client: Redis | None):
        self.client = client

    async def get(self, key: str) -> str | None:
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.warning("Redis GET failed for key %s: %s", key, e)
            return None

    async def setex(self, key: str, seconds: int, value: str) -> bool:
        if not self.client:
            return False
        try:
            await self.client.setex(key, seconds, value)
            return True
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.warning("Redis SETEX failed for key %s: %s", key, e)
            return False

    async def delete(self, key: str) -> bool:
        if not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.warning("Redis DELETE failed for key %s: %s", key, e)
            return False


class MockRedisWrapper:
    """A simple in-memory version of our Redis wrapper for testing."""

    def __init__(self, should_fail: bool = False):
        self.storage = {}
        self.should_fail = should_fail

    async def get(self, key: str):
        if self.should_fail:
            return None
        return self.storage.get(key)

    async def setex(self, key: str, _: int, value: str):
        if self.should_fail:
            return False
        self.storage[key] = value
        return True

    async def delete(self, key: str):
        if self.should_fail:
            return False
        return self.storage.pop(key, None) is not None
