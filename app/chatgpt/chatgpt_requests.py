import openai
<<<<<<< HEAD
=======
import json
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)

from app.core import config
from app.utils.utils import logger

openai.api_key = config.OPENAI_API_KEY
<<<<<<< HEAD
prompts = {
    "translate": "rewrite this paragraph in {language}, keeping the meaning but use suitable wording, "
    "make the paragraph sound good : {caption}"
}


def rewrite_caption_in_language(caption: str, language: str) -> str:
    prompt = prompts["translate"]
    prompt = prompt.format(caption=caption, language=language)
    response_message = ""
=======
prompt_list = json.load(open("app/chatgpt/prompts.json", encoding='utf8'))


def rewrite_caption_in_language(caption, language):
    prompt = prompt_list["translate"]
    prompt = eval(f"f'{prompt}'")
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": prompt}],
        )
        response_message = response["choices"][0]["message"]["content"]
<<<<<<< HEAD
    except Exception as error:
        logger.error(f"Chatgpt Error {error}", exc_info=True)
=======
    except Exception as e:
        logger.error(f"Chatgpt Error {e}", exc_info=True)
        return None
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
    return response_message
