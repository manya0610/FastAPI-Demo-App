from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.database.models import User
from src.exceptions.db_exceptions import NotFoundError
from src.repo import user_repo
from src.schemas.user_schema import UserCreate, UserPublic, UserUpdate

user_router = APIRouter(prefix="/user")


@user_router.post("")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    try:
        user: User = await user_repo.create_user(db, user)
        return UserPublic(**user.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500) from e


@user_router.get("")
async def list_users(
    db: AsyncSession = Depends(get_db),
    limit: Annotated[int, Query(le=100)] = 100,
    offset: int = 0,
) -> list[UserPublic]:
    try:
        users: list[User] = await user_repo.list_users(db, limit, offset)
        return [UserPublic(**user.__dict__) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500) from e


@user_router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserPublic:
    try:
        user: User = await user_repo.get_user(db, user_id)
        return UserPublic(**user.__dict__)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="user not found") from None
    except Exception as e:
        raise HTTPException(status_code=500) from e


@user_router.patch("/{user_id}")
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    try:
        user: User = await user_repo.update_user(db, user_id, user)
        return UserPublic(**user.__dict__)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="user not found") from None
    except Exception as e:
        raise HTTPException(status_code=500) from e


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    try:
        await user_repo.delete_user(db, user_id)
        return {"details": "user deleted"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="user not found") from None
    except Exception as e:
        raise HTTPException(status_code=500) from e
