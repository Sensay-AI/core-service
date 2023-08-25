import json
from json import JSONDecodeError
from typing import Any, Generator

from app.infrastructure.llm.vocabulary import (
    ChatGPTVocabularyGenerator,
)
from app.models.common.pagination import PagedResponseSchema
from app.models.db.vocabulary import VocabularyPrompt
from app.models.schemas.vocabulary import (
    GetVocabularyHistoryQuestion,
    GetVocabularyQuestions,
    VocabularyAnswerCreate,
    VocabularyPromptCreate,
    VocabularyQuestionCreate,
)
from app.repositories.vocabulary_repository import (
    CreateWithCategoryResponse,
    VocabularyRepository,
)
from app.services.base_service import BaseService


def parse_json_prompt(
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


class VocabularyService(BaseService):
    def __init__(
        self,
        voca_generator: ChatGPTVocabularyGenerator,
        voca_repository: VocabularyRepository,
    ):
        super().__init__(voca_repository)

        self.voca_generator = voca_generator
        self.voca_repository = voca_repository

    def get_new_vocabulary_lessons(
        self, user_id: str, user_input: GetVocabularyQuestions
    ) -> Generator:
        raw_questions = ""
        for text in self.voca_generator.generate_vocabulary_questions(
            category=user_input.category,
            translated_language=user_input.translated_language,
            learning_language=user_input.learning_language,
            num_questions=user_input.num_questions,
            num_answers=user_input.num_answers,
            level=user_input.level,
        ):
            raw_questions += text
            yield text
        yield "\n \n \n"
        try:
            self.logger.debug("Streaming process done")
            raw_questions = raw_questions.replace("\\n", " ")
            raw_questions = raw_questions.replace("\n", " ")

            questions: dict[str, Any] = json.loads(raw_questions)
            self.logger.debug("Try to parse plan text to object")
            learning_obj = parse_json_prompt(
                user_input.category,
                user_input.learning_language,
                user_input.translated_language,
                questions,
            )
            learning_obj.level = user_input.level
            category = self._add_lesson_to_database(learning_obj, user_id)
            # Yield category_id
            yield {
                "category_id": category.category_id,
                "learning_language": category.learning_language,
            }.__str__()
        except JSONDecodeError as e:
            self.logger.error(e.__str__())
            raise PromptParserException()

    def _add_lesson_to_database(
        self, learning_obj: VocabularyPromptCreate, user_id: str
    ) -> CreateWithCategoryResponse:
        self.logger.debug("Add lesson to database")
        return self.voca_repository.create_with_category(learning_obj, user_id)

    def get_history_lessons(
        self,
        user_input: GetVocabularyHistoryQuestion,
        user_id: str,
        page: int,
        size: int,
    ) -> PagedResponseSchema[VocabularyPrompt]:
        return self.voca_repository.get_history_questions(
            user_input, user_id, page, size
        )


class PromptParserException(Exception):
    def __init__(self) -> None:
        super().__init__("Can not parse prompt response to json")
