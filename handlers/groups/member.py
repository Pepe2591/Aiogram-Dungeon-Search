from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from tools.filters import IsRegisteredFilter

group_member_router = Router()

group_member_router.message.filter(
    IsRegisteredFilter(), # type: ignore
)


@group_member_router.message(Command('Test'))
async def test(message: Message):
    await message.answer('Проверка')
