import sqlite3
import logging
from telegram import Bot
from constants import DATABASE_PATH

async def send_order_info_to_admin():
    """Отправляет информацию о заказе админботу."""

    bot_token = '7495955549:AAGG0PQNvFC-SN0PO4rx0WVi2HEeIM8mnVg'  # Токен админбота
    admin_chat_id = 542067858  # chat_id админбота

    # Создаем подключение к базе данных
    conn = sqlite3.connect(DATABASE_PATH)
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
            "SELECT order_id, user_id, session_number, user_name, selected_date, start_time, end_time, duration,"
            " people_count, selected_style, preferences, city, calculated_cost FROM orders WHERE user_id = ? "
            "AND status = 2 ORDER BY session_number DESC LIMIT 1",
            (user_id,)
        )
        order_info = cursor.fetchone()

        if order_info is None:
            logging.error(f"No recent orders with status 2 found for user_id {user_id}.")
            return

        # Шаг 3: Формируем сообщение для отправки админботу
        admin_message = (
            f"я получил сообщение от PicnicsAlicanteBot\n"
            f"про бронирование нового ивента:\n"
            f"ПРОФОРМА № {order_info[1]}_{order_info[2]}_3\n"
            f"Дата мероприятия: {order_info[4]}\n"
            f"Время: {order_info[5]} - {order_info[6]}\n"
            f"Количество персон: {order_info[8]}\n"
            f"Стиль мероприятия: {order_info[9]}\n"
            f"Город: {order_info[11]}\n"
            f"Сумма к оплате: {float(order_info[12]) - 20} евро\n"
            
            "\n1. Я отправляю заказчику информационное подтверждение на его языке\n"
            "2. Я отправляю Администратору Ирине текст полной заявки на новый ивент с переводом на русский"


           # "\n1. Если место ивента более чем в 15 км за Аликанте, дополнительная плата за доставку реквизита 0,5 евро за км.\n"

            #"2. Всю дополнительную информацию можете узнать по вотсапу: 1234556 - Ирина."
        )

        # Отправляем сообщение админботу
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=admin_chat_id, text=admin_message)

        logging.info(f"Message sent to admin bot {admin_chat_id}.")

        # Шаг 4: Обновляем значение number_of_events и сбрасываем статус

        new_number_of_events = number_of_events + 1

        cursor.execute("UPDATE users SET number_of_events = ?, status = NULL WHERE user_id = ?",
                       (new_number_of_events, user_id))
        conn.commit()

        logging.info(f"User number_of_events updated to {new_number_of_events} for user_id {user_id}.")

    except Exception as e:
        logging.error(f"Failed to send order info to admin bot: {e}")
        print(f"Принт: Ошибка при отправке сообщения: {e}")

    finally:
        conn.close()
