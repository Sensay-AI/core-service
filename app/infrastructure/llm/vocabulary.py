import json
import logging

from langchain import OpenAI, PromptTemplate

from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.vocabulary import VocabularyAnswerCreate, VocabularyQuestionCreate, VocabularyPromptCreate


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


class ChatGPTVocabularyGenerator:
    _vocabulary_format = """{
                "lesson": "<prompt of lesson without a newline>",
                "questions": [
                {
                    "question": "What is the term used for a person who runs in a race?",
                    "options": ["Swimmer", "Runner", "Cyclist"],
                    "answer": "Runner"
                }
                ]
            }"""

    _vocabulary_template = """
            Create a prompt lesson more than 100 words about {{ category }} and suggest {{ num_questions }} vocabulary 
            to learn {{ learning_language }} in multiple-choice format with {{ num_answers }} answers, 
            display the answer for each question  and translate to {{ primary_language }}
            Do not include any explanations, only provide a RFC8259 compliant JSON response following 
            this format without deviation, the lesson must not include a newline and special characters:
            {
                    "{{ learning_language }}": {{ format_output }},
                    "{{ primary_language }}": {{ format_output }}
            }
        """

    def __init__(self, model: OpenAI, voca_repository: VocabularyRepository):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model = model
        self.voca_repository = voca_repository

    def generate_vocabulary_questions(
            self,
            category: str,
            translated_language: str,
            learning_language: str,
            user_id: str,
            num_questions: int = 4,
            num_answers: int = 5,
    ):
        try:
            prompt_template: PromptTemplate = PromptTemplate.from_template(
                self._vocabulary_template, template_format="jinja2"
            )

            prompt = prompt_template.format(
                category=category,
                primary_language=translated_language,
                learning_language=learning_language,
                num_questions=num_questions,
                num_answers=num_answers,
                format_output=self._vocabulary_format,
            )
            self.logger.debug("START STREAMING")

            result: str = ""
            for response in self.model.stream(prompt):
                self.logger.debug(response)
                result += response
                yield response
            result = result.replace("\\n", " ")
            result = result.replace("\n", " ")
            loads_result = json.loads(result)
            learning_obj = parse_json_prompt(
                category,
                learning_language,
                translated_language,
                loads_result,
            )
            self._add_lesson_to_database(learning_obj, user_id)

        except ValueError as e:
            self.logger.error(e.__str__())
            raise PromptParserException()

    def _add_lesson_to_database(
            self, learning_obj: VocabularyPromptCreate, user_id: str
    ) -> None:
        self.voca_repository.create_with_category(learning_obj, user_id)


class PromptParserException(Exception):
    def __init__(self) -> None:
        super().__init__("Can not parse prompt response to json")
