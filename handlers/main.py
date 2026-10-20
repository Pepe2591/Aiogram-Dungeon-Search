from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.requests import profile_is_exist

main_router = Router()

@main_router.message(CommandStart()) # type: ignore
async def start(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    print('RESULT::', await profile_is_exist(tg_id))

    if await profile_is_exist(tg_id):
        print('Ты зареган')

    print('Ты не зареган')


