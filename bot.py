from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import config
import os

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)

# Ключ -> путь к файлу
files = {
    "video1": "files/video1.mp4",
    "book": "files/book.pdf"
}

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    param = message.get_args()  # Получаем deep link параметр
    if not param:
        await message.answer("Привет! Чтобы получить файл, используй специальную ссылку.")
        return

    # Проверка подписки
    member = await bot.get_chat_member(config.CHANNEL_ID, message.from_user.id)
    if member.status in ("member", "administrator", "creator"):
        file_path = files.get(param)
        if file_path and os.path.exists(file_path):
            await message.answer_document(open(file_path, "rb"))
        else:
            await message.answer("Файл не найден.")
    else:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Подписаться", url=config.CHANNEL_LINK),
            InlineKeyboardButton("✅ Проверить подписку", callback_data=f"check_{param}")
        )
        await message.answer("Сначала подпишись на канал, потом нажми 'Проверить подписку'.", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def check_subscription(callback: types.CallbackQuery):
    param = callback.data.split("_", 1)[1]
    member = await bot.get_chat_member(config.CHANNEL_ID, callback.from_user.id)
    if member.status in ("member", "administrator", "creator"):
        file_path = files.get(param)
        if file_path and os.path.exists(file_path):
            await bot.send_document(callback.from_user.id, open(file_path, "rb"))
        else:
            await callback.message.answer("Файл не найден.")
    else:
        await callback.answer("❌ Ты всё ещё не подписан!", show_alert=True)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
