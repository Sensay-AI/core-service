from typing import Any

from app.models.db.image_caption import ImageCaption, ImageCaptionTranslation
from app.models.schemas.image_caption import ImageCaptionCreate
from app.repositories.base_repository import BaseRepository
from app.repositories.vocabulary_repository import check_language


class CaptionRepository(BaseRepository[ImageCaption, ImageCaptionCreate, Any]):
    # TODO: Refactor this code like Minh comment in the discussion here
    #  https://github.com/Sensay-AI/core-service/pull/9#discussion_r1306123877
    def add_image_caption(
        self, user_id: str, image_caption: ImageCaptionCreate
    ) -> None:
        with self.session_factory() as session:
            learning_language_id = check_language(
                session, image_caption.learning_language
            )
            primary_language_id = check_language(
                session, image_caption.primary_language
            )
            img_caption = ImageCaption(
                user_id=user_id,
                image_bucket_path_key=image_caption.image_path,
                caption=image_caption.caption,
                language_id=primary_language_id,
            )
            translated_image_caption = ImageCaptionTranslation(
                translated_language_id=learning_language_id,
                translated_caption=image_caption.translation,
                caption=img_caption,
            )
            session.add(img_caption)
            session.add(translated_image_caption)
            session.commit()
