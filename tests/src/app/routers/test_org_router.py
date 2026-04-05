import pytest
from httpx import AsyncClient

from src.auth.security import create_access_token
from src.schemas.org_schema import OrgPublic
from tests.fixtures import org_fixture, user_fixture


@pytest.mark.asyncio(loop_scope="session")
async def test_create_org_201(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        "/org", json={"name": "new_org", "config": {"plan": "pro"}}, headers=headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "new_org"
    assert body["config"] == {"plan": "pro"}
    assert "id" in body


@pytest.mark.asyncio(loop_scope="session")
async def test_create_org_without_config(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        "/org", json={"name": "bare_org"}, headers=headers
    )

    assert response.status_code == 201
    assert response.json()["config"] is None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_org_422_missing_name(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post("/org", json={}, headers=headers)

    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_create_org_401_no_token(async_client: AsyncClient):
    response = await async_client.post("/org", json={"name": "unauth_org"})

    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_list_orgs(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    await org_fixture(
        db_session,
    )
    await org_fixture(
        db_session,
    )

    response = await async_client.get("/org", headers=headers)

    assert response.status_code == 200
    # At least the 2 we created plus the one from user_fixture
    assert len(response.json()) >= 2


@pytest.mark.asyncio(loop_scope="session")
async def test_get_org(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    org = await org_fixture(db_session)

    response = await async_client.get(f"/org/{org.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == org.id
    assert response.json()["name"] == org.name


@pytest.mark.asyncio(loop_scope="session")
async def test_get_org_404(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/org/99999", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_update_org(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    org = await org_fixture(db_session)

    response = await async_client.patch(
        f"/org/{org.id}",
        json={"name": "updated_org", "config": {"tier": "enterprise"}},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "updated_org"
    assert response.json()["config"] == {"tier": "enterprise"}


@pytest.mark.asyncio(loop_scope="session")
async def test_update_org_404(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.patch(
        "/org/99999", json={"name": "ghost"}, headers=headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_org(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    org = await org_fixture(db_session)

    response = await async_client.delete(f"/org/{org.id}", headers=headers)

    assert response.status_code == 204


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_org_404(db_session, async_client: AsyncClient):
    user = await user_fixture(db_session)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.delete("/org/99999", headers=headers)

    assert response.status_code == 404
