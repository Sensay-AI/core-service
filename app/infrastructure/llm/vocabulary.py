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
        "Create a {{ level }}-level vocabulary lesson in the context of {{ category }}."
        "Teach the students {{ num_questions }} different words. "
        "The lesson content will be like this: the list words can be a mix of nouns, "
        "verbs, adjectives, or adverbs, present each word and its part of speech in {{ learning_language }} "
        "along with its {{ primary_language }} TRANSLATION, then, include a detailed description of the word"
        " in the relevant context in {{ primary_language }}, "
        "after use the word in an example sentence in {{ learning_language }} , "
        "include the {{ primary_language }} translation of that sentence, "
        "put all of this content in a single paragraph. "
        "Create {{ num_questions }} multiple-choice questions. "
        "Each vocabulary word should have 1 question along with 3 possible answers. "
        "The questions and answers should be written in {{ learning_language }} . "
        "The questions must effectively test the understanding of the recently"
        " taught vocabulary words and present a challenge to the students. "
        "Include the {{ primary_language }} translation of the questions. "
        "Include the answer key at the end of the lesson. "
        "Do not include any explanations, and do not  return anything in your response outside of curly braces. "
        "Only provide a RFC8259 compliant JSON response following this format without deviation:"
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
