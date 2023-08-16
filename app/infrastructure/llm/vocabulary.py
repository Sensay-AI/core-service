import json
import logging
from datetime import datetime
from typing import Any

from langchain import OpenAI, PromptTemplate


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

    def __init__(self, model: OpenAI):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model = model

    def generate_vocabulary_questions(
        self,
        category: str,
        translated_language: str,
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
                primary_language=translated_language,
                learning_language=learning_language,
                num_questions=num_questions,
                num_answers=num_answers,
                format_output=self._vocabulary_format,
            )
            self.logger.debug(f"Prompt: {prompt}")
            response = self.model.predict(prompt)
            response = response.replace("\\n", " ")
            response = response.replace("\n", " ")
            self.logger.debug(f"Execution time: {datetime.now() - start}")
            self.logger.debug(f"Response: {response}")
            return json.loads(response)
        except ValueError as e:
            self.logger.error(e.__str__())
            raise PromptParserException()


class PromptParserException(Exception):
    def __init__(self) -> None:
        super().__init__("Can not parse prompt response to json!")
