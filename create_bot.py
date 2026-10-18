import os 

from dotenv import load_dotenv, find_dotenv 

from aiogram import Bot 
from aiogram.enums import ParseMode 
from aiogram.client.default import DefaultBotProperties 

load_dotenv(find_dotenv(), override=True)

token = os.getenv("TOKEN")

if not token:
    raise ValueError("TOKEN environment variable not found")


bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML, 
        link_preview_is_disabled=True 
    )
)