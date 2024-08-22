import sqlite3
import logging
from telegram import Bot
from constants import DATABASE_PATH, ORDER_STATUS


async def send_order_info_to_admin(user_id, session_num):
    """Отправляет информацию о заказе админботу."""

    bot_token = '7495955549:AAGG0PQNvFC-SN0PO4rx0WVi2HEeIM8mnVg'  # Токен админбота
    admin_chat_id = 542067858  # chat_id админбота

    # Создаем подключение к базе данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT order_id, user_id, session_number, user_name, selected_date, start_time, end_time, duration,"
            " people_count, selected_style, preferences, city, calculated_cost FROM orders WHERE user_id = ? "
            "AND status = 3 AND session_number = ?",
            (user_id, session_num,)
        )
        order_info = cursor.fetchone()

        if order_info is None:
            logging.error(f"No recent orders with status 3 found for user_id {user_id}.")
            return

        #  Формируем сообщение для отправки админботу
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
        )

        # Отправляем сообщение админботу
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=admin_chat_id, text=admin_message)

        logging.info(f"Message sent to admin bot {admin_chat_id}.")

        # Обновляем статус ордера

        cursor.execute("UPDATE orders SET status = ? WHERE user_id = ? AND session_number = ?",
                       (ORDER_STATUS["админ_бот получил соообщение"], user_id, session_num))
        conn.commit()

        logging.info(f"User !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!number_of_events updated to  and status set to NULL for user_id {user_id}.")

    except Exception as e:
        logging.error(f"Failed to send order info to admin bot: {e}")
        print(f"Принт: Ошибка при отправке сообщения: {e}")


        conn.close()
