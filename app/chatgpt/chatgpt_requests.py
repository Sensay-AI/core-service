import openai
import json

from app.core import config
from app.utils.utils import logger

openai.api_key = config.OPENAI_API_KEY
prompt_list = json.load(open("app/chatgpt/prompts.json", encoding='utf8'))


def rewrite_caption_in_language(caption, language):
    prompt = prompt_list["translate"]
    prompt = eval(f"f'{prompt}'")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": prompt}],
        )
        response_message = response["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Chatgpt Error {e}", exc_info=True)
        return None
    return response_message
