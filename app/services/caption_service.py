from app.models.image_caption import ImageCaption
from app.repositories.caption_repository import CaptionRepository


class CaptionService:
    def __init__(self, image_caption_repository: CaptionRepository) -> None:
        self._repository: CaptionRepository = image_caption_repository

    def add_image_caption(self, image_caption: ImageCaption) -> ImageCaption | None:
        return self._repository.add(image_caption)
