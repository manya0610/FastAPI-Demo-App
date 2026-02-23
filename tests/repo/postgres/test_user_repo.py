import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.redis_client import MockRedisWrapper
from src.repo.postgres.user_repo import UserRepository
from src.schemas.user_schema import UserCreate, UserUpdate
from src.services.user_service import UserService


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_create_user(db_session: AsyncSession):
    """Test raw repository creation without service overhead."""
    repo = UserRepository(db_session)
    user_data = UserCreate(name="db_tester", password="1234")

    user = await repo.create(user_data)
    await db_session.flush()  # Sync with DB but don't commit yet

    assert user.id is not None
    assert user.name == "db_tester"


@pytest.mark.asyncio(loop_scope="session")
async def test_service_register_user_persistence(
    db_session: AsyncSession, mock_redis: MockRedisWrapper
):
    """Test that the Service Layer correctly commits to the DB."""
    service = UserService(db_session, mock_redis)
    user_data = UserCreate(name="service_user",password="1234")

    # Service calls repo.create and session.commit()
    new_user = await service.register_user(user_data)

    # Verify persistence by starting a fresh query
    result = await db_session.execute(select(User).where(User.id == new_user.id))
    persisted_user = result.scalar_one_or_none()

    assert persisted_user is not None
    assert persisted_user.name == "service_user"


@pytest.mark.asyncio(loop_scope="session")
async def test_db_isolation_and_truncation(db_session: AsyncSession):
    """
    Proof of isolation: Even if previous tests added users,
    this test must see an empty table due to the truncate fixture.
    """
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_service_update_user(db_session: AsyncSession, mock_redis):
    """Test updating existing data through the service layer."""
    service = UserService(db_session, mock_redis)
    # Setup
    initial_user = await service.register_user(UserCreate(name="old_me", password="1234"))

    # Update
    update_data = UserUpdate(name="new_me")
    updated_user = await service.update_user_info(initial_user.id, update_data)

    assert updated_user.name == "new_me"
