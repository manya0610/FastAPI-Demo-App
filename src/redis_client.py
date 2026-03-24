import logging
from collections.abc import AsyncGenerator
from typing import Protocol

import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class RedisProtocol(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def setex(self, key: str, seconds: int, value: str) -> bool: ...
    async def delete(self, key: str) -> bool: ...


class RedisClient:
    _instance: "RedisClient | None" = None
    _client: redis.Redis | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        if hasattr(self, "_initialized"):
            return
        self.redis_url = f"redis://{host}:{port}/{db}"
        self._initialized = True

    async def connect(self):
        if self._client is not None:
            return
        try:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
            await self._client.ping()
            logger.info("Redis connected: %s", self.redis_url)
        except (ConnectionError, TimeoutError):
            self._client = None
            logger.exception("Redis unavailable: %s", self.redis_url)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get(self, key: str) -> str | None:
        if not self._client:
            return None
        try:
            return await self._client.get(key)
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.warning("Redis GET failed for key %s: %s", key, e)
            return None

    async def setex(self, key: str, seconds: int, value: str) -> bool:
        if not self._client:
            return False
        try:
            await self._client.setex(key, seconds, value)
            return True
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.warning("Redis SETEX failed for key %s: %s", key, e)
            return False

    async def delete(self, key: str) -> bool:
        if not self._client:
            return False
        try:
            await self._client.delete(key)
            return True
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.warning("Redis DELETE failed for key %s: %s", key, e)
            return False


async def get_redis() -> AsyncGenerator[RedisClient, None]:
    yield RedisClient()


class MockRedisClient:
    _instance: "MockRedisClient | None" = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, should_fail: bool = False):
        if hasattr(self, "_initialized"):
            return
        logger.info("starting mock redis")
        self.storage: dict = {}
        self.should_fail: bool = should_fail
        self._initialized = True

    def reset(self):
        """Call this in test setUp to get a clean state between tests."""
        self.storage = {}
        self.should_fail = False

    async def get(self, key: str) -> str | None:
        if self.should_fail:
            return None
        return self.storage.get(key)

    async def setex(self, key: str, _: int, value: str) -> bool:
        if self.should_fail:
            return False
        self.storage[key] = value
        return True

    async def delete(self, key: str) -> bool:
        if self.should_fail:
            return False
        return self.storage.pop(key, None) is not None
