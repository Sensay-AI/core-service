from io import BytesIO

from app.models.image_caption import ImageCaption
from app.repositories.caption_repository import CaptionRepository
from app.infrastructure.captions.replicate_caption import CaptionGenerator
from app.infrastructure.llm.caption import ChatGPTCaption
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
            self,
            image_file: BytesIO,
            language: str
    ):
        caption = self.caption_generator.generate_from_image(
            prompt="Generate a caption for the following image", image_file=image_file
        )
        rewritten_caption = self.chatgpt_caption.rewrite_caption(
            caption=caption, language=language
        )
        return rewritten_caption
