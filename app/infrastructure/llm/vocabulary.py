import logging
from datetime import datetime
from typing import Generator

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
            Create a prompt lesson more than 100 words about {{ category }} with difficult in level {{ level }} and suggest {{ num_questions }} vocabulary 
            to learn {{ learning_language }} in multiple-choice format with {{ num_answers }} options, 
            display the answer for each question , make sure the questions make sense, the answer exists in {{ num_answers }} options and translate to {{ primary_language }}
            Do not include any explanations, the lesson must not include a newline and special character and do not 
            return anything in your response outside of curly braces. Only provide a RFC8259 compliant JSON response 
            following this format without deviation:
            
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
        level: int = 1,
    ) -> Generator:
        start = datetime.now()
        prompt_template: PromptTemplate = PromptTemplate.from_template(
            self._vocabulary_template, template_format="jinja2"
        )
        response = ""
        prompt = prompt_template.format(
            category=category,
            primary_language=translated_language,
            learning_language=learning_language,
            num_questions=num_questions,
            num_answers=num_answers,
            format_output=self._vocabulary_format,
            level=level,
        )

        self.logger.debug(f"Request: {prompt}")
        for text in self.model.stream(prompt):
            response += text
            yield text

        self.logger.debug(f"Execution time: {datetime.now() - start}")
        self.logger.debug(f"Response: {response}")
