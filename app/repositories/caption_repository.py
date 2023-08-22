from typing import Any

from app.models.image_caption import ImageCaption
from app.repositories.base_repository import BaseRepository


class CaptionRepository(
    BaseRepository[ImageCaption, Any]
):
    def add_image_caption(self, image_caption: ImageCaption) -> ImageCaption | None:
        with self.session_factory() as session:
            session.add(image_caption)
            session.commit()
            session.refresh(image_caption)
            return image_caption
