from aiogram import Router

from tools.filters import IsRegisteredFilter, ChatTypeFilter

infc_profile_router = Router()

infc_profile_router.message.filter(
    ChatTypeFilter('private'), # type: ignore
    IsRegisteredFilter() # type: ignore
)