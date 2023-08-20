from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from app.container.containers import Container
from app.infrastructure.llm.vocabulary import PromptParserException
from app.models.common.pagination import PageParams
from app.models.db.vocabulary import Category
from app.models.schemas.users import Auth0User
from app.models.schemas.vocabulary import (
    GetVocabularyHistoryQuestion,
    GetVocabularyQuestions,
)
from app.repositories.vocabulary_repository import LanguageNotSupportException
from app.routes.api_v1.endpoints.auth import check_user
from app.services.base_service import BaseService
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
    except LanguageNotSupportException as e:
        return HTTPException(status_code=10003, detail=e.__str__())


@router.get("/category")
@inject
async def get_user_categories(
    *,
    page_params: PageParams = Depends(),
    category_service: BaseService = Depends(Provide[Container.category_service]),
    auth: Auth0User = Depends(check_user),
) -> object:
    return category_service.query(
        query=Category.user_id == auth.id, page=page_params.page, size=page_params.size
    )


@router.post("/category/history/questions")
@inject
async def get_history_question_by_category(
    user_input: GetVocabularyHistoryQuestion,
    page_params: PageParams = Depends(),
    vocabulary_service: VocabularyService = Depends(
        Provide[Container.vocabulary_service]
    ),
    auth: Auth0User = Depends(check_user),
) -> object:
    return vocabulary_service.get_history_lessons(
        user_id=auth.id,
        user_input=user_input,
        page=page_params.page,
        size=page_params.size,
    )
