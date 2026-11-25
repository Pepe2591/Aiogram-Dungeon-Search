from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.models import User, Profile, Member, async_session

from database.requests import get_profile
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload
from tools.filters import IsRegisteredFilter, ChatTypeFilter
from config import TEXT_PROFILE, TEXT_ADMIN_PROFILE
from tools.utis import ollama_answer, split_text

group_profile_router = Router()

group_profile_router.message.filter(
    ChatTypeFilter(['group', 'supergroup', 'channel']), # type: ignore
    IsRegisteredFilter()
)


@group_profile_router.message(
    (F.text.lower() == "u") | F.text.regexp(r"(?i)^u\s+@?\w{3,32}$")
)
async def u(message: Message):
    parts = message.text.split(maxsplit=1)
    username = parts[1].lstrip("@") if len(parts) > 1 else None

    stmt = (
        select(Profile)
        .join(User, Profile.user_fk == User.id)
        .options(
            selectinload(Profile.admin_role),
            selectinload(Profile.member).options(
                selectinload(Member.role),
                selectinload(Member.clan),
            ),
        )
    )

    if username:
        stmt = stmt.where(
            func.lower(func.ltrim(User.username, "@")) == username.lower()
        )
    elif message.reply_to_message and message.reply_to_message.from_user:
        stmt = stmt.where(User.tg_id == message.reply_to_message.from_user.id)
    else:
        stmt = stmt.where(User.tg_id == message.from_user.id)

    async with async_session.begin() as session:
        profile = await session.scalar(stmt)

        if profile is None:
            await message.reply("Профиль игрока не найден.")
            return

        member = profile.member
        clan_name = member.clan.name if member and member.clan else "Отсутствует"
        role_name = member.role.name if member and member.role else "Отсутствует"
        created = profile.created_at.strftime("%d.%m.%Y")

        if profile.admin_role:
            text = TEXT_ADMIN_PROFILE.format(
                profile.nickname,
                clan_name,
                role_name,
                profile.admin_role.name,
                profile.admin_role.level_access,
                created,
            )
        else:
            text = TEXT_PROFILE.format(profile.nickname, clan_name, role_name, created)

    await message.reply(text)