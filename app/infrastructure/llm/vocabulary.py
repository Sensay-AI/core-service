import logging
import textwrap
from datetime import datetime
from typing import Generator

from langchain import OpenAI, PromptTemplate


class ChatGPTVocabularyGenerator:
    _vocabulary_format = """{
        "lesson": "<prompt of lesson without a newline>",
        "questions": [
        {
        "question": "What is the term used for a person who runs in a race?",
        "options": ["Swimmer", "Runner", "Cyclist",...],
        "answer": "Runner"
        }
        ]
        }"""

    _vocabulary_template = (
        "Create a short language lesson in {{ learning_language }} of no more than 300 words. You will teach the "
        "students {{ num_questions }} {{ level }} vocabulary words in the context of {{ category }}. Then, create "
        "{{ num_questions }} multiple choice questions with {{ num_answers }} possible answers for each question. "
        "Each question should elicit the meaning of the vocabulary words you just taught them. You can ask the students"
        "questions about the meaning of the word as well as questions about how the word is used in context. "
        "Make sure the the answer exists in {{ num_answers }} options. "
        "Write the translations of the questions, answers, and instructions in {{ primary_language }} "
        "Do not include any explanations, the lesson must not include a newline and special character and do not "
        "return anything in your response outside of curly braces. Only provide a RFC8259 compliant JSON response "
        "following this format without deviation: "
        '{"{{ learning_language }}": {{ format_output }}, "{{ primary_language }}": {{ format_output }}}'
    )

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
        level: str = "EASY",
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
            format_output=textwrap.dedent(self._vocabulary_format),
            level=level,
        )

        prompt = textwrap.dedent(prompt)
        self.logger.debug(f"Request: {prompt}")
        for text in self.model.stream(prompt):
            response += text
            yield text

        self.logger.debug(f"Execution time: {datetime.now() - start}")
        self.logger.debug(f"Response: {response}")
