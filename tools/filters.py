from aiogram.filters import BaseFilter
from aiogram.types import Message

from sqlalchemy import select
from database.models import async_session, User, Profile, Member, AdminRole


class ChatTypeFilter(BaseFilter):
    """Определяет тип чата, и если он соответствует ранее введенному типу/типам возвращает true"""

    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types


class IsRegisteredFilter(BaseFilter):
    """Проверяет, зарегистрирован ли пользователь,
    если да пропускает сообщение, в противном случае игнорирует"""

    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False

        async with async_session.begin() as session:
            query = await session.execute(
                select(User.id)
                .join(Profile)
                .where(User.tg_id == message.from_user.id)
            )
            result = query.scalar_one_or_none()

        return result is not None


class IsMemberFilter(BaseFilter):
    """Проверяет, является ли пользователь участником клана,
    если является пропускает сообщения, в противном случае игнорирует"""

    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False

        async with async_session.begin() as session:
            query = await session.execute(
                select(Member.id)
                .join(Profile)
                .join(User)
                .where(User.tg_id == message.from_user.id)
            )
            # результат читаем внутри блока, пока сессия открыта
            result = query.scalar_one_or_none()

        return result is not None


class IsAdminAccessFilter(BaseFilter):
    """Пропускает сообщение, если уровень доступа админа >= lvl_access"""

    def __init__(self, lvl_access: int) -> None:
        self.lvl_access = lvl_access

    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False

        async with async_session.begin() as session:
            query = await session.execute(
                select(AdminRole.level_access)
                .join(Profile)
                .join(User)
                .where(User.tg_id == message.from_user.id)
            )
            result = query.scalar_one_or_none()

        if result is None:
            return False

        return result <= self.lvl_access