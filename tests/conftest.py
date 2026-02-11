import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.database import Base, DATABASE_URL


# 2. Force a single session-wide event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# 3. Create the engine inside a session fixture (NOT at the top of the file)
@pytest_asyncio.fixture(scope="session")
async def engine(event_loop):
    engine = create_async_engine(DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


# 4. Setup tables
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 5. Provide the session
@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session


# 6. Truncation logic
@pytest_asyncio.fixture(autouse=True)
async def truncate_tables(engine):
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
