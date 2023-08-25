import logging
from typing import Generator

from langchain import OpenAI, PromptTemplate


class ChatGPTCaption:
    # TODO: naming of the package in this folder must be more consistent
    #  https://github.com/Sensay-AI/core-service/pull/9#discussion_r1306129822

    _caption_template = """
        Create a paragraph of less than 30 words based on the following description : {{ description }} . 
        Do the translation in two languages: {{ primary_language }} and {{ learning_language }} ,use suitable wording and make them sound good, the orignial meaning must be kept and no information can be made up.
        Do not include any explanations, the paragraph must not include a newline and special character and do not 
        return anything in your response outside of curly braces. Only provide a RFC8259 compliant JSON response 
        following this format without deviation:
        
        {
                "{{ learning_language }}": "paragraph in learning language",
                "{{ primary_language }}": "paragraph in primary language"
        }
    """

    def __init__(self, model: OpenAI):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model = model

    def rewrite_caption(
        self, learning_language: str, primary_language: str, caption: str
    ) -> Generator:
        caption_template: PromptTemplate = PromptTemplate.from_template(
            self._caption_template, template_format="jinja2"
        )

        prompt = caption_template.format(
            primary_language=primary_language,
            learning_language=learning_language,
            description=caption,
        )
        result: str = ""
        for response in self.model.stream(prompt):
            result += response
            yield response
