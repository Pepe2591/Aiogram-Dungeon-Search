from html import escape

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from tools.filters import ChatTypeFilter, IsAdminAccessFilter

group_admin_router = Router()

group_admin_router.message.filter(
    ChatTypeFilter(['group', 'supergroup', 'channel'])
)


@group_admin_router.message(F.content_type == 'photo', IsAdminAccessFilter(3))
async def get_photo(message: Message):
    if message.caption == "get_id_picture":
        id_photo = message.photo[-1].file_id
        await message.reply(f"<b>{{🖼️}} id фотографии:</b> {id_photo}")


@group_admin_router.message(Command("id"), IsAdminAccessFilter(3))
async def get_id(message: Message):
    thread_id = "отсутствует" if message.message_thread_id is None else message.message_thread_id
    text = "@{0} \n[🔨] id пользователя: {1}\n[👥] id группы: {2}\n[👑] id темы: {3}"

    if message.reply_to_message is None:
        user = message.from_user
    elif message.reply_to_message.forward_origin:
        await message.answer(
            "⚠️ Ошибка: Данные пользователя не найдены. "
            "Пожалуйста, используйте команду, отвечая на конкретное сообщение."
        )
        return
    else:
        user = message.reply_to_message.from_user

    await message.answer(
        text.format(user.username or "без username", user.id, message.chat.id, thread_id)
    )


@group_admin_router.message(F.text.lower() == 'show_json', IsAdminAccessFilter(2))
async def get_msg_data(message: Message):
    target_msg = message.reply_to_message or message

    json_data = target_msg.model_dump_json(indent=2, exclude_none=True)

    if len(json_data) > 4000:
        file = BufferedInputFile(json_data.encode('utf-8'), filename="message_data.json")
        await message.answer_document(file, caption="Вся информация о сообщении")
    else:
        await message.answer(f"<pre><code class=\"language-json\">{escape(json_data)}</code></pre>")