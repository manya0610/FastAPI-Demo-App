import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.db_exceptions import NotFoundError
from src.schemas.user_schema import UserCreate, UserUpdate
from src.services.user_service import UserService


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_service(db_session: AsyncSession):
    """Verifies service creates user and commits transaction."""
    service = UserService(db_session)
    user_in = UserCreate(name="service_admin")

    # The service handles the commit internally
    user = await service.register_user(user_in)

    assert user.id is not None
    assert user.name == "service_admin"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_profile_not_found(db_session: AsyncSession):
    """Verifies service returns None for non-existent users."""
    service = UserService(db_session)

    # Database is fresh/empty due to truncation
    user = await service.get_user_profile(999)
    assert user is None


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_info_not_found(db_session: AsyncSession):
    """Verifies service propagates NotFoundError from repository."""
    service = UserService(db_session)
    update_data = UserUpdate(name="ghost")

    with pytest.raises(NotFoundError):
        await service.update_user_info(999, update_data)


@pytest.mark.asyncio(loop_scope="session")
async def test_list_active_users_multiple(db_session: AsyncSession):
    """Verifies listing and pagination logic."""
    service = UserService(db_session)

    # Create two users
    await service.register_user(UserCreate(name="u1"))
    await service.register_user(UserCreate(name="u2"))

    users = await service.list_active_users(limit=1)
    assert len(users) == 1
    assert users[0].name == "u1"


@pytest.mark.asyncio(loop_scope="session")
async def test_remove_user_success(db_session: AsyncSession):
    """Verifies delete logic and commit."""
    service = UserService(db_session)
    user = await service.register_user(UserCreate(name="bye"))

    success = await service.remove_user(user.id)
    assert success is True

    # Double check they are gone
    deleted_user = await service.get_user_profile(user.id)
    assert deleted_user is None
