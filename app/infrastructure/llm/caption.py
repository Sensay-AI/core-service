import logging
from datetime import datetime
from typing import Generator

from langchain import OpenAI, PromptTemplate


class ChatGPTCaption:
    _caption_trans_template = """
            rewrite this paragraph in {{ language }}, keeping the meaning but use suitable wording,
            make the paragraph sound good : {{ caption }}
        """

    def __init__(self, model: OpenAI):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model = model

    def rewrite_caption(self, language: str, caption: str) -> Generator:
        prompt_template: PromptTemplate = PromptTemplate.from_template(
            self._caption_trans_template, template_format="jinja2"
        )

        prompt = prompt_template.format(languague=language, caption=caption)
        result: str = ""
        for response in self.model.stream(prompt):
            self.logger.debug(response)
            result += response
            yield response
