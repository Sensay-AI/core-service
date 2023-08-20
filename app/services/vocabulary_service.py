from typing import Type

from app.infrastructure.llm.vocabulary import (
    ChatGPTVocabularyGenerator,
)
from app.models.vocabulary import VocabularyPrompt
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.vocabulary import (
    GetVocabularyHistoryQuestion,
    GetVocabularyQuestions,
)


class VocabularyService:
    def __init__(
            self,
            voca_generator: ChatGPTVocabularyGenerator,
            voca_repository: VocabularyRepository,
    ):
        self.voca_generator = voca_generator
        self.voca_repository = voca_repository

    def get_new_vocabulary_lessons(
            self, user_id: str, user_input: GetVocabularyQuestions
    ):
        return self.voca_generator.generate_vocabulary_questions(category=user_input.category,
                                                                 translated_language=user_input.translated_language,
                                                                 learning_language=user_input.learning_language,
                                                                 num_questions=user_input.num_questions,
                                                                 num_answers=user_input.num_answers,
                                                                 user_id=user_id,
                                                                 )

    def get_history_lessons(
            self, user_input: GetVocabularyHistoryQuestion, user_id: str
    ) -> list[Type[VocabularyPrompt]]:
        return self.voca_repository.get_history_questions(user_input, user_id)
