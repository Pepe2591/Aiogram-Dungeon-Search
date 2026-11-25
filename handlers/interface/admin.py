from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from tools.filters import ChatTypeFilter, IsAdminAccessFilter

from config import DEFAULT_ROLES
from database.requests import get_profile, get_all_user
from database.models import async_session, Clan, Profile, User, Role, Member

infc_admin_router = Router()

infc_admin_router.message.filter(
    ChatTypeFilter('private'),  # type: ignore
    IsAdminAccessFilter(3)  # type: ignore
)
infc_admin_router.callback_query.filter(
    IsAdminAccessFilter(3)  # type: ignore
)

CLAN_NAME_MAX_LEN = 30


class RegisterClan(StatesGroup):
    name = State()


@infc_admin_router.message(F.text == '👮 Админ панель')
async def show_kb(message: Message):
    user = await get_all_user(message.from_user.id)
    profile = user.profile
    lvl = int(profile.admin_role.level_access)
    kb_builder = InlineKeyboardBuilder()

    if lvl <= 3:
        kb_builder.add(InlineKeyboardButton(text='Создать клан', callback_data='create_clan'))

    await message.answer('Панель администратора', reply_markup=kb_builder.adjust(2).as_markup())


@infc_admin_router.callback_query(F.data == 'create_clan')
async def create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        f'Введите имя клана, который вы хотите создать (до {CLAN_NAME_MAX_LEN} символов)'
    )
    await state.set_state(RegisterClan.name)


@infc_admin_router.message(RegisterClan.name, F.text)
async def get_clan_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if not name or len(name) > CLAN_NAME_MAX_LEN:
        await message.answer(
            f'Название должно быть от 1 до {CLAN_NAME_MAX_LEN} символов. Попробуйте ещё раз:'
        )
        return

    async with async_session() as session:
        profile = await session.scalar(
            select(Profile)
            .join(User, Profile.user_fk == User.id)
            .where(User.tg_id == message.from_user.id)
            .options(selectinload(Profile.member))
        )

        if profile is None:
            await state.clear()
            await message.answer('Профиль не найден. Сначала пройдите регистрацию.')
            return

        if profile.member is not None:
            await state.clear()
            await message.answer('Вы уже состоите в клане, создать новый нельзя.')
            return

        name_taken = await session.scalar(
            select(Clan.id).where(func.lower(Clan.name) == name.lower())
        )
        if name_taken:
            await message.answer('Клан с таким названием уже существует. Введите другое:')
            return

        clan = Clan(name=name, description=None, owner_fk=profile.id)
        session.add(clan)
        await session.flush()

        roles = [
            Role(
                name=r['name'],
                description=r['description'],
                level_access=r['id'],
                clan_fk=clan.id,
            )
            for r in DEFAULT_ROLES
        ]
        session.add_all(roles)
        await session.flush()

        leader_role = next(r for r in roles if r.level_access == 1)

        session.add(Member(
            profile_fk=profile.id,
            clan_fk=clan.id,
            role_fk=leader_role.id,
        ))

        await session.commit()

    await state.clear()
    await message.answer(f'Клан «{name}» был успешно создан! Вы назначены Лидером 👑')


@infc_admin_router.message(RegisterClan.name)
async def get_clan_name_invalid(message: Message):
    await message.answer('Отправьте название клана текстом.')