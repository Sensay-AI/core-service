import os
from unittest import mock
from typing import Iterator
from io import BytesIO

import pytest
from langchain import OpenAI
from fastapi.testclient import TestClient
from PIL import Image

from app.infrastructure.auth0.auth0 import Auth0Service
from app.infrastructure.aws.s3 import S3Service
from app.main import app
from app.schemas.users import Auth0User

APPLICATION_JSON = "application/json"


@pytest.fixture()
def client():
    return TestClient(app)


def mock_chat_gpt_response() -> Iterator[str]:
    return iter(
        """there is a cat that is standing in the grass and looking at the camera
        """
    )


def test_generate_caption(client):
    s3_service_mock = mock.Mock(spec=S3Service)
    s3_service_mock.upload_file.return_value = "http://s3.image.jng"

    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )
    open_ai_mock = mock.Mock(spec=OpenAI)
    open_ai_mock.stream.return_value = mock_chat_gpt_response()
    app.container.s3_service.override(s3_service_mock)
    app.container.auth.override(auth_service_mock)

    image_path = os.path.join(os.path.dirname(__file__), "../image_caption/test_image.jpg")
    test_image = Image.open(image_path)
    test_image_bytes = BytesIO()
    test_image.save(test_image_bytes, format='jpg')

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        image_file = ("test_image.png", image_bytes, "image/png")
        response = client.post(
            "/api/v1/image/generate_caption",
            files={"image_file": image_file},
            headers={
                "Accept": APPLICATION_JSON,
                "Authorization": "Bearer xyz",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"upload_path": "http://s3.image.jng"}
    s3_service_mock.upload_file.assert_called_once_with(
        file=mock.ANY,
        bucket_name=mock.ANY,
        user_id="user123",  # Set the user_id based on the mock
        extension=".png",
    )
