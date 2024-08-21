import sqlite3
import logging
from telegram import Bot
import asyncio

# Настройка токена и ID администратора
admin_bot_token = '7495955549:AAGG0PQNvFC-SN0PO4rx0WVi2HEeIM8mnVg'
admin_chat_id = 542067858  # это id AdminPicnicsAlicante (https://t.me/AssistPicnicsBot)

# Логирование для отслеживания работы
logging.basicConfig(level=logging.INFO)

async def send_message_to_user():
    """Отправляет информацию о заказе пользователю и администратору Ирины."""
    # Подключение к базе данных
    conn = sqlite3.connect('path_to_your_database.db')  # замените на реальный путь к вашей базе данных
    cursor = conn.cursor()

    try:
        # Шаг 1: Вытаскиваем user_id из таблицы users, где статус равен 3
        cursor.execute("SELECT user_id FROM users WHERE status = 3")
        user_info = cursor.fetchone()

        if user_info is None:
            logging.error("No users with status 3 found.")
            return

        user_id = user_info[0]  # user_id из таблицы users

        # Шаг 2: Проверяем последний заказ пользователя в таблице orders на наличие статуса 2
        cursor.execute(
            "SELECT order_id, user_id, session_number, user_name, selected_date, start_time, end_time, duration, people_count, selected_style, preferences, city, calculated_cost FROM orders WHERE user_id = ? AND status = 2 ORDER BY session_number DESC LIMIT 1",
            (user_id,)
        )
        order_info = cursor.fetchone()

        if order_info is None:
            logging.error(f"No recent orders with status 2 found for user_id {user_id}.")
            return

        # Формирование сообщения для отправки пользователю
        user_message = (
            f"Привет, {order_info[3]}!\n"
            f"Благодарим за бронирование ивента.\n"
            f"ПРОФОРМА № {order_info[0]}_{order_info[2]}_3\n"
            f"Дата мероприятия: {order_info[4]}\n"
            f"Время: {order_info[5]} - {order_info[6]}\n"
            f"Количество персон: {order_info[8]}\n"
            f"Стиль мероприятия: {order_info[9]}\n"
            f"Город: {order_info[11]}\n"
            f"Сумма к оплате: {float(order_info[12]) - 20} евро\n"
            "\n1. Если место ивента более чем в 15 км за Аликанте, дополнительная плата за доставку реквизита 0,5 евро за км.\n"
            "2. Всю дополнительную информацию можете узнать по вотсапу: 1234556 - Ирина."
        )

        # Отправка сообщения пользователю
        await send_message_to_user_by_id(user_id, user_message, admin_bot_token)

        # Формирование сообщения для администратора Ирины
        irina_message = (
            f"Привет, Ирина.\n"
            f"Я AdminPicnicAlicante. Подтвержденный заказ от {order_info[3]} на ивент с параметрами:\n"
            f"ПРОФОРМА № {order_info[0]}_{order_info[2]}_3\n"
            f"Дата мероприятия: {order_info[4]}\n"
            f"Время: {order_info[5]} - {order_info[6]}\n"
            f"Количество персон: {order_info[8]}\n"
            f"Стиль мероприятия: {order_info[9]}\n"
            f"Город: {order_info[11]}\n"
            f"Сумма к оплате: {float(order_info[12]) - 20} евро\n"
            "\nПожалуйста, свяжитесь с клиентом для дальнейших действий."
        )

        # Отправка сообщения администратору Ирины
        await send_message_to_user_by_id(admin_chat_id, irina_message, admin_bot_token)

        # Обновляем статус в таблице users на 3001, 3002 и т.д.
        cursor.execute("SELECT MAX(status) FROM users WHERE status >= 3001")
        max_status = cursor.fetchone()[0]

        if max_status is None:
            new_status = 3001
        else:
            new_status = max_status + 1

        cursor.execute("UPDATE users SET status = ? WHERE user_id = ?", (new_status, user_id))
        conn.commit()

        logging.info(f"User status updated to {new_status} for user_id {user_id}.")

    except Exception as e:
        logging.error(f"Failed to send order info to user or admin: {e}")

    finally:
        conn.close()

async def send_message_to_user_by_id(chat_id, message, bot_token):
    """Функция для отправки сообщения по chat_id"""
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

# Пример вызова функции (если файл запускается напрямую)
if __name__ == "__main__":
    asyncio.run(send_message_to_user())
