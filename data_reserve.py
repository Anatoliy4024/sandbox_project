import sqlite3
import logging
from constants import DATABASE_PATH
from datetime import datetime, timedelta

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



# функция для проверки зарезервированного времени по данным БД
def test_reserved_time_extraction():
    # Задаем тестовые даты для выборки временных интервалов
    test_dates = [
        '2024-09-29',  # Дата с несколькими зарезервированными интервалами
        '2024-09-14',  # Дата без зарезервированных интервалов
        '2024-09-28'   # Дата с одним зарезервированным интервалом
    ]

    for test_date in test_dates:
        logging.info(f"Тестирование для даты: {test_date}")
        reserved_intervals = get_reserved_times_for_date(test_date)

        if reserved_intervals:
            logging.info(f"Зарезервированные интервалы для {test_date}: {reserved_intervals}")
        else:
            logging.info(f"Для даты {test_date} нет зарезервированных временных интервалов.")

# Вызов тестовой функции
if __name__ == '__main__':
    test_reserved_time_extraction()
