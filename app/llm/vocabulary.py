import json
import logging
from datetime import datetime
from http import HTTPStatus
from typing import Any

from fastapi import HTTPException
from langchain import PromptTemplate
from langchain.llms import OpenAI
from singleton_decorator import singleton

from app.core.config import OPEN_API_KEY

LOG = logging.getLogger(__name__)


@singleton
class ChatGPTVocabularyGenerator(object):
    _model = OpenAI(openai_api_key=OPEN_API_KEY, max_tokens=-1, temperature=0.5)

    _vocabulary_format = """{
                "lesson": <prompt of lesson>,
                "questions": [
                {
                    "Question": "What is the term used for a person who runs in a race?",
                    "Options": ["Swimmer", "Runner", "Cyclist"],
                    "Answer": "Runner"
                }
                ]
            }"""
    _vocabulary_template = """
            Create a prompt lesson more than 100 words about {{ category }} and suggest {{ num_questions }} vocabulary 
            to learn {{ learning_language }} in multiple-choice format with {{ num_answers }} answers, 
            display the answer for each question  and translate to {{ primary_language }}
            Do not include any explanations, only provide a RFC8259 compliant JSON response following 
            this format without deviation:
            {
                    "{{ learning_language }}": {{ format_output }},
                    "{{ primary_language }}": {{ format_output }}
            }
        """

    def __int__(self) -> Any:
        pass

    def generateVocabularyQuestion(
        self,
        category: str,
        primary_language: str,
        learning_language: str,
        num_questions: int = 4,
        num_answers: int = 5,
    ) -> dict[str, Any]:
        try:
            start = datetime.now()
            prompt_template: PromptTemplate = PromptTemplate.from_template(
                self._vocabulary_template, template_format="jinja2"
            )

            prompt = prompt_template.format(
                category=category,
                primary_language=primary_language,
                learning_language=learning_language,
                num_questions=num_questions,
                num_answers=num_answers,
                format_output=self._vocabulary_format,
            )
            LOG.debug(f"[Vocabulary] Prompt: {prompt}")

            response = self._model.predict(prompt)

            LOG.debug(f"[Vocabulary] Execution time: {datetime.now() - start}")

            return json.loads(response)

        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=str(e),
            )
