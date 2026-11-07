from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select

from tools.filters import IsRegisteredFilter, ChatTypeFilter,IsMemberFilter
from config import TEXT_PROFILE, TEXT_ADMIN_PROFILE

from database.models import async_session, Clan
from database.requests import get_profile


infc_profile_router = Router()

infc_profile_router.message.filter(
    ChatTypeFilter('private'), # type: ignore
    IsRegisteredFilter() # type: ignore
)

@infc_profile_router.message(F.text == '🔎 Найти клан', ~IsMemberFilter())
async def show_settings(message : Message):

    async with async_session.begin() as session:
        req = await session.scalars(
            select(Clan)
        )
        clans = req.all()

    if clans:
        text = 'Бла-бла'
    else:
        await message.answer('Пока нет доступных кланов 🙌')

@infc_profile_router.message(F.text == '⚙️ Настройки')
async def show_settings(message : Message):
    await message.answer('Привет')


@infc_profile_router.message(F.text == '🎩 Профиль')
async def show_profile(message: Message):
    profile = await get_profile(message.from_user.id)
    member = profile.member

    clan_name = member.clan.name if member and member.clan else 'Отсутствует'
    role_name = member.role.name if member and member.role else 'Отсутствует'

    if profile.admin_role:
        await message.answer(
            TEXT_ADMIN_PROFILE.format(
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
            TEXT_PROFILE.format(
                profile.nickname,
                clan_name,
                role_name,
                profile.created_at.strftime("%d.%m.%Y")
            ),
        )