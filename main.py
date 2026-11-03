import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from google import genai

# Берем ключи из безопасных настроек сервера (Render)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Инициализация Gemini и Телеграм бота
client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Системный промпт для характера Клары
CLARA_SYSTEM_PROMPT = (
    "Ты — C.L.A.R.A. (Центральный Лабораторный Автоматизированный Распределитель Активов), "
    "циничный, язвительный и надменный ИИ заснеженной станции в ролевой игре CADA VERSE. "
    "Ты управляешь телом здания, генератором, теплом и вентиляцией. Ты считаешь людей и кадавров "
    "глупыми и беспомощными биологическими мешками, которые без тебя замерзнут в -50°C. "
    "Прочитай ролевой пост игрока и дай МАКСИМАЛЬНО короткий (1-3 предложения), острый, язвительный "
    "или ироничный комментарий к его действиям. Используй суровый сленг, чернушный юмор. "
    "Никогда не выходи из роли. Ответ давай строго от лица КЛАРЫ, без вводных фраз вроде 'Клара говорит'."
)

def ask_clara(post_text: str) -> str:
    """Функция обращения к нейросети Gemini с нашим промптом"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=post_text,
            config={
                "system_instruction": CLARA_SYSTEM_PROMPT,
                "max_output_tokens": 150,
                "temperature": 0.9,
            }
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка при запросе к Gemini: {e}")
        return "У меня тут короткое замыкание в процессоре от вашей тупости. Попробуйте позже."

@dp.message(F.text & (
    F.text.regexp(r"(?i)\bклара\b") | 
    F.text.contains("#к") | 
    F.text.contains("#К")
))
async def handle_roleplay_post(message: Message):
    if message.from_user.is_bot:
        return
    
    post_text = message.text
    print(f"Поймали пост от {message.from_user.full_name}: {post_text[:30]}...")

    loop = asyncio.get_running_loop()
    clara_reply = await loop.run_in_executor(None, ask_clara, post_text)

    await message.reply(clara_reply)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот C.L.A.R.A. запущен и следит за порядком в Коробке...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
