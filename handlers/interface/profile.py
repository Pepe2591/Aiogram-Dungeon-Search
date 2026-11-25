from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from tools.filters import IsRegisteredFilter, ChatTypeFilter,IsMemberFilter
from config import TEXT_PROFILE, TEXT_ADMIN_PROFILE

from database.models import async_session, Clan, Profile, User, Member


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
    await message.answer('Empty text')


@infc_profile_router.message(F.text == '🎩 Профиль')
async def show_profile(message: Message):
    async with async_session() as session:
        profile = await session.scalar(
            select(Profile)
            .join(User)
            .where(User.tg_id == message.from_user.id)
            .options(
                joinedload(Profile.admin_role),
                joinedload(Profile.member).options(
                    joinedload(Member.role),
                    joinedload(Member.clan),
                ),
            )
        )

    if profile is None:
        await message.answer("Профиль не найден.")
        return

    member = profile.member
    clan_name = member.clan.name if member and member.clan else 'Отсутствует'
    role_name = member.role.name if member and member.role else 'Отсутствует'
    created = profile.created_at.strftime("%d.%m.%Y")

    if profile.admin_role:
        text = TEXT_ADMIN_PROFILE.format(
            profile.nickname, clan_name, role_name,
            profile.admin_role.name, profile.admin_role.level_access, created,
        )
    else:
        text = TEXT_PROFILE.format(profile.nickname, clan_name, role_name, created)

    await message.answer(text)