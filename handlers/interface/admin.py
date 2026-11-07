from aiogram import Router, F
from aiogram.types import Message

from tools.filters import ChatTypeFilter

infc_admin_router = Router()

infc_admin_router.message.filter(
    ChatTypeFilter('private') # type: ignore
)

@infc_admin_router.message(F.text == '👮 Админ панель')
async def show_settings(message : Message):
    await message.answer('Test')