import asyncio
from telegram import Bot

async def send_message():
    # Вставьте сюда токен вашего бота
    bot_token = '7495955549:AAGG0PQNvFC-SN0PO4rx0WVi2HEeIM8mnVg'

    # Вставьте сюда chat_id пользователя, которому хотите отправить сообщение
    chat_id = 542067858  # Замените на нужный user_id

    # Сообщение, которое хотите отправить
    message_text = "Привет! Это тестовое сообщение."

    # Создаем объект бота и отправляем сообщение
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message_text)

    print("Сообщение отправлено!")

# Запуск асинхронной функции
asyncio.run(send_message())
