from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram.fsm.state import State, StatesGroup

from database.requests import get_profile, create_user, create_profile

from tools.filters import ChatTypeFilter
from tools.images import reg_icon

from config import text_reg
from handlers.keyboards import keyboard_fabric

main_router = Router()

class RegisterUser(StatesGroup):
    nickname = State()


@main_router.message(CommandStart(), ChatTypeFilter('private')) # type: ignore
async def start(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id

    profile = await get_profile(tg_id)

    if profile:
        txt_bts = ['🎩 Профиль']

        if profile.member:
            txt_bts.append('💠 Клан')
        if not profile.member:
            txt_bts.append('🔎 Найти клан')
        if profile.admin_role.level_access > 0:
            txt_bts.append('👮 Админ панель')

        txt_bts.append('⚙️ Настройки')

        await message.answer(
            'Клавиатура успешно обновлена!',
            reply_markup=keyboard_fabric(tuple(txt_bts), 2, True))

    else:
        await state.set_state(RegisterUser.nickname)
        await message.answer_photo(photo=reg_icon, caption=text_reg)


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

@main_router.message(Command('help'))
async def show_help(message : Message):
    pass
