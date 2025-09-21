import logging
from collections.abc import Sequence

from sqlalchemy import CursorResult, ScalarResult, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.exceptions.db_exceptions import DatabaseError, NotFoundError
from src.schemas.user_schema import UserCreate, UserUpdate

logging.basicConfig()
logger = logging.getLogger(__name__)


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    try:
        query = insert(User).values(data.model_dump()).returning(User)
        user: User = await session.scalar(query)
        await session.commit()
        return user
    except Exception as e:
        await session.rollback()
        logger.exception("Error creating user=%s", data, stack_info=True)
        raise DatabaseError from e


async def get_user(session: AsyncSession, user_id: int) -> User:
    try:
        query = select(User).where(User.id == user_id)
        result: ScalarResult = await session.scalars(query)
        user = result.one_or_none()
        if user is None:
            logger.exception("user with id=%s not found", user_id, stack_info=True)
            raise NotFoundError
        return user
    except NotFoundError:
        raise
    except Exception as e:
        logger.exception(
            "Error while getting user with id=%s",
            user_id,
            stack_info=True,
        )
        raise DatabaseError from e


# List all users, returning a list of User objects
async def list_users(
    session: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> list[User]:
    try:
        query = select(User).limit(limit).offset(offset)
        response: ScalarResult = await session.scalars(query)
        users: Sequence[User] = response.all()
        return users
    except Exception as e:
        logger.exception("Error while listing users", stack_info=True)
        raise DatabaseError from e


async def update_user(session: AsyncSession, user_id: int, data: UserUpdate) -> User:
    try:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(**data.model_dump())
            .returning(User)
        )
        user: User = await session.scalar(query)
        await session.commit()
        if user is None:
            logger.warning("No user found with id=%s to update", user_id)
            raise NotFoundError
        return user
    except NotFoundError:
        raise
    except Exception as e:
        await session.rollback()
        logger.exception(
            "Error updating user with id=%s, data=%s",
            user_id,
            data,
            stack_info=True,
        )
        raise DatabaseError from e


async def delete_user(session: AsyncSession, user_id: int) -> int:
    try:
        query = delete(User).where(User.id == user_id)
        response: CursorResult = await session.execute(query)
        await session.commit()

        if response.rowcount == 0:
            logger.warning("No user found with id=%s to delete", user_id)
            raise NotFoundError
        return response.rowcount
    except NotFoundError:
        raise
    except Exception as e:
        await session.rollback()
        logger.exception("Error deleting user with id=%s", user_id, stack_info=True)
        raise DatabaseError from e
