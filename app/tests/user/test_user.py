from http import HTTPStatus
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.auth0.auth0 import Auth0Service
from app.main import app
from app.models.schemas.users import Auth0User
from app.repositories.user_repository import UserRepository

APPLICATION_JSON = "application/json"


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_user_info_without_token(client):
    response = client.get(
        "/api/v1/user/",
        headers={
            "Accept": APPLICATION_JSON,
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_user_info(client):
    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )
    app.container.auth.override(auth_service_mock)

    repository_mock = mock.AsyncMock(spec=UserRepository)
    repository_mock.get_by_id.return_value = ""

    with app.container.user_repository.override(repository_mock):
        response = client.get(
            "/api/v1/user/",
            headers={
                "Accept": APPLICATION_JSON,
                "Authorization": "Bearer xyz",
            },
        )
    assert response.status_code == HTTPStatus.OK


def test_create_user(client):
    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )
    app.container.auth.override(auth_service_mock)

    repository_mock = mock.AsyncMock(spec=UserRepository)
    repository_mock.add.return_value = ""

    with app.container.user_repository.override(repository_mock):
        resp = client.post(
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
