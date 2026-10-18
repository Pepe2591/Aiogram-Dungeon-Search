import os
from typing import cast

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup


from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(), override=True)


def response_text(text : str) -> str:
    """Обращается к чат gpt через api_key и выдает текст"""

    client = OpenAI(api_key=os.getenv('API_KEY'))

    response = client.responses.create(
    model="gpt-6-astra",
    input=text,
)
    return response.output_text
         