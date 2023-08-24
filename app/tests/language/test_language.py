from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.base_service import BaseService
from app.tests.utils import get_http_header, mock_user


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_supported_languages(client):
    auth_service_mock = mock_user()

    language_service_mock = mock.Mock(spec=BaseService)
    language_service_mock.get_multi.return_value = []
    app.container.auth.override(auth_service_mock)
    app.container.language_service.override(language_service_mock)
    response = client.get(
        "/api/v1/language",
        headers=get_http_header(),
    )
    assert response.status_code == 200
