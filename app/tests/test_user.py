from http import HTTPStatus

from fastapi.testclient import TestClient

from app.core.auth0 import Auth0Helper
from app.main import app
from app.schemas.users import Auth0User
from app.tests.config_test import MockToken

client = TestClient(app)
token = MockToken.get_token()


def test_get_user_info_without_token():
    response = client.get(
        "/api/v1/user",
        headers={
            "Accept": "application/json",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_user_info():
    response = client.get(
        "/api/v1/user",
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer " + token,
        },
    )
    assert response.status_code == HTTPStatus.OK


def test_user_scope_found():
    auth0User: Auth0User = Auth0Helper.verify_token(token)
    assert len(auth0User.permissions) != 0
    assert "create:client_grants" in auth0User.permissions


def test_create_user():
    resp = client.post(
        "/api/v1/user/create",
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer " + token,
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
    assert resp.status_code in (HTTPStatus.OK, HTTPStatus.BAD_REQUEST)
