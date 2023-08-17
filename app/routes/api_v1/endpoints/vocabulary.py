from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from app.container.containers import Container
from app.infrastructure.llm.vocabulary import PromptParserException
from app.models.vocabulary import Category
from app.repositories.base_repository import BaseRepository
from app.routes.api_v1.endpoints.auth import check_user
from app.schemas.users import Auth0User
from app.schemas.vocabulary import (
    GetVocabularyHistoryQuestion,
    GetVocabularyQuestions,
)
from app.services.vocabulary_service import VocabularyService

router = APIRouter()


@router.post("/questions")
@inject
async def get_new_vocabulary_questions(
    *,
    user_input: GetVocabularyQuestions,
    vocabulary_service: VocabularyService = Depends(
        Provide[Container.vocabulary_service]
    ),
    auth: Auth0User = Depends(check_user),
) -> object:
    try:
        questions: dict[str, Any] = vocabulary_service.get_new_vocabulary_lessons(
            user_id=auth.id, user_input=user_input
        )
        return {"items": questions}
    except PromptParserException as e:
        return HTTPException(status_code=10002, detail=e.__str__())


@router.get("/category")
@inject
async def get_user_categories(
    *,
    repo: BaseRepository = Depends(Provide[Container.category_repository]),
    auth: Auth0User = Depends(check_user),
) -> object:
    categories = repo.query(Category.user_id == auth.id)
    items = []
    if categories:
        items = [category.__dict__ for category in categories]
    return {"items": items}


@router.post("/category/history/questions")
@inject
async def get_history_question_by_category(
    user_input: GetVocabularyHistoryQuestion,
    vocabulary_service: VocabularyService = Depends(
        Provide[Container.vocabulary_service]
    ),
    auth: Auth0User = Depends(check_user),
) -> object:
    prompts = vocabulary_service.get_history_lessons(
        user_id=auth.id, user_input=user_input
    )
    return {"items": prompts}
