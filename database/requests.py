from sqlalchemy import select, exists

from aiogram.types import Message

from database.models import async_session, Profile, User, Member


async def check_access(lvl_access : int, message : Message) -> bool:
    """Проверяет права человека по сообщению, если все в порядке пропускает его дальше"""
    async with async_session.begin() as session:
        req = await session.execute(
            select(Profile.admin_rank)
            .join(User, User.tg_id == message.from_user.id)
        )
        result = req.scalar_one_or_none()

        return result is not None and result >= lvl_access


async def user_is_exist(tg_id : int) -> bool:
    async with async_session.begin() as session:
        req = await session.execute(
            select(
                select(User.id)
                .order_by(User.tg_id == tg_id)
            )
        )
    return req.scalar()

async def profile_is_exist(tg_id : int) -> bool:
    async with async_session.begin() as session:
        req = await session.execute(
            select(
                select(Profile)
                .join(User)
                .where(User.tg_id == tg_id)
                .exists()
            )
        )
    return req.scalar()

async def member_is_exist(tg_id : int) -> bool:
    async with async_session.begin() as session:
        req = await session.execute(
            select(User)
            .join(Profile)
            .join(Member)
            .where(User.tg_id == tg_id)
            .exists()
        )
    return req.scalar()