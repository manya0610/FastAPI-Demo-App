import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.routers.deps import auth_required, get_user_service
from src.exceptions.db_exceptions import NotFoundError
from src.rmq import get_rmq_publisher
from src.rmq.publisher import RabbitMQPublisher
from src.schemas.user_schema import UserCreate, UserPublic, UserUpdate
from src.services.user_service import UserService

user_router = APIRouter(
    prefix="/user", tags=["users"], dependencies=[Depends(auth_required)]
)

logger = logging.getLogger(__name__)


@user_router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        user = await service.register_user(user_data)
        return UserPublic.model_validate(user)
    except Exception as e:
        logger.exception("error while creating user")
        raise HTTPException(status_code=500, detail=str(e)) from e


@user_router.get("")
async def list_users(
    limit: Annotated[int, Query(le=100)] = 100,
    offset: int = 0,
    service: UserService = Depends(get_user_service),
) -> list[UserPublic]:
    try:
        # Now calling the service's list method
        users = await service.list_active_users(limit=limit, offset=offset)
        return [UserPublic.model_validate(u) for u in users]
    except Exception as e:
        logger.exception("error while listing user")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@user_router.get("/{user_id}")
async def get_user(
    user_id: int, service: UserService = Depends(get_user_service)
) -> UserPublic:
    try:
        # Now calling the service's get method
        user = await service.get_user_profile(user_id)
        if not user:
            raise NotFoundError
        return UserPublic.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="User not found") from e
    except Exception as e:
        logger.exception("error while fetching user")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@user_router.patch("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        user = await service.update_user_info(user_id, user_data)
        return UserPublic.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="User not found") from e
    except Exception as e:
        logger.exception("error while updating user")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@user_router.post("/register-async")
async def register_user_async(
    user_data: UserCreate, publisher: RabbitMQPublisher = Depends(get_rmq_publisher)
):
    # Instead of calling UserService (which hits the DB now),
    # we just toss the data into RabbitMQ and return 202 Accepted.
    await publisher.publish(user_data.model_dump())

    return {"message": "User registration is being processed in the background"}
