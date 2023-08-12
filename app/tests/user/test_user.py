from http import HTTPStatus
from unittest import mock

import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.infrastructure.auth0.auth0 import Auth0Service
from app.main import app
from app.repositories.user_repository import UserRepository
from app.schemas.users import Auth0User

APPLICATION_JSON = "application/json"


class StsClientStub:
    pass


class TempCredentialsStub:
    pass


class SessionStub:
    pass


class S3ClientStub:
    pass


class S3ServiceStub:
    pass


class S3ImageBucket:
    pass


@pytest.fixture()
def client():
    app.container.sts_client.override(providers.Resource(StsClientStub))
    app.container.temp_credentials.override(providers.Resource(TempCredentialsStub))
    app.container.session.override(providers.Resource(SessionStub))
    app.container.s3_client.override(providers.Resource(S3ClientStub))
    app.container.s3_service.override(providers.Factory(S3ServiceStub))
    app.container.s3_image_bucket.override(providers.Resource(S3ImageBucket))
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
