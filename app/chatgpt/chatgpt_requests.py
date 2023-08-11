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
    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        logger.error(f"OpenAI API returned an API Error: {e}", exc_info=True)
        pass
    except openai.error.APIConnectionError as e:
        # Handle connection error here
        logger.error(f"Failed to connect to OpenAI API: {e}", exc_info=True)
        pass
    except openai.error.RateLimitError as e:
        # Handle rate limit error (we recommend using exponential backoff)
        logger.error(f"OpenAI API request exceeded rate limit: {e}", exc_info=True)
        pass
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return response_message
