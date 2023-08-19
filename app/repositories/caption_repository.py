import logging
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.models.image_caption import ImageCaption


class CaptionRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )

    def add(self, image_caption: ImageCaption) -> ImageCaption | None:
        with self.session_factory() as session:
            session.add(image_caption)
            session.commit()
            session.refresh(image_caption)
            return image_caption
