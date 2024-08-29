import sqlite3
import logging
from datetime import datetime, timedelta
from constants import DATABASE_PATH

def get_events_on_date(date):
    """
    Возвращает все ивенты на указанную дату, включая время начала и окончания.
    """
    logging.info(f"Функция get_events_on_date вызвана для даты: {date}")

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        logging.info("Соединение с базой данных успешно установлено.")
    except Exception as e:
        logging.error(f"Не удалось подключиться к базе данных: {e}")
        return []

    cursor = conn.cursor()

    try:
        logging.info(f"Выполнение SQL-запроса для даты {date}")
        cursor.execute("SELECT start_time, end_time FROM orders WHERE selected_date = ?", (date,))

        events = cursor.fetchall()
        logging.info(f"Найдено {len(events)} ивентов на дату {date}: {events}")
        return events

    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        return []

    finally:
        conn.close()
        logging.info("Соединение с базой данных закрыто.")
