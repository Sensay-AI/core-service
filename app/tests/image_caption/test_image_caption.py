import os
from json.decoder import JSONDecodeError
from typing import Iterator
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from langchain import OpenAI
from replicate import Client

from app.infrastructure.auth0.auth0 import Auth0Service
from app.infrastructure.aws.s3 import S3Service
from app.main import app
from app.models.schemas.users import Auth0User
from app.repositories.caption_repository import (
    CaptionRepository,
    TranslatedCaptionRepository,
)

APPLICATION_JSON = "application/json"


@pytest.fixture()
def client():
    return TestClient(app)


def mock_chat_gpt_response() -> Iterator[str]:
    return iter(
        """{
        "vietnamese": "con mèo đứng trên bãi cỏ nhìn về hướng máy ảnh",
        "english": "A cat standing on the grass  looking at the camera"
        }
        """
    )


def mock_fail_response() -> Iterator[str]:
    return iter(
        """{
                "vietnamese": "con mèo đứng trên bãi cỏ nhìn về hướng máy ảnh"",
                "english": "A cat standing on the grass  looking at the camera"
                }
                """
    )


def mock_replicate_caption_response() -> Iterator[str]:
    return iter(
        """there is a cat that is standing in the grass and looking at the camera
        """
    )


def test_generate_caption(client):
    image_path = os.path.join(
        os.path.dirname(__file__), "../image_caption/test_image.jpg"
    )
    test_image = open(image_path, "rb")

    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )

    primary_caption_repository_mock = mock.AsyncMock(spec=CaptionRepository)
    learning_caption_repository_mock = mock.AsyncMock(spec=TranslatedCaptionRepository)
    open_ai_mock = mock.Mock(spec=OpenAI)
    open_ai_mock.stream.return_value = mock_chat_gpt_response()

    replicate_caption_mock = mock.Mock(spec=Client)
    replicate_caption_mock.run.return_value = mock_replicate_caption_response()
    s3_service_mock = mock.Mock(spec=S3Service)
    s3_service_mock.upload_file.return_value = "http://s3.image.jng"
    s3_service_mock.get_file.return_value = test_image.read()
    app.container.primary_caption_repository.override(primary_caption_repository_mock)
    app.container.learning_caption_repository.override(learning_caption_repository_mock)
    app.container.s3_service.override(s3_service_mock)
    app.container.auth.override(auth_service_mock)
    app.container.open_ai.override(open_ai_mock)
    app.container.caption_client.override(replicate_caption_mock)

    payload = {
        "image_bucket_path_key": "http://s3.image.jng/user/abc.jpg",
        "learning_language": "english",
        "primary_language": "vietnamese",
    }

    response = client.post(
        "/api/v1/image/s3_bucket/sensayai-images/caption",
        json=payload,
        headers={
            "Accept": APPLICATION_JSON,
            "Authorization": "Bearer xyz",
        },
    )
    assert response.status_code == 200


def test_generate_caption_fail(client):
    image_path = os.path.join(
        os.path.dirname(__file__), "../image_caption/test_image.jpg"
    )
    test_image = open(image_path, "rb")

    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )

    primary_caption_repository_mock = mock.AsyncMock(spec=CaptionRepository)
    learning_caption_repository_mock = mock.AsyncMock(spec=TranslatedCaptionRepository)
    open_ai_mock = mock.Mock(spec=OpenAI)
    open_ai_mock.stream.return_value = mock_fail_response()

    replicate_caption_mock = mock.Mock(spec=Client)
    replicate_caption_mock.run.return_value = mock_replicate_caption_response()
    s3_service_mock = mock.Mock(spec=S3Service)
    s3_service_mock.upload_file.return_value = "http://s3.image.jng"
    s3_service_mock.get_file.return_value = test_image.read()
    app.container.primary_caption_repository.override(primary_caption_repository_mock)
    app.container.learning_caption_repository.override(learning_caption_repository_mock)
    app.container.s3_service.override(s3_service_mock)
    app.container.auth.override(auth_service_mock)
    app.container.open_ai.override(open_ai_mock)
    app.container.caption_client.override(replicate_caption_mock)

    payload = {
        "image_bucket_path_key": "http://s3.image.jng/user/abc.jpg",
        "learning_language": "english",
        "primary_language": "vietnamese",
    }
    with pytest.raises(JSONDecodeError) as e:
        client.post(
            "/api/v1/image/s3_bucket/sensayai-images/caption",
            json=payload,
            headers={
                "Accept": APPLICATION_JSON,
                "Authorization": "Bearer xyz",
            },
        )
    assert e.type == JSONDecodeError
