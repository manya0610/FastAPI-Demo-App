from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from env import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # steady open connections
    max_overflow=20,  # extra burst connections
    pool_timeout=30,  # wait before giving up
    pool_recycle=1800,  # recycle stale conns every 30 min
    pool_pre_ping=True,
)

# session factory
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
