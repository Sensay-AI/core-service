from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.models.db.image_caption import (
    ImageCaptionLearningLanguage,
    ImageCaptionPrimaryLanguage,
)
from app.models.schemas.image_caption import ImageCaptionCreate
from app.repositories.vocabulary_repository import check_language


class CaptionRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
    ):
        self.session_factory = session_factory

    def add_image_caption(
        self, user_id: str, image_caption: ImageCaptionCreate
    ) -> ImageCaptionPrimaryLanguage:
        with self.session_factory() as session:
            primary_language_id = check_language(
                session, image_caption.primary_language
            )
            img_caption = ImageCaptionPrimaryLanguage(
                user_id=user_id,
                image_bucket_path_key=image_caption.image_path,
                caption=image_caption.caption,
                primary_language_id=primary_language_id,
            )
            session.add(img_caption)
            session.commit()
            return img_caption


class TranslatedCaptionRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
    ):
        self.session_factory = session_factory

    def add_translated_caption(
        self,
        learning_caption: str,
        learning_language: str,
        image_caption_object: ImageCaptionPrimaryLanguage,
    ) -> ImageCaptionLearningLanguage:
        with self.session_factory() as session:
            learning_language_id = check_language(session, learning_language)
            translated_image_caption = ImageCaptionLearningLanguage(
                learning_language_id=learning_language_id,
                learning_language_caption=learning_caption,
                caption=image_caption_object,
            )
            session.add(translated_image_caption)
            session.commit()
            return translated_image_caption
