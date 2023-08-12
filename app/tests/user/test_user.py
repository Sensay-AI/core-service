from http import HTTPStatus

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.routes.api_v1.endpoints.auth import check_user
from app.schemas.users import Auth0User

APPLICATION_JSON = "application/json"


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[check_user] = override_dependency
    async with AsyncClient(app=app, base_url="http://test") as testClient:
        yield testClient


async def override_dependency():
    return Auth0User(sub="user1234", permissions=["read", "write"])


@pytest.mark.asyncio()
async def test_get_user_info_without_token(client):
    app.dependency_overrides[check_user] = check_user
    response = await client.get(
        "/api/v1/user/",
        headers={
            "Accept": APPLICATION_JSON,
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio()
async def test_get_user_info(client):
    app.dependency_overrides[check_user] = override_dependency
    response = await client.get(
        "/api/v1/user/",
        headers={
            "Accept": APPLICATION_JSON,
            "Authorization": "Bearer xyz",
        },
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio()
async def test_create_user(client):
    app.dependency_overrides[check_user] = override_dependency
    resp = await client.post(
        "/api/v1/user/create",
        headers={
            "Accept": APPLICATION_JSON,
            "Authorization": "Bearer xyz",
        },
        json={
            "full_name": "string",
            "email": "1234@gmail.com",
            "country": "vn",
            "language": "eng",
            "phone_number": "+84123456789",
            "nickname": "Bee",
            "date_of_birth": "2005-07-26",
        },
    )
    assert resp.status_code in (HTTPStatus.OK, HTTPStatus.NOT_FOUND)
