from typing import Any
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from langchain import OpenAI

from app.infrastructure.auth0.auth0 import Auth0Service
from app.main import app
from app.repositories.vocabulary_repository import VocabularyRepository
from app.services.vocabulary_service import parse_json_prompt
from app.schemas.users import Auth0User
from app.schemas.vocabulary import (
    VocabularyAnswerCreate,
    VocabularyPromptCreate,
    VocabularyQuestionCreate,
)

LEARNING_LANGUAGE = "english"
TRANSLATED_LANGUAGE = "vietnamese"
APPLICATION_JSON = "application/json"
CATEGORY = "mock_category"


@pytest.fixture()
def client():
    return TestClient(app)


def mock_chat_gpt_response() -> str:
    return """{ "lesson": "Let's learn about sports! Sports are physical activities that involve skill, competition, 
    and often teamwork. They are a great way to stay active and have fun. There are many different types of sports, 
    including team sports like soccer, basketball, and rugby, as well as individual sports like swimming, running, 
    and cycling. Sports can be played for leisure or professionally, and they bring people from diverse backgrounds 
    together to enjoy a shared passion."
        "questions": [
        {
        "Question": "What is the term used for a person who runs in a race?",
        "Options": ["Swimmer", "Runner", "Cyclist", "Skater"],
        "Answer": "Runner"
        },
        {
        "Question": "Which sport involves hitting a shuttlecock over a net?",
        "Options": ["Tennis", "Badminton", "Golf", "Volleyball"],
        "Answer": "Badminton"
        },
        {
        "Question": "In which sport can you score a touchdown?",
        "Options": ["Football", "Basketball", "Baseball", "Hockey"],
        "Answer": "Football"
        },
        {
        "Question": "Which sport is also known as 'The Gentleman's Game'?",
        "Options": ["Cricket", "Rugby", "Golf", "Squash"],
        "Answer": "Cricket"
        },
        {
        "Question": "What is the term used for the area where you play basketball?",
        "Options": ["Court", "Field", "Rink", "Course"],
        "Answer": "Court"
        }
        ]
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
#     auth_service_mock = mock.Mock(spec=Auth0Service)
#     auth_service_mock.verify_token.return_value = Auth0User(
#         sub="user123", permissions=["read", "write"]
#     )
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
    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )
    voca_repo_mock = mock.Mock(spec=VocabularyRepository)

    open_ai_mock = mock.Mock(spec=OpenAI)
    open_ai_mock.predict.return_value = mock_chat_gpt_response()

    app.container.auth.override(auth_service_mock)
    app.container.open_ai.override(open_ai_mock)
    app.container.vocabulary_repository.override(voca_repo_mock)
    response = client.post(
        "/api/v1/lesson/vocabulary/questions",
        headers={
            "Accept": APPLICATION_JSON,
            "Authorization": "Bearer xyz",
        },
        json={
            "category": "football",
            "translated_language": "english",
            "learning_language": "vietnamese",
            "num_questions": 1,
            "num_answers": 1,
        },
    )
    assert response.status_code == 200


def test_parse_json_prompt():
    input_obj = parse_json_prompt(
        CATEGORY, LEARNING_LANGUAGE, TRANSLATED_LANGUAGE, mock_lesson_dict()
    )
    output_obj = mock_lesson_object()

    assert input_obj == output_obj
