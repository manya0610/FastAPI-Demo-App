from src.database.models import User
from src.services.user_service import UserService
from src.schemas.user_schema import UserCreate, UserPublic


async def user_fixture(db_session, user:UserCreate=None) -> UserPublic:
    service = UserService(db_session)
    if not user:
        user = UserCreate(name="db_tester", password="1234")
    return await service.register_user(user)
