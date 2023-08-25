from io import BytesIO

from replicate import Client


class CaptionGenerator:
    # TODO: naming of the package in this folder must be more consistent
    #  https://github.com/Sensay-AI/core-service/pull/9#discussion_r1306129822

    def __init__(self, caption_client: Client, model_id: str) -> None:
        self.caption_client = caption_client
        self.model_id = model_id

    def generate_from_image(self, image_file: BytesIO) -> str:
        caption = ""
        output = self.caption_client.run(self.model_id, input={"image": image_file})
        for word in output:
            caption += word
        return caption
