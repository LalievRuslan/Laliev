import os
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv
import json

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настройка бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

openai.api_key = OPENAI_API_KEY

# Файл для хранения истории
history_file = "conversation_history.json"

# Функции для загрузки и сохранения истории


def load_history():
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            return json.load(f)
    return {}


def save_history(history):
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)


conversation_history = load_history()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я GPT-бот. Задай мне любой вопрос.")


@dp.message_handler()
async def echo_message(message: types.Message):
    try:
        user_id = message.from_user.id
        user_message = message.text

        # Создание истории для пользователя, если её нет
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Добавление сообщения пользователя в историю
        conversation_history[user_id].append(f"User: {user_message}")

        # Создание запроса для OpenAI
        prompt = "\n".join(conversation_history[user_id]) + "\nAI:"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        ai_reply = response.choices[0].message['content'].strip()

        # Добавление ответа от AI в историю и отправка ответа пользователю
        conversation_history[user_id].append(f"AI: {ai_reply}")
        await message.reply(ai_reply)
        save_history(conversation_history)
    except Exception as e:
        await message.reply("Произошла ошибка при обработке вашего сообщения.")
        print(f"Error: {e}")

if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
