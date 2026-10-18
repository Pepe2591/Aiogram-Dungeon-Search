from aiogram import Router

from tools.filters import IsRegisteredFilter, ChatTypeFilter

group_profile_router = Router()

group_profile_router.message.filter(
    ChatTypeFilter(['group', 'supergroup', 'channel']),
    IsRegisteredFilter()
)