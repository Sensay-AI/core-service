import os
from typing import Iterator
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from langchain import OpenAI
from replicate import Client

from app.infrastructure.auth0.auth0 import Auth0Service
from app.infrastructure.aws.s3 import S3Service
from app.main import app
from app.models.db.image_caption import ImageCaption
from app.models.schemas.users import Auth0User
from app.repositories.caption_repository import CaptionRepository

APPLICATION_JSON = "application/json"


@pytest.fixture()
def client():
    return TestClient(app)


def mock_chat_gpt_response() -> Iterator[str]:
    return iter(
        """In the picturesque setting of the verdant expanse, a graceful feline creature can be observed maintaining an
         upright stance upon the swaying blades of emerald grass. Its gaze, a mesmerizing amalgamation of curiosity 
         and contemplation, is gracefully directed towards the lens of the camera capturing this enchanting tableau.
        """
    )


def mock_replicate_caption_response() -> Iterator[str]:
    return iter(
        """there is a cat that is standing in the grass and looking at the camera
        """
    )


def test_generate_caption(client):
    image_path = os.path.join(os.path.dirname(__file__), "../zzz/test_image.jpg")
    test_image = open(image_path, "rb")

    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )

    image_caption_add = ImageCaption(
        user_id="123",
        image_url="http://s3.image.jng/user/abc.jpg",
        caption="""In the picturesque setting of the verdant expanse, a graceful feline creature can be observed maintaining an
         upright stance upon the swaying blades of emerald grass. Its gaze, a mesmerizing amalgamation of curiosity 
         and contemplation, is gracefully directed towards the lens of the camera capturing this enchanting tableau.""",
        language="english",
    )
    repository_mock = mock.AsyncMock(spec=CaptionRepository)
    repository_mock.add_image_caption.return_value = image_caption_add

    open_ai_mock = mock.Mock(spec=OpenAI)
    open_ai_mock.stream.return_value = mock_chat_gpt_response()

    replicate_caption_mock = mock.Mock(spec=Client)
    replicate_caption_mock.run.return_value = mock_replicate_caption_response()
    s3_service_mock = mock.Mock(spec=S3Service)
    s3_service_mock.upload_file.return_value = "http://s3.image.jng"
    s3_service_mock.get_file.return_value = test_image.read()
    app.container.s3_service.override(s3_service_mock)
    app.container.auth.override(auth_service_mock)
    app.container.open_ai.override(open_ai_mock)
    app.container.caption_client.override(replicate_caption_mock)

    payload = {"image_url": "http://s3.image.jng/user/abc.jpg", "language": "english"}
    with app.container.image_caption_repository.override(repository_mock):
        response = client.post(
            "/api/v1/image/generate_caption",
            json=payload,
            headers={
                "Accept": APPLICATION_JSON,
                "Authorization": "Bearer xyz",
            },
        )

    assert response.status_code == 200
