from typing import Any
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from langchain import OpenAI

from app.main import app
from app.models.vocabulary import Category
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.vocabulary import (
    VocabularyAnswerCreate,
    VocabularyPromptCreate,
    VocabularyQuestionCreate,
)
from app.services.base_service import BaseService
from app.services.vocabulary_service import VocabularyService, parse_json_prompt
from app.tests.utils import get_http_header, mock_user

LEARNING_LANGUAGE = "english"
TRANSLATED_LANGUAGE = "vietnamese"
APPLICATION_JSON = "application/json"
CATEGORY = "mock_category"


@pytest.fixture()
def client():
    return TestClient(app)


def mock_category() -> list[Category]:
    return [
        Category(id=1, category_name="football"),
        Category(id=2, category_name="movie"),
    ]


def mock_wrong_chat_gpt_response() -> str:
    return """{ 
        "english": { 
            "lesson": "E
                       ABCD"
                "questions": [
                    {
                    "Question": "What is the term used for a person who runs in a race?",
                    "Options": ["Swimmer", "Runner", "Cyclist", "Skater"],
                    "Answer": "Runner"
                    },
                ]
                }
        "vietnamese": {
                    "lesson": "ABCD
                               ABCD",
                "questions": [
                    {
                    "Question": "What is the term used for a person who runs in a race?",
                    "Options": ["Swimmer", "Runner", "Cyclist", "Skater"],
                    "Answer": "Runner"
                    },
                ]
        }
    }
    """


def mock_chat_gpt_response() -> str:
    return """{ 
        "english": { 
            "lesson": "ABCD
                       ABCD",
                "questions": [
                    {
                    "question": "What is the term used for a person who runs in a race?",
                    "options": ["Swimmer", "Runner", "Cyclist", "Skater"],
                    "answer": "Runner"
                    }
                ]
                },
        "vietnamese": {
                    "lesson": "ABCD
                               ABCD",
                "questions": [
                    {
                    "question": "What is the term used for a person who runs in a race?",
                    "options": ["Swimmer", "Runner", "Cyclist", "Skater"],
                    "answer": "Runner"
                    }
                ]
        }
    }
    """


def mock_questions_dict() -> list[dict[str, Any]]:
    return [
        {"question": "question1", "options": ["A", "B", "C", "D"], "answer": "A"},
        {"question": "question2", "options": ["A", "B", "C", "D"], "answer": "A"},
    ]


def mock_prompt_dict() -> dict[str, Any]:
    return {"lesson": "prompt", "questions": mock_questions_dict()}


def mock_lesson_dict() -> dict[str, Any]:
    return {
        LEARNING_LANGUAGE: mock_prompt_dict(),
        TRANSLATED_LANGUAGE: mock_prompt_dict(),
    }


def mock_lesson_object() -> VocabularyPromptCreate:
    answers = [
        VocabularyAnswerCreate(answer_text="A", is_correct=True, translation="A"),
        VocabularyAnswerCreate(answer_text="B", is_correct=False, translation="B"),
        VocabularyAnswerCreate(answer_text="C", is_correct=False, translation="C"),
        VocabularyAnswerCreate(answer_text="D", is_correct=False, translation="D"),
    ]
    questions = [
        VocabularyQuestionCreate(
            question_text="question1", answers=answers, translation="question1"
        ),
        VocabularyQuestionCreate(
            question_text="question2", answers=answers, translation="question2"
        ),
    ]
    return VocabularyPromptCreate(
        prompt="prompt",
        category=CATEGORY,
        questions=questions,
        learning_language=LEARNING_LANGUAGE,
        translated_language=TRANSLATED_LANGUAGE,
        translation="prompt",
    )


# def test_api_new_vocabulary_questions(client):
#     auth_service_mock = prepare_user()
#     app.container.auth.override(auth_service_mock)
#     voca_repo_mock = mock.Mock(spec=VocabularyRepository)
#     app.container.vocabulary_repository.override(voca_repo_mock)
#
#     response = client.post(
#         "/api/v1/lesson/vocabulary/questions",
#         headers={
#             "Accept": APPLICATION_JSON,
#             "Authorization": "Bearer xyz",
#         },
#         json={
#             "category": "football",
#             "translated_language": "english",
#             "learning_language": "vietnamese",
#             "num_questions": 1,
#             "num_answers": 1
#         }
#     )
#     assert response.status_code == 200


def test_func_generate_vocabulary_questions(client):
    auth_service_mock = mock_user()
    voca_repo_mock = mock.Mock(spec=VocabularyRepository)

    open_ai_mock = mock.Mock(spec=OpenAI)
    open_ai_mock.predict.return_value = mock_chat_gpt_response()

    app.container.auth.override(auth_service_mock)
    app.container.vocabulary_repository.override(voca_repo_mock)
    payload = {
        "category": "football",
        "translated_language": "english",
        "learning_language": "vietnamese",
        "level": 1,
        "num_questions": 1,
        "num_answers": 1,
    }
    with app.container.open_ai.override(open_ai_mock):
        response = client.post(
            "/api/v1/lesson/vocabulary/questions",
            headers=get_http_header(),
            json=payload,
        )
    assert response.status_code == 200
    assert "status_code" not in response.json().keys()


# def test_prompt_parse_failed(client):
#     auth_service_mock = mock_user()
#     voca_repo_mock = mock.Mock(spec=VocabularyRepository)
#
#     open_ai_mock = mock.Mock(spec=OpenAI)
#     open_ai_mock.predict.return_value = mock_wrong_chat_gpt_response()
#
#     app.container.auth.override(auth_service_mock)
#     app.container.vocabulary_repository.override(voca_repo_mock)
#     payload = {
#         "category": "football",
#         "translated_language": "english",
#         "learning_language": "vietnamese",
#         "num_questions": 1,
#         "num_answers": 1,
#     }
#     with app.container.open_ai.override(open_ai_mock):
#         response = client.post(
#             "/api/v1/lesson/vocabulary/questions",
#             headers=get_http_header(),
#             json=payload,
#         )
#     assert response.status_code == 200
#     assert "status_code" in response.json().keys()


def test_parse_json_prompt():
    input_obj = parse_json_prompt(
        CATEGORY, LEARNING_LANGUAGE, TRANSLATED_LANGUAGE, mock_lesson_dict()
    )
    output_obj = mock_lesson_object()

    assert input_obj == output_obj


def test_get_category(client):
    auth_service_mock = mock_user()

    category_service_mock = mock.Mock(spec=BaseService)
    category_service_mock.query.return_value = mock_category()

    app.container.auth.override(auth_service_mock)
    app.container.category_service.override(category_service_mock)

    response = client.get(
        "/api/v1/lesson/vocabulary/category", headers=get_http_header()
    )
    assert response.status_code == 200


def test_get_history_question(client):
    auth_service_mock = mock_user()

    vocabulary_service_mock = mock.Mock(spec=VocabularyService)
    vocabulary_service_mock.get_history_lessons.return_value = []

    app.container.auth.override(auth_service_mock)
    app.container.vocabulary_service.override(vocabulary_service_mock)

    response = client.post(
        "/api/v1/lesson/vocabulary/category/history/questions",
        headers=get_http_header(),
        json={"category_id": 1, "limit_prompts": 10, "learning_language": "english"},
    )
    assert response.status_code == 200
