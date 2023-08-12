from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth0 import check_user
from app.crud.crud_vocabulary import CRUDVocabularyPrompt
from app.db.database import get_db
from app.llm.vocabulary import ChatGPTVocabularyGenerator
from app.models.vocabulary import (
    Category,
)
from app.schemas.users import Auth0User
from app.schemas.vocabulary import (
    GetVocabularyHistoryQuestion,
    GetVocabularyQuestions,
    VocabularyAnswerCreate,
    VocabularyPromptCreate,
    VocabularyQuestionCreate,
)

router = APIRouter()


def _parse_json_prompt(
    category: str, learning_language: str, translated_language: str, data: dict
) -> VocabularyPromptCreate:
    questions = []
    data_learning = data[learning_language]
    data_translated = data[translated_language]
    for question_learning, question_translated in zip(
        data_learning["questions"], data_translated["questions"]
    ):
        answers = []
        for answer_learning, answer_translated in zip(
            question_learning["options"], question_translated["options"]
        ):
            is_correct = answer_learning == question_learning["answer"]
            answers.append(
                VocabularyAnswerCreate(
                    answer_text=answer_learning,
                    is_correct=is_correct,
                    translation=answer_translated,
                )
            )

        questions.append(
            VocabularyQuestionCreate(
                question_text=question_learning["question"],
                answers=answers,
                translation=question_translated["question"],
            )
        )

    return VocabularyPromptCreate(
        prompt=data_learning["lesson"],
        category=category,
        questions=questions,
        learning_language=learning_language,
        translated_language=translated_language,
        translation=data_translated["lesson"],
    )


@router.get("/")
async def get(*, db: Session = Depends(get_db)) -> dict[str, Any]:
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
        translated_language=user_input.translated_language,
        learning_language=user_input.learning_language,
        num_questions=user_input.num_questions,
        num_answers=user_input.num_answers,
    )

    learning_language_object = _parse_json_prompt(
        user_input.category,
        user_input.learning_language,
        user_input.translated_language,
        questions,
    )
    CRUDVocabularyPrompt(VocabularyPromptCreate).create_with_category(
        db, learning_language_object, auth.id
    )
    return {"items": questions}


@router.get("/category")
async def get_user_categories(
    *, db: Session = Depends(get_db), auth: Auth0User = Depends(check_user)
) -> dict[str, Any]:
    categories = db.query(Category).filter(Category.user_id == auth.id).limit(100).all()
    categories = [category.__dict__ for category in categories]
    return {"items": categories}


@router.post("/category/history/questions")
async def get_history_question_by_category(
    *,
    db: Session = Depends(get_db),
    input: GetVocabularyHistoryQuestion,
    auth: Auth0User = Depends(check_user),
) -> dict[str, Any]:
    prompts = CRUDVocabularyPrompt(VocabularyPromptCreate).get_history_questions(
        db, input, auth.id
    )
    return {"items": prompts}
