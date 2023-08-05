from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.core.auth0 import check_user
from app.llm.vocabulary import ChatGPTVocabularyGenerator
from app.schemas.users import Auth0User
from app.schemas.vocabulary import GetVocabularyQuestions

router = APIRouter()


@router.get("/")
async def get(*, auth: Auth0User = Depends(check_user)) -> dict[str, Any]:
    return {"message": "successfully"}


@router.post("/")
async def getVocabularyQuestions(
    *, user_input: GetVocabularyQuestions, _: Auth0User = Depends(check_user)
) -> dict[str, Any]:
    return {
        "data": ChatGPTVocabularyGenerator().generateVocabularyQuestion(
            category=user_input.category,
            primary_language=user_input.primary_language,
            learning_language=user_input.learning_language,
            num_questions=user_input.num_questions,
            num_answers=user_input.num_answers,
        )
    }
