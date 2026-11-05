import aiohttp

from aiogram.filters.callback_data import CallbackData
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(), override=True)

class AdminAction(CallbackData, prefix='admin'):
    name_action : str
    lvl_access : int


def split_text(text: str, limit: int = 4000) -> list[str]:
    chunks = []

    while len(text) > limit:
        split_index = text.rfind('\n', 0, limit)

        if split_index == -1:
            split_index = text.rfind(' ', 0, limit)

        if split_index == -1:
            split_index = limit

        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()

    if text:
        chunks.append(text)

    return chunks

async def ollama_answer(
        prompt : str, url = 'http://localhost:11434/api/generate', model = 'qwen3:8b',
        think = False, stream = False):

    async with aiohttp.ClientSession() as session:
        async with session.post(
                url,
                json={
                    "model" : model,
                    "prompt" : prompt,
                    "think" : think,
                    "stream" : stream
                }
        ) as response:
            result = await response.json()
            return result['response']