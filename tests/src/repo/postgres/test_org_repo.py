import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Org
from src.repo.postgres.org_repo import OrgRepository
from src.schemas.org_schema import OrgCreate, OrgUpdate


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_create_org(db_session: AsyncSession):
    repo = OrgRepository(db_session)
    org_data = OrgCreate(name="test_org", config={"tier": "free"})

    org = await repo.create(org_data)
    await db_session.flush()

    assert org.id is not None
    assert org.name == "test_org"
    assert org.config == {"tier": "free"}


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_create_org_without_config(db_session: AsyncSession):
    repo = OrgRepository(db_session)
    org_data = OrgCreate(name="no_config_org")

    org = await repo.create(org_data)
    await db_session.flush()

    assert org.id is not None
    assert org.config is None


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_get_org(db_session: AsyncSession):
    repo = OrgRepository(db_session)
    org = await repo.create(OrgCreate(name="get_me"))
    await db_session.commit()

    fetched = await repo.get(org.id)

    assert fetched is not None
    assert fetched.id == org.id
    assert fetched.name == "get_me"


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_list_orgs(db_session: AsyncSession):
    repo = OrgRepository(db_session)
    await repo.create(OrgCreate(name="org_a"))
    await repo.create(OrgCreate(name="org_b"))
    await db_session.commit()

    orgs = await repo.list()

    assert len(orgs) == 2
    names = {o.name for o in orgs}
    assert names == {"org_a", "org_b"}


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_update_org(db_session: AsyncSession):
    repo = OrgRepository(db_session)
    org = await repo.create(OrgCreate(name="before"))
    await db_session.commit()

    updated = await repo.update(org.id, OrgUpdate(name="after", config={"k": "v"}))
    await db_session.commit()

    assert updated.name == "after"
    assert updated.config == {"k": "v"}


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_delete_org(db_session: AsyncSession):
    repo = OrgRepository(db_session)
    org = await repo.create(OrgCreate(name="to_delete"))
    await db_session.commit()

    deleted = await repo.delete(org.id)
    await db_session.commit()

    assert deleted is True
    result = await db_session.execute(select(Org).where(Org.id == org.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_delete_nonexistent_org(db_session: AsyncSession):
    repo = OrgRepository(db_session)

    deleted = await repo.delete(99999)

    assert deleted is False
