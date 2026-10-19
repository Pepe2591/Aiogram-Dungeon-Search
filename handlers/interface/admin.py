from aiogram import Router

from tools.filters import ChatTypeFilter

infc_admin_router = Router()

infc_admin_router.message.filter(
    ChatTypeFilter('private') # type: ignore
)