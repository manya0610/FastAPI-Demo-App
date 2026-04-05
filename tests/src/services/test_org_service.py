import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.db_exceptions import NotFoundError
from src.schemas.org_schema import OrgCreate, OrgPublic, OrgUpdate
from src.services.org_service import OrgService


@pytest.mark.asyncio(loop_scope="session")
async def test_create_org_returns_public_dto(db_session: AsyncSession):
    service = OrgService(db_session)

    result = await service.create_org(OrgCreate(name="acme", config={"plan": "pro"}))

    assert isinstance(result, OrgPublic)
    assert result.id is not None
    assert result.name == "acme"
    assert result.config == {"plan": "pro"}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_org_without_config(db_session: AsyncSession):
    service = OrgService(db_session)

    result = await service.create_org(OrgCreate(name="minimal"))

    assert result.config is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_org_returns_correct_org(db_session: AsyncSession):
    service = OrgService(db_session)
    created = await service.create_org(OrgCreate(name="findme"))

    result = await service.get_org(created.id)

    assert isinstance(result, OrgPublic)
    assert result.id == created.id
    assert result.name == "findme"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_org_returns_none_for_missing(db_session: AsyncSession):
    service = OrgService(db_session)

    result = await service.get_org(99999)

    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_list_orgs(db_session: AsyncSession):
    service = OrgService(db_session)
    await service.create_org(OrgCreate(name="list_org_1"))
    await service.create_org(OrgCreate(name="list_org_2"))

    results = await service.list_orgs()

    assert len(results) == 2
    names = {o.name for o in results}
    assert names == {"list_org_1", "list_org_2"}


@pytest.mark.asyncio(loop_scope="session")
async def test_list_orgs_respects_limit_and_offset(db_session: AsyncSession):
    service = OrgService(db_session)
    for i in range(5):
        await service.create_org(OrgCreate(name=f"page_org_{i}"))

    page = await service.list_orgs(limit=2, offset=1)

    assert len(page) == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_update_org(db_session: AsyncSession):
    service = OrgService(db_session)
    org = await service.create_org(OrgCreate(name="old_name"))

    updated = await service.update_org(
        org.id, OrgUpdate(name="new_name", config={"x": 1})
    )

    assert isinstance(updated, OrgPublic)
    assert updated.name == "new_name"
    assert updated.config == {"x": 1}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_org_not_found_raises(db_session: AsyncSession):
    service = OrgService(db_session)

    with pytest.raises(NotFoundError):
        await service.update_org(99999, OrgUpdate(name="ghost"))


@pytest.mark.asyncio(loop_scope="session")
async def test_remove_org_returns_true(db_session: AsyncSession):
    service = OrgService(db_session)
    org = await service.create_org(OrgCreate(name="to_delete"))

    result = await service.remove_org(org.id)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_remove_org_returns_false_for_missing(db_session: AsyncSession):
    service = OrgService(db_session)

    result = await service.remove_org(99999)

    assert result is False
