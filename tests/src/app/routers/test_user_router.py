import asyncio
import threading
import pytest
from httpx import AsyncClient
from src.auth.security import create_access_token
from src.schemas.user_schema import UserPublic
from tests.fixtures import user_fixture
import logging




logger = logging.getLogger(__name__)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_201(db_session, async_client:AsyncClient):

    user:UserPublic = await user_fixture(db_session, )
    token = create_access_token(user.id)
    loop = asyncio.get_running_loop()
    print(f"test event loop {str(loop)},{ loop.is_running()},{threading.current_thread().name}, {type(loop).__name__}")

    data = {"name": "test_user_1", "password": "1234"}
    headers = {
        "Authorization" : f"Bearer {token}",
        "Content-Type" : "application/json"
    }
    print(async_client)
    response = await async_client.post("/user",json=data, headers=headers)
    print(response.json())
    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "name": "test_user_1",
    }

    print("first test done")

    # 422 case
    data = {"name": 1}
    headers = {
        "Authorization" : f"Bearer {token}",
        "Content-Type" : "application/json"
    }
    response = await async_client.post("/user",json=data, headers=headers)
    print(response.json())
    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_401(db_session, async_client:AsyncClient):

    user:UserPublic = await user_fixture(db_session)
    token = create_access_token(user.id)

    data = {"name": "test_user_1", "password": "1234"}
    headers = {
        "Authorization" : f"Bearer",
        "Content-Type" : "application/json"
    }
    response = await async_client.post("/user",json=data, headers=headers)
    print(response.json())
    assert response.status_code == 401