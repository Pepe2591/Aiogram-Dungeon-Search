from aiogram import Router

from tools.filters import IsMemberFilter, ChatTypeFilter


infc_member_router = Router()

infc_member_router.message.filter(
    IsMemberFilter(),
    ChatTypeFilter('private')
)