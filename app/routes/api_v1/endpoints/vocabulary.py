from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.container.containers import Container
from app.models.common.pagination import PageParams
from app.models.db.vocabulary import Category
from app.models.schemas.users import Auth0User
from app.models.schemas.vocabulary import (
    GetVocabularyHistoryQuestion,
    GetVocabularyQuestions,
)
from app.routes.api_v1.endpoints.auth import check_user
from app.services.base_service import BaseService
from app.services.vocabulary_service import PromptParserException, VocabularyService

router = APIRouter()


@router.post("/question")
@inject
async def create_vocabulary_question(
    *,
    user_input: GetVocabularyQuestions,
    vocabulary_service: VocabularyService = Depends(
        Provide[Container.vocabulary_service]
    ),
    auth: Auth0User = Depends(check_user),
) -> object:
    try:
        return StreamingResponse(
            vocabulary_service.get_new_vocabulary_lessons(
                user_id=auth.id, user_input=user_input
            ),
            media_type="text/plain",
        )
    except PromptParserException as e:
        return HTTPException(status_code=10002, detail=e.__str__())


@router.get("/categories")
@inject
async def list_categories(
    *,
    page_params: PageParams = Depends(),
    category_service: BaseService = Depends(Provide[Container.category_service]),
    auth: Auth0User = Depends(check_user),
) -> object:
    return category_service.query(
        query=Category.user_id == auth.id,
        page=page_params.page,
        size=page_params.size,
        sort_by=Category.created_at.desc(),
    )


@router.get("/category/{category_id}/learning_language/{learning_language}/questions")
@inject
async def list_questions(
    category_id: int,
    learning_language: str,
    page_params: PageParams = Depends(),
    vocabulary_service: VocabularyService = Depends(
        Provide[Container.vocabulary_service]
    ),
    auth: Auth0User = Depends(check_user),
) -> object:
    user_input = GetVocabularyHistoryQuestion(
        category_id=category_id, learning_language=learning_language
    )
    return vocabulary_service.get_history_lessons(
        user_id=auth.id,
        user_input=user_input,
        page=page_params.page,
        size=page_params.size,
    )
