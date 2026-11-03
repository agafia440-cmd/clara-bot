import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from google import genai

# ==================== СВОИ КЛЮЧИ ВСТАВЛЯТЬ СЮДА ====================
TELEGRAM_BOT_TOKEN = "ТОКЕН_БОТА"
GEMINI_API_KEY = "ТВОЙ_КЛЮЧ"
# ===================================================================

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
            model="gemini-2.5-flash",  # Быстрая и бесплатная модель для текста
            contents=post_text,
            config={
                "system_instruction": CLARA_SYSTEM_PROMPT,
                "max_output_tokens": 150,  # Ограничение по длине, чтобы Клара говорила кратко
                "temperature": 0.9,       # Добавляем немного творческого безумия и сарказма
            }
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка при запросе к Gemini: {e}")
        return "У меня тут короткое замыкание в процессоре от вашей тупости. Попробуйте позже."

# Ловим сообщения, где есть хэштег #к, слово "клара" (в любом регистре) ИЛИ ответ на сообщение бота
@dp.message(F.text & (
    F.text.regexp(r"(?i)\bклара\b") | 
    F.text.contains("#к") | 
    F.text.contains("#К")
))
async def handle_roleplay_post(message: Message):
    # Игнорируем сообщения от самого бота, чтобы он не отвечал сам себе
    if message.from_user.is_bot:
        return
    
    # Отправляем текст поста игрока Кларе на растерзание
    post_text = message.text
    
    # Печатаем в консоль для отладки
    print(f"Поймали пост от {message.from_user.full_name}: {post_text[:30]}...")

    # Генерируем ответ через ИИ (делаем это в фоновом режиме, чтобы бот не зависал)
    loop = asyncio.get_running_loop()
    clara_reply = await loop.run_in_executor(None, ask_clara, post_text)

    # Отвечаем в чате ролевой репликой от Клары (используем reply, чтобы привязать к посту игрока)
    await message.reply(clara_reply)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот C.L.A.R.A. запущен и следит за порядком в Коробке...")
    # Запускаем поллинг (опрос серверов Телеграма)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
