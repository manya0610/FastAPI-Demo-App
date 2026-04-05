from src.schemas.org_schema import OrgCreate, OrgPublic
from src.schemas.user_schema import UserCreate, UserPublic
from src.services.org_service import OrgService
from src.services.user_service import UserService


async def org_fixture(db_session, org: OrgCreate = None) -> OrgPublic:
    service = OrgService(db_session)
    if not org:
        org = OrgCreate(name="test_org")
    return await service.create_org(org)


async def user_fixture(db_session, user: UserCreate = None) -> UserPublic:
    org = await org_fixture(db_session)
    service = UserService(db_session)
    if not user:
        user = UserCreate(name="db_tester", password="1234", org_id=org.id)
    return await service.register_user(user)
