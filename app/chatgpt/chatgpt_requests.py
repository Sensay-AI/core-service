import openai

from app.core import config
from app.utils.utils import logger

openai.api_key = config.OPENAI_API_KEY
prompts = {
    "translate": "rewrite this paragraph in {language}, keeping the meaning but use suitable wording, "
    "make the paragraph sound good : {caption}"
}


def rewrite_caption_in_language(caption: str, language: str) -> str:
    prompt = prompts["translate"]
    prompt = prompt.format(caption=caption, language=language)
    response_message = ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": prompt}],
        )
        response_message = response["choices"][0]["message"]["content"]
    except Exception as error:
        logger.error(f"Chatgpt Error {error}", exc_info=True)
    return response_message
