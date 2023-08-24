import json
from typing import Generator

from app.infrastructure.captions.replicate_caption import CaptionGenerator
from app.infrastructure.llm.caption import ChatGPTCaption
from app.models.db.image_caption import ImageCaption
from app.repositories.caption_repository import CaptionRepository
from app.services.base_service import BaseService


class CaptionService(BaseService):
    def __init__(
        self,
        image_caption_repository: CaptionRepository,
        caption_generator: CaptionGenerator,
        chatgpt_caption: ChatGPTCaption,
    ) -> None:
        super().__init__(image_caption_repository)
        self._repository: CaptionRepository = image_caption_repository
        self.caption_generator = caption_generator
        self.chatgpt_caption = chatgpt_caption

    def add_image_caption(self, image_caption: ImageCaption) -> ImageCaption | None:
        return self._repository.add_image_caption(image_caption)

    def get_caption_from_image(
        self, user_id: str, caption_input: dict
    ) -> Generator:
        caption = self.caption_generator.generate_from_image(
            prompt="Generate a caption for the following image",
            image_file=caption_input["file"],
        )
        rewritten_caption = ""
        for text in self.chatgpt_caption.rewrite_caption(
            caption=caption,
            primary_language=caption_input['primary_language'],
            learning_language=caption_input['learning_language']
        ):
            rewritten_caption += text
            yield text
        caption_data = json.loads(rewritten_caption)
        new_image_caption = ImageCaption(
            user_id=user_id,
            image_url=caption_input["path"],
            caption_learning_language=caption_data['learning_language'],
            caption_primary_language=caption_data['primary_language']
        )
        self.add_image_caption(new_image_caption)
