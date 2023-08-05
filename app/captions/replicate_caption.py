from io import BytesIO
import replicate
from fastapi.responses import StreamingResponse

from app.core import config
from app.utils.utils import logger


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
            )
            caption = []
            for word in output:
                caption.append(word)
        except Exception as e:
            logger.error(f"Replicate Error {e}", exc_info=True)
            return None
        
        return "".join(caption)
