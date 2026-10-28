import types

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from database.requests import get_profile

from tools.filters import IsRegisteredFilter, ChatTypeFilter

from config import text_profile, text_admin_profile

group_profile_router = Router()

group_profile_router.message.filter(
    ChatTypeFilter(['group', 'supergroup', 'channel']), # type: ignore
    IsRegisteredFilter()
)

@group_profile_router.message(F.text == 'u')
async def u(message: Message):
    profile = await get_profile(message.reply_to_message.from_user.id)

    if profile is None:
        await message.answer("Профиль игрока не найден.")
        return

    member = profile.member
    clan_name = member.clan.name if member and member.clan else "Отсутствует"
    role_name = member.role.name if member and member.role else "Отсутствует"

    if profile.admin_role:
        text = text_admin_profile.format(
            profile.nickname,
            clan_name,
            role_name,
            profile.admin_role.name,
            profile.admin_role.level_access,
            profile.created_at.strftime("%d.%m.%Y")
        )
    else:
        text = text_profile.format(
            profile.nickname,
            clan_name,
            role_name,
            profile.created_at.strftime("%d.%m.%Y")
        )

    await message.answer(text)