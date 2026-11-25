from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram.fsm.state import State, StatesGroup
from database.models import async_session, Profile, Member, User

from database.requests import create_user, create_profile
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from tools.filters import ChatTypeFilter
from tools.images import reg_icon

from config import TEXT_REG
from handlers.keyboards import keyboard_fabric

main_router = Router()

class RegisterUser(StatesGroup):
    nickname = State()


@main_router.message(CommandStart(), ChatTypeFilter('private')) # type: ignore
async def start(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id

    async with async_session.begin() as session:
        user = await session.scalar(
            select(Profile)
            .join(User)
            .where(User.tg_id == tg_id)
            .options(
                selectinload(Profile.admin_role),
                selectinload(Profile.member)
                .options(
                    selectinload(Member.clan)
                    )
                )
            )

    if user:
        txt_bts = ['🎩 Профиль']

        if user.member:
            txt_bts.append('💠 Клан')
        if not user.member:
            txt_bts.append('🔎 Найти клан')
        if user.admin_role.level_access > 0:
            txt_bts.append('👮 Админ панель')

        txt_bts.append('⚙️ Настройки')

        await message.answer(
            'Клавиатура успешно обновлена!',
            reply_markup=keyboard_fabric(tuple(txt_bts), 2, True))

    else:
        await state.set_state(RegisterUser.nickname)
        await message.answer_photo(photo=reg_icon, caption=TEXT_REG)


@main_router.message(RegisterUser.nickname)
async def reg_nickname(message: Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer('Ваше имя должно быть меньше 30 символов!')
        await state.set_state(RegisterUser.nickname)


    await create_user(message)
    await create_profile(message.from_user.id, message.text, 0)
    await state.clear()
    await message.answer(
        'Вы успешно авторизовались!',
        reply_markup=keyboard_fabric(
            ('🎩 Профиль', '🔎 Найти клан', '⚙️ Настройки'),
            2,
            True
        )
    )

