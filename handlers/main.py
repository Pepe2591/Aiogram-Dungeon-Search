from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload

from database.models import async_session, User, Profile

main_router = Router()

@main_router.message(CommandStart()) # type: ignore
async def start(message: Message, state: FSMContext):
    async with async_session.begin() as session:

        query = await session.execute(
            select(Profile)
            .options(selectinload(Profile.user))
            .where(User.tg_id == message.from_user.id)
        )

    if query.scalar() is not None:
        pass

