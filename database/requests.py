from email import message

from aiogram.types import Message
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload

from database.models import async_session, Profile, User, Member, Clan, Role


async def check_access(lvl_access : int, message : Message) -> bool:
    """Проверяет права человека по сообщению, если все в порядке пропускает его дальше"""
    async with async_session.begin() as session:
        req = await session.execute(
            select(Profile.admin_rank)
            .join(User, User.tg_id == message.from_user.id)
        )
        result = req.scalar_one_or_none()

        return result is not None and result >= lvl_access


async def get_user(tg_id: int) -> User | None:
    """Возвращает пользователя по tg_id или None."""
    async with async_session() as session:
        req = await session.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.tg_id == tg_id)
        )
        return req.scalar_one_or_none()


async def get_profile(tg_id: int) -> Profile | None:
    """Возвращает профиль пользователя по tg_id или None."""
    async with async_session() as session:
        req = await session.execute(
            select(Profile)
            .options(
                selectinload(Profile.user),
                selectinload(Profile.member),
            )
            .join(Profile.user)
            .where(User.tg_id == tg_id)
        )
        return req.scalar_one_or_none()


async def get_member(tg_id: int) -> Member | None:
    """Возвращает участника по tg_id или None."""
    async with async_session() as session:
        req = await session.execute(
            select(Member)
            .options(
                selectinload(Member.profile),
                selectinload(Member.clan),
                selectinload(Member.role),
            )
            .join(Member.profile)
            .join(Profile.user)
            .where(User.tg_id == tg_id)
        )
        return req.scalar_one_or_none()


async def create_user(message: Message) -> User:
    """Извлекает информацию из message и создает нового пользователя."""
    if await get_user(message.from_user.id):
        raise ValueError('This user already exists!')

    async with async_session.begin() as session:
        user = User(
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            tg_id=message.from_user.id,
        )
        session.add(user)

    return user


async def create_profile(tg_id: int, nickname: str, admin_rank: int) -> Profile:
    """Создает профиль из полученных данных."""
    user = await get_user(tg_id)

    if user is None:
        raise ValueError('User does not exist!')
    elif await get_profile(tg_id):
        raise ValueError('This profile already exists!')

    async with async_session.begin() as session:
        profile = Profile(
            nickname=nickname,
            admin_rank=admin_rank,
            user_fk=user.id,
        )
        session.add(profile)

    return profile


async def create_member(tg_id: int, clan_id: int, profile_id: int, role_id: int) -> Member:
    """Создает участника клана."""
    profile = await get_profile(tg_id)

    if profile is None:
        raise ValueError('Profile does not exist!')
    elif await get_member(tg_id):
        raise ValueError('This member already exists!')

    async with async_session.begin() as session:
        query = await session.execute(
            select(Clan)
            .where(Clan.id == clan_id)
        )
        clan = query.scalar_one_or_none()

        if clan is None:
            raise ValueError('Clan does not exist!')
        elif await session.get(Role, role_id) is None:
            raise ValueError('Role does not exist!')

        member = Member(
            is_banned=False,
            is_muted=False,
            profile_fk=profile_id,
            clan_fk=clan_id,
            role_fk=role_id,
        )
        session.add(member)

    return member