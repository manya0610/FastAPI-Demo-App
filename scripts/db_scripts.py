import asyncio
import subprocess
import sys
from contextlib import asynccontextmanager

from sqlalchemy_utils import create_database, database_exists, drop_database

from src.database import engine, get_db
from src.schemas.org_schema import OrgCreate
from src.schemas.user_schema import UserCreate
from src.services.org_service import OrgService
from src.services.user_service import UserService


async def create_db():
    url = engine.url.set(drivername="postgresql")
    if not database_exists(url):
        print("database doesn't exist, creating it")
        create_database(url)
        print("database created")
    else:
        print("database already exists, dropping it")
        drop_database(url)
        print("database dropped, now creating it")
        create_database(url)
        print("database created")
    await engine.dispose()


def drop_db():
    if not database_exists(engine.url):
        print("database doesn't exist")
        raise Exception("database doesn't exist")
    drop_database(engine.url)
    print("database dropped")


def create_tables():
    subprocess.run(["alembic", "upgrade", "head"])


async def seed_db():
    await create_org()
    await create_user()


async def create_org():
    async_get_db = asynccontextmanager(get_db)
    async with async_get_db() as session:
        org_service = OrgService(session)
        org_data = OrgCreate(name="manish")
        await org_service.create_org(org_data)

async def create_user():
    async_get_db = asynccontextmanager(get_db)
    async with async_get_db() as session:
        user_service = UserService(session)
        user_data = UserCreate(name="manish", password="1234", org_id=1)
        await user_service.register_user(user_data)


print("argument list", sys.argv)

for arg in sys.argv[1:]:
    if arg == "create_db":
        asyncio.run(create_db())
    elif arg == "drop_db":
        drop_db()
    elif arg == "create_tables":
        create_tables()
    elif arg == "seed_db":
        asyncio.run(seed_db())
    else:
        print("invalid arg", arg)
