import os
from unittest import mock

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.infrastructure.aws.s3 import S3Service
from app.main import app
from app.routes.api_v1.endpoints.auth import check_user
from app.schemas.users import Auth0User

pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[check_user] = override_dependency
    async with AsyncClient(app=app, base_url="http://test") as testClient:
        yield testClient


async def override_dependency():
    return Auth0User(sub="user123", permissions=["read", "write"])


@pytest.mark.asyncio()
async def test_upload_image(client):
    s3_service_mock = mock.AsyncMock(spec=S3Service)
    s3_service_mock.upload_file.return_value = "http://s3.image.jng"
    image_path = os.path.join(os.path.dirname(__file__), "test_image.jpg")
    with open(image_path, "rb") as image_file:
        with app.container.s3_service.override(s3_service_mock):
            image_bytes = image_file.read()
            image_file = ("test_image.png", image_bytes, "image/png")

            response = await client.post(
                "/api/v1/image/upload",
                files={"image_file": image_file},
            )

    assert response.status_code == 200
    assert response.json() == {"upload_path": "http://s3.image.jng"}
    s3_service_mock.upload_file.assert_called_once_with(
        file=mock.ANY,
        bucket_name=mock.ANY,
        user_id="user123",  # Set the user_id based on the mock
        extension=".png",
    )
