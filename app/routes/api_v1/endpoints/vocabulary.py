from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container.containers import Container
from app.infrastructure.llm.vocabulary import ChatGPTVocabularyGenerator
from app.models.vocabulary import Category
from app.repositories.base_repository import BaseRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.routes.api_v1.endpoints.auth import check_user
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


@router.post("/questions")
@inject
async def get_new_vocabulary_questions(
    *,
    user_input: GetVocabularyQuestions,
    voca_generator: ChatGPTVocabularyGenerator = Depends(
        Provide[Container.chatGPT_vocabulary_generator]
    ),
    repo: VocabularyRepository = Depends(Provide[Container.vocabulary_repository]),
    auth: Auth0User = Depends(check_user),
) -> dict[str, Any]:
    questions: dict[str, Any] = voca_generator.generate_vocabulary_questions(
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
    repo.create_with_category(learning_language_object, auth.id)
    return {"items": questions}


@router.get("/category")
@inject
async def get_user_categories(
    *,
    repo: BaseRepository = Depends(Provide[Container.category_repository]),
    auth: Auth0User = Depends(check_user),
) -> dict[str, Any]:
    categories = repo.query(Category.user_id == auth.id)
    items = []
    if categories:
        items = [category.__dict__ for category in categories]
    return {"items": items}


@router.post("/category/history/questions")
@inject
async def get_history_question_by_category(
    input: GetVocabularyHistoryQuestion,
    repo: VocabularyRepository = Depends(Provide[Container.vocabulary_repository]),
    auth: Auth0User = Depends(check_user),
) -> dict[str, Any]:
    prompts = repo.get_history_questions(input, auth.id)
    return {"items": prompts}
