from aiogram import Router, F
from aiogram.types import Message

from tools.filters import ChatTypeFilter

group_admin_router = Router()

group_admin_router.message.filter(
    ChatTypeFilter(['group', 'supergroup', 'channel']) # type: ignore
)

@group_admin_router.message(F.text.lower() == 'show_json')
async def get_msg_data(message: Message):
 
    target_msg = message.reply_to_message or message

    json_data = target_msg.model_dump_json(indent=2, exclude_none=True)

    if len(json_data) > 4000:
        from aiogram.types import BufferedInputFile
        file = BufferedInputFile(json_data.encode('utf-8'), filename="message_data.json")
        await message.answer_document(file, caption="Вся информация о сообщении")
    else:
        await message.answer(f"<pre><code class=\"language-json\">{json_data}</code></pre>", parse_mode="HTML")