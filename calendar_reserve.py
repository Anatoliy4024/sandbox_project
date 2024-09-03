
import sqlite3
import logging
from constants import DATABASE_PATH
from datetime import datetime


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




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



def check_date_reserved(cur_date, order_list):
    date_str = cur_date.strftime("%Y-%m-%d")
    number_of_orders = order_list.count((date_str,))

    if number_of_orders > 1:
        logging.info(f"Дата {cur_date.date()} зарезервирована.")
        return True
    else:
        logging.info(f"Дата {cur_date.date()} не зарезервирована.")
        return False

def reserved_month(current_date):
    logging.info(f"Функция reserved_date вызвана для даты: {current_date}")

    # Создаем подключение к базе данных
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        logging.info("Соединение с базой данных успешно установлено.")
    except Exception as e:
        logging.error(f"Не удалось подключиться к базе данных: {e}")
        return False

    cursor = conn.cursor()
    first_day_month = datetime(current_date.year, current_date.month, 1)
    first_day_next_month = datetime(current_date.year, current_date.month + 1, 1)
    try:
        # Проверяем запрос и данные
        logging.info(f"Выполнение SQL-запроса для даты {current_date.date()}")
        cursor.execute("SELECT selected_date FROM orders WHERE status > 2 AND selected_date BETWEEN ? AND ?",
                       (first_day_month, first_day_next_month))

        # Получаем результат
        user_info = cursor.fetchall()
        logging.info(f"Результат запроса: {user_info}")
        if user_info is None:
            logging.warning("Нет записей в orders для указанной даты.")
            return None

        else:
            return user_info

    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        return False

    finally:
        conn.close()
        logging.info("Соединение с базой данных закрыто.")

# date_list = reserved_month(datetime(2024,9,13,))
# print(date_list)
# print(check_date_reserved(datetime(2024,9,15,), date_list))



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