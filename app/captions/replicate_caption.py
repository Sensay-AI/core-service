from io import BytesIO
<<<<<<< HEAD

import replicate
from singleton_decorator import singleton
=======
import replicate
from fastapi.responses import StreamingResponse
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)

from app.core import config
from app.utils.utils import logger


<<<<<<< HEAD
@singleton
class CaptionGenerator:
    def __init__(self) -> None:
        self.mplug_model_id = config.IMAGE_CAPTIONING_MODEL
        self.replicate_generator = replicate.Client(
            api_token=config.REPLICATE_API_TOKEN
        )

    def generate_from_image(self, prompt: str, image_file: BytesIO) -> str:
        try:
            output = self.replicate_generator.run(
                self.mplug_model_id, input={"prompt": prompt, "img": image_file}
=======
class CaptionGenerator:
    def __init__(self) -> None:
        self.mplug_model_id = config.IMAGE_CAPTIONING_MODEL
        self.replicate_generator = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

    def generate_from_image(self, prompt: str, image_file: BytesIO):
        try:
            output = self.replicate_generator.run(
                self.mplug_model_id,
                input={"prompt": prompt,
                       "img": image_file}
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
            )
            caption = []
            for word in output:
                caption.append(word)
        except Exception as e:
            logger.error(f"Replicate Error {e}", exc_info=True)
<<<<<<< HEAD
            return ""
=======
            return None
        
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
        return "".join(caption)
