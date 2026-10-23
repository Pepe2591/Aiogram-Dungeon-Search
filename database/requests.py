from email import message

from aiogram.types import Message
from sqlalchemy import select, insert

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


async def get_user(tg_id : int) -> User | None:
    """Возвращает объект User по tg_id, если объект не найден, отдает None"""
    async with async_session.begin() as session:
        req = await session.execute(
            select(User.id)
            .order_by(User.tg_id == tg_id)
        )
    return req.scalar_one_or_none()

async def get_profile(tg_id : int) -> Profile | None:
    """Возвращает объект Profile по tg_id, если объект не найден, отдает None"""
    async with async_session.begin() as session:
        req = await session.execute(
            select(Profile)
            .join(User)
            .where(User.tg_id == tg_id)
        )
    return req.scalar_one_or_none()

async def get_member(tg_id : int) -> Member | None:
    """Возвращает объект Member по tg_id, если объект не найден, отдает None"""
    async with async_session.begin() as session:
        req = await session.execute(
            select(Member)
            .join(Profile)
            .join(User)
            .where(User.tg_id == tg_id)
        )
    return req.scalar_one_or_none()


async def create_user(message : Message) -> User:
    """Извлекает информацию из message и создает из него нового пользователя"""
    if await get_user(message.from_user.id):
        raise ValueError('This user already exists!')

    async with async_session.begin() as session:
        user = User(
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            tg_id=message.from_user.id
        )

        session.add(user)
    return user


async def create_profile(tg_id: int, nickname: str, admin_rank: int) -> Profile:
    """Создает профиль их полученных данных"""

    user = await get_user(tg_id)

    if user is None:
        raise ValueError('User is not already exists!')
    elif await get_profile(tg_id):
        raise ValueError('This profile already exists!')

    async with async_session.begin() as session:
        profile = Profile(
            nickname=nickname,
            admin_rank=admin_rank,
            user_fk=user.id
        )

        session.add(profile)

    return profile


async def create_member(tg_id: int, clan_id : int, profile_id : int, role_id) -> Member:
    profile = await get_profile(tg_id)

    if profile is None:
        raise ValueError('Profile is not already exists!')
    elif await get_member(tg_id):
        raise ValueError('This member already exists!')

    async with async_session.begin() as session:

        query = await session.execute(
            select(Clan)
            .filter_by(id = clan_id)
        )

        clan = query.scalar_one_or_none()

        if clan is None:
            raise ValueError('Clan is not already exists!')
        elif await session.get(Role, role_id) is None:
            raise ValueError('Role is not exists!')

        member = Member(
            is_banned=False,
            is_muted=False,

            profile_fk=profile_id,
            clan_fk=clan_id,
            role_fk=role_id,
        )

        session.add(member)
    return member