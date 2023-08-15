from io import BytesIO

import replicate
from replicate.exceptions import ReplicateError
from singleton_decorator import singleton

from app.core import config
from app.utils.utils import logger


@singleton
class CaptionGenerator:
    def __init__(self, model_id, caption_client) -> None:
        self.model_id = model_id
        self.caption_client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

    def generate_from_image(self, prompt: str, image_file: BytesIO) -> str:
        caption = []
        try:
            output = self.caption_client.run(
                self.model_id, input={"prompt": prompt, "img": image_file}
            )

            for word in output:
                caption.append(word)
        except ReplicateError as e:
            logger.error(f"Replicate Error {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Got an error when generating caption: {e}", exc_info=True)

        return "".join(caption)
