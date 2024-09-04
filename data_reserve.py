import sqlite3
import logging
from constants import DATABASE_PATH
from datetime import datetime, timedelta, time

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reserved_time_intervals(selected_date):
    logging.info(f"Функция reserved_time_intervals вызвана для даты: {selected_date}")

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        logging.info("Соединение с базой данных успешно установлено.")
    except Exception as e:
        logging.error(f"Не удалось подключиться к базе данных: {e}")
        return []

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT start_time, end_time 
            FROM orders 
            WHERE status > 2 AND selected_date = ?
        """, (selected_date,))

        reserved_times = cursor.fetchall()
        logging.info(f"Зарезервированные интервалы: {reserved_times}")

        if not reserved_times:
            logging.warning("Нет зарезервированных интервалов для указанной даты.")
            return []

        return reserved_times

    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        return []

    finally:
        conn.close()
        logging.info("Соединение с базой данных закрыто.")


# def check_time_reserved(start_time, end_time, reserved_time_intervals):
#     """
#     Проверяет, пересекается ли временной интервал с уже зарезервированными временными интервалами.
#     """
#
#     # Преобразование времени в datetime объекты для сравнения
#     start_time_dt = datetime.strptime(start_time, "%H:%M").time()
#     end_time_dt = datetime.strptime(end_time, "%H:%M").time()
#
#     for reserved_start, reserved_end in reserved_time_intervals:
#         reserved_start_dt = datetime.strptime(reserved_start, "%H:%M").time()
#         reserved_end_dt = datetime.strptime(reserved_end, "%H:%M").time()
#
#         # Проверка на пересечение интервалов
#         if start_time_dt < reserved_end_dt and end_time_dt > reserved_start_dt:
#             logging.info(
#                 f"Время с {start_time} до {end_time} пересекается с {reserved_start} до {reserved_end}.")
#             return True
#
#     logging.info(f"Время с {start_time} до {end_time} не пересекается с зарезервированными интервалами.")
#     print(f"Время с {start_time} до {end_time} не пересекается с зарезервированными интервалами.")
#     return False


def check_time_reserved(cur_time, reserved_time_intervals):
    """
    Проверяет, пересекается ли временной интервал с уже зарезервированными временными интервалами.
    """
    timelist = create_reserved_timelist(reserved_time_intervals)

    if cur_time in timelist:
        return True
    return False


def get_reserved_times_for_date(selected_date):
    logging.info(f"Функция get_reserved_times_for_date вызвана для даты: {selected_date}")

    # Получаем все зарезервированные временные интервалы для указанной даты
    reserved_intervals = reserved_time_intervals(selected_date)
    print(reserved_intervals)
    if not reserved_intervals:
        logging.info(f"Для даты {selected_date} нет зарезервированных временных интервалов.")
    return reserved_intervals

import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_reserved_timelist (time_list):
    reserved_time_list = list()

    for i in time_list:
        start = datetime.strptime(i[0], "%H:%M") - timedelta(hours=5)
        end = datetime.strptime(i[1], "%H:%M") + timedelta(hours=5, minutes=30)
        while start < end:
            if start.time() > time(7, 30) and start.time() < time(22, 30):


                 reserved_time_list.append(start.strftime('%H:%M'))
            start += timedelta(minutes=30)
    return reserved_time_list



#
#
# # функция для проверки зарезервированного времени по данным БД
# def test_reserved_time_extraction():
#     # Задаем тестовые даты для выборки временных интервалов
#     test_dates = [
#         '2024-09-29',  # Дата с несколькими зарезервированными интервалами
#         '2024-09-14',  # Дата без зарезервированных интервалов
#         '2024-09-30'   # Дата с одним зарезервированным интервалом
#     ]
#
#     for test_date in test_dates:
#         logging.info(f"Тестирование для даты: {test_date}")
#         reserved_intervals = get_reserved_times_for_date(test_date)
#
#         if reserved_intervals:
#             logging.info(f"Зарезервированные интервалы для {test_date}: {reserved_intervals}")
#         else:
#             logging.info(f"Для даты {test_date} нет зарезервированных временных интервалов.")
#
# # Вызов тестовой функции
# if __name__ == '__main__':
#     test_reserved_time_extraction()

# date_list = reserved_time_intervals(datetime(2024,9,29,).date())
# print(date_list)
# print(create_reserved_timelist(date_list))

