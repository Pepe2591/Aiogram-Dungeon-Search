from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram.fsm.state import State, StatesGroup

from database.requests import get_profile, get_member, create_user, create_profile

from tools.filters import ChatTypeFilter

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
        if profile.admin_rank > 0:
            txt_bts.append('👮 Админ панель')

        txt_bts.append('⚙️ Настройки')

        await message.answer(
            'Клавиатура успешно обновлена!',
            reply_markup=keyboard_fabric(tuple(txt_bts), 2, True))

    else:
        await state.set_state(RegisterUser.nickname)
        await message.answer(text_reg)


@main_router.message(RegisterUser.nickname)
async def reg_nickname(message: Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer('Ваше имя должно быть меньше 30 символов!')
        await state.set_state(RegisterUser.nickname)


    await create_user(message)
    await create_profile(message.from_user.id, message.text, 0)
    await state.clear()
    await message.answer(
        'Вы успешно зарегистрировались!',
        reply_markup=keyboard_fabric(
            ('🎩 Профиль', '🔎 Найти клан', '⚙️ Настройки'),
            2,
            True
        )
    )




#Если профиля нет, мы будем устраивать регистрацию
#А какую клавиатуру вставлять будем проверять через get_member
#Если он уже участник клана то у него будет клавиатура с заявками в другие кланы
#В противном случае будет просто раздел клан
#Остальные кнопки можно придумать

