
import sqlite3
import logging
from constants import DATABASE_PATH
from datetime import datetime, timedelta, time


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

def create_reserved_datelist (date_list):
    reserved_date_list = list()
    date_for_checklist = list()

    for date in date_list:
        date_for_checklist.append(date[0])

    for i in date_list:
        if date_for_checklist.count(i[0]) > 1:
            reserved_date_list.append(i[0])
            continue

        if i[1] is None or i[2] is None:
            continue

        start = datetime.strptime(i[1], "%H:%M")
        start_with_5 = start - timedelta(hours=5)
        end_with_5 = datetime.strptime(i[2], "%H:%M") + timedelta(hours=5)

        start_dif = start_with_5 - datetime(start.year, start.month, start.day, 8, 0)
        start_dif_int = start_dif.total_seconds()//3600
        end_dif = datetime(start.year, start.month, start.day, 22, 0) - end_with_5
        end_dif_int = end_dif.total_seconds()//3600

        if start_dif_int < 2 and end_dif_int < 2:
            reserved_date_list.append(i[0])

    return set(reserved_date_list)


def check_date_reserved(cur_date, order_list):
    reserved_list = list(create_reserved_datelist(order_list))

    date_str = cur_date.strftime("%Y-%m-%d")
    if date_str in reserved_list:
        return True

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
        cursor.execute("SELECT selected_date, start_time, end_time FROM orders WHERE status > 2 AND selected_date BETWEEN ? AND ?",
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

# date_list = reserved_month(datetime(2024,9,6,))
# print(date_list)
# print(create_reserved_datelist(date_list))
# # print(check_date_reserved(datetime(2024,9,6,), date_list))


