from io import BytesIO

from replicate import Client
from singleton_decorator import singleton


@singleton
class CaptionGenerator:
    def __init__(self, caption_client: Client, model_id: str) -> None:
        self.caption_client = caption_client
        self.model_id = model_id

    def generate_from_image(self, prompt: str, image_file: BytesIO) -> str:
        caption = []
        output = self.caption_client.run(
            self.model_id, input={"prompt": prompt, "img": image_file}
        )

        for word in output:
            caption.append(word)
        return "".join(caption)
