import pytest
from src.services.user_service import UserService
from src.schemas.user_schema import UserCreate, UserPublic, UserUpdate


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_returns_pydantic_and_caches(db_session, mock_redis):
    service = UserService(db_session, mock_redis)

    # 1. Setup: Create a user
    created_dto = await service.register_user(UserCreate(name="test_user"))

    # 2. Action: Get the profile
    result = await service.get_user_profile(created_dto.id)

    # 3. Assertions
    assert isinstance(result, UserPublic)  # Verify DTO return type
    assert result.name == "test_user"

    # Verify it was cached in our mock
    cache_val = await mock_redis.get(f"user:{created_dto.id}")
    assert cache_val is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_graceful_degradation_when_redis_fails(db_session, failing_redis):
    """
    Test that even if Redis 'fails' (returns None/Error),
    the service still returns data from the DB.
    """
    service = UserService(db_session, failing_redis)

    # Setup: Create user directly in DB (simulating existing data)
    created_dto = await service.register_user(UserCreate(name="resilient_user"))

    # Action: Get profile while Redis is 'broken'
    result = await service.get_user_profile(created_dto.id)

    # Assertions
    assert result is not None
    assert result.name == "resilient_user"
    # The app didn't crash! That's the win.


@pytest.mark.asyncio(loop_scope="session")
async def test_update_invalidates_cache(db_session, mock_redis):
    service = UserService(db_session, mock_redis)
    user = await service.register_user(UserCreate(name="old_name"))

    # Prime the cache
    await service.get_user_profile(user.id)
    assert await mock_redis.get(f"user:{user.id}") is not None

    # Update user
    await service.update_user_info(user.id, UserUpdate(name="new_name"))

    # Verify cache was updated
    cached_user = await mock_redis.get(f"user:{user.id}")
    assert cached_user is not None
