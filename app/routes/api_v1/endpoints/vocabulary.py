from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth0 import check_user
from app.crud.crud_vocabulary import CRUDVocabularyPrompt
from app.db.database import get_db
from app.llm.vocabulary import ChatGPTVocabularyGenerator
from app.models.vocabulary import Category, VocabularyPrompt
from app.schemas.users import Auth0User
from app.schemas.vocabulary import (
    GetVocabularyQuestions,
    VocabularyAnswerCreate,
    VocabularyPromptCreate,
    VocabularyQuestionCreate,
)

router = APIRouter()


def _parse_json_prompt(
    category: str, language: str, data: dict
) -> VocabularyPromptCreate:
    questions = []
    data = data[language]
    for question in data["questions"]:
        answers = []
        for answer in question["options"]:
            is_correct = answer == question["answer"]
            answers.append(
                VocabularyAnswerCreate(answer_text=answer, is_correct=is_correct)
            )

        questions.append(
            VocabularyQuestionCreate(
                question_text=question["question"], answers=answers
            )
        )

    return VocabularyPromptCreate(
        prompt=data["lesson"],
        category=category,
        questions=questions,
        language=language,
    )


def generate_data() -> VocabularyPromptCreate:
    answers = [
        VocabularyAnswerCreate(answer_text="1", is_correct=False),
        VocabularyAnswerCreate(answer_text="2", is_correct=False),
        VocabularyAnswerCreate(answer_text="3", is_correct=False),
        VocabularyAnswerCreate(answer_text="4", is_correct=True),
    ]
    question = VocabularyQuestionCreate(question_text="ABCDEFGH?", answers=answers)
    return VocabularyPromptCreate(
        prompt="this is sample prompt 2",
        category="movie",
        questions=[question],
        language="english",
    )


@router.get("/")
async def get(*, db: Session = Depends(get_db)) -> dict[str, Any]:
    abc = CRUDVocabularyPrompt(VocabularyPrompt)
    abc.create_with_category(db, generate_data(), "facebook|4152771494955357")
    return {"message": "successfully"}


@router.post("/questions")
async def get_new_vocabulary_questions(
    *,
    user_input: GetVocabularyQuestions,
    db: Session = Depends(get_db),
    auth: Auth0User = Depends(check_user),
) -> dict[str, Any]:
    questions: dict[str, Any] = ChatGPTVocabularyGenerator().generateVocabularyQuestion(
        category=user_input.category,
        primary_language=user_input.primary_language,
        learning_language=user_input.learning_language,
        num_questions=user_input.num_questions,
        num_answers=user_input.num_answers,
    )

    # primary_language_object = _parse_json_prompt(user_input.category, user_input.primary_language, questions)
    learning_language_object = _parse_json_prompt(
        user_input.category, user_input.learning_language, questions
    )
    CRUDVocabularyPrompt(VocabularyPromptCreate).create_with_category(
        db, learning_language_object, auth.id
    )
    return {"items": questions}


@router.get("/categories")
async def get_user_categories(
    *, db: Session = Depends(get_db), auth: Auth0User = Depends(check_user)
) -> dict[str, Any]:
    categories = db.query(Category).filter(Category.user_id == auth.id).limit(100).all()
    categories = [category.__dict__ for category in categories]
    return {"items": categories}
