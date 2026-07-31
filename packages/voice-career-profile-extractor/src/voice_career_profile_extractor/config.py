import os

from dotenv import load_dotenv
from openai import OpenAI


def get_openai_api_key() -> str:
    """
    Load and validate the OpenAI API key.
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Add it to a local .env file or export it in your terminal."
        )

    return api_key


def create_openai_client() -> OpenAI:
    """
    Create an authenticated OpenAI API client.
    """
    return OpenAI(api_key=get_openai_api_key())
