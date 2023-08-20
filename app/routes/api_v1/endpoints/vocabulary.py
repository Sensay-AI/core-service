import asyncio
import time

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

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

mock_stream_data = [
    "                   ",
    "           {               ",
    ' "English": { ',
    '                "lesson": "Tinh Yeu La Gi is a Vietnamese phrase that translates to ',
    'What is love?. Love is a powerful emotion that can be experienced in many different ways. It can be ',
    'a feeling of strong attachment and affection towards someone, a feeling of admiration and respect, ',
    'or a feeling of joy and happiness. Love can also be a feeling of loyalty and commitment towards ',
    'someone or something. Love is something that is shared between two people and can bring them closer ',
    'together. It can also be something that is shared between many people, like a family or a group of ',
    'friends. Love is an emotion that can change over time, but it can also be a lasting emotion that ',
    'unites people and brings them together. Here are five vocabulary words related to love:',
    ' Affection - an emotion of fondness or tenderness towards someone.',
    '  Commitment - a promise or dedication to do something.',
    '  Admiration - a feeling of respect or approval towards someone.',
    '  Compassion - a feeling of sympathy and understanding towards someone.',
    '   Loyalty - a strong feeling of support and allegiance towards someone.", ',
    '  "questions": [',
    '                         {',
    '"question": "What is the term used for a feeling of strong attachment and affection towards '
    'someone?", ',
    '                            "options": ["Admiration", "Compassion", "Affection"],',
    '                            "answer": "Affection"',
    '                         },',
    "                   ",
    "           {               ",
]


async def generator():
    for response in mock_stream_data:
        yield response
        print(response)
        await asyncio.sleep(4)


def fake_data_streamer():
    print(len(mock_stream_data))
    for i in range(97):
        print(mock_stream_data[i])
        yield mock_stream_data[i] + '\n'
        time.sleep(2.5)

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
        return StreamingResponse(
            vocabulary_service.get_new_vocabulary_lessons(user_id=auth.id, user_input=user_input),
            media_type="text/plain"
        )

        # return StreamingResponse(fake_data_streamer(), media_type='application/x-ndjson')
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
