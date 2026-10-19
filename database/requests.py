from sqlalchemy import select

from aiogram.types import Message

from models import async_session, Profile, User



async def check_access(lvl_access : int, message : Message) -> bool:
    """Проверяет права человека по сообщению, если все в порядке пропускает его дальше"""
    async with async_session.begin() as session:
        req = await session.execute(
            select(Profile.admin_rank)
            .join(User, User.tg_id == message.from_user.id)
        )
        result = req.scalar_one_or_none()

        return result is not None and result >= lvl_access