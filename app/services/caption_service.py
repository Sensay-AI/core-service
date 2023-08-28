import json
from typing import Generator

from app.infrastructure.llm.caption import ChatGPTCaptionGenerator
from app.infrastructure.replicate.caption import CaptionGenerator
from app.models.schemas.image_caption import ImageCaptionCreate
from app.repositories.caption_repository import (
    CaptionRepository,
    TranslatedCaptionRepository,
)


class CaptionService:
    def __init__(
        self,
        primary_caption_repository: CaptionRepository,
        learning_caption_repository: TranslatedCaptionRepository,
        caption_generator: CaptionGenerator,
        chatgpt_caption: ChatGPTCaptionGenerator,
    ) -> None:
        self.primary_caption_repository = primary_caption_repository
        self.learning_caption_repository = learning_caption_repository
        self.caption_generator = caption_generator
        self.chatgpt_caption = chatgpt_caption

    def get_caption_from_image(self, user_id: str, caption_input: dict) -> Generator:
        caption = self.caption_generator.generate_from_image(
            image_file=caption_input["file"],
        )
        rewritten_caption = ""
        for text in self.chatgpt_caption.rewrite_caption(
            caption=caption,
            primary_language=caption_input["primary_language"],
            learning_language=caption_input["learning_language"],
        ):
            rewritten_caption += text
            yield text
        caption_data = json.loads(rewritten_caption)
        new_image_caption = ImageCaptionCreate(
            image_path=caption_input["path"],
            caption=caption_data[caption_input["primary_language"]],
            primary_language=caption_input["primary_language"],
        )
        caption_insert_object = self.primary_caption_repository.add_image_caption(
            user_id=user_id, image_caption=new_image_caption
        )
        self.learning_caption_repository.add_translated_caption(
            learning_caption=caption_data[caption_input["learning_language"]],
            learning_language=caption_input["learning_language"],
            image_caption_object=caption_insert_object,
        )
