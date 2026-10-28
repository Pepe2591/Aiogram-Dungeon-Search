import types

from aiogram import Router, F
from aiogram.types import Message

from database.models import Clan
from tools.filters import IsRegisteredFilter, ChatTypeFilter
from config import text_profile, text_admin_profile

from database.requests import get_profile

infc_profile_router = Router()

infc_profile_router.message.filter(
    ChatTypeFilter('private'), # type: ignore
    IsRegisteredFilter() # type: ignore
)

@infc_profile_router.message(F.text == '🎩 Профиль')
async def show_profile(message: Message):
    profile = await get_profile(message.from_user.id)
    member = profile.member

    clan_name = member.clan.name if member and member.clan else 'Отсутствует'
    role_name = member.role.name if member and member.role else 'Отсутствует'

    if profile.admin_role:
        await message.answer(
            text_admin_profile.format(
                profile.nickname,
                clan_name,
                role_name,
                profile.admin_role.name,
                profile.admin_role.level_access,
                profile.created_at.strftime("%d.%m.%Y")
            ),
        )
    else:
        await message.answer(
            text_profile.format(
                profile.nickname,
                clan_name,
                role_name,
                profile.created_at.strftime("%d.%m.%Y")
            ),
        )