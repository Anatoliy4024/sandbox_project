
import sqlite3
import logging
from constants import DATABASE_PATH
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import sqlite3
import logging
from constants import DATABASE_PATH


def reserved_date(current_date):
    logging.info(f"Функция reserved_date вызвана для даты: {current_date}")

    # Создаем подключение к базе данных
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        logging.info("Соединение с базой данных успешно установлено.")
    except Exception as e:
        logging.error(f"Не удалось подключиться к базе данных: {e}")
        return False

    cursor = conn.cursor()

    try:
        # Проверяем запрос и данные
        logging.info(f"Выполнение SQL-запроса для даты {current_date.date()}")
        cursor.execute("SELECT COUNT(order_id) FROM orders WHERE status > 2 AND selected_date = ?",
                       (current_date.date(),))

        # Получаем результат
        user_info = cursor.fetchone()
        logging.info(f"Результат запроса: {user_info}")

        if user_info is None:
            logging.warning("Нет записей в orders для указанной даты.")
            return False

        number_of_orders = user_info[0]
        logging.info(f"Количество заказов для даты {current_date.date()}: {number_of_orders}")

        if number_of_orders > 1:
            logging.info(f"Дата {current_date.date()} зарезервирована.")
            return True
        else:
            logging.info(f"Дата {current_date.date()} не зарезервирована.")
            return False

    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        return False

    finally:
        conn.close()
        logging.info("Соединение с базой данных закрыто.")


    # это кусок кода утра 29_08_2024

    # def reserved_date(current_date):
#     # Создаем подключение к базе данных
#     conn = sqlite3.connect(DATABASE_PATH)
#     cursor = conn.cursor()
#
#     try:
#         # Шаг 1: Вытаскиваем user_id из таблицы users, где статус равен 3
#         cursor.execute("SELECT COUNT(user_id) FROM orders WHERE status > 2 AND selected_date = ?", (current_date.date()))
#         user_info = cursor.fetchone()
#
#         if user_info is None:
#             logging.error("No orders with status 3 found.")
#             return
#
#         print(user_info)
#
#         number_of_orders = user_info[0]  # user_id из таблицы users
#         if number_of_orders > 1:
#             return True
#
#     except Exception as e:
#         logging.error(f"Failed to send order info to admin bot or user: {e}")
#         print(f"Принт: Ошибка при отправке сообщения: {e}")
#
#     finally:
#         conn.close()
#
#     return False