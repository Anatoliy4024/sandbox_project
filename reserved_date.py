# reserved_date.py

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


def is_slot_available(date, new_start_time, new_end_time):
    """
    Проверяет, доступен ли временной слот для нового события, учитывая 6-часовой зазор.
    """
    events = get_events_on_date(date)

    new_start = datetime.strptime(new_start_time, '%H:%M')
    new_end = datetime.strptime(new_end_time, '%H:%M')

    print(f"Новый слот: {new_start.time()} - {new_end.time()}")

    for event in events:
        if event[0] and event[1]:  # Проверка, что времена начала и конца события не пусты
            existing_start = datetime.strptime(event[0], '%H:%M')
            existing_end = datetime.strptime(event[1], '%H:%M')

            print(f"Проверка существующего события: {existing_start.time()} - {existing_end.time()}")

            # Проверка 6-часового зазора
            if not (new_end <= existing_start - timedelta(hours=5) or new_start >= existing_end + timedelta(hours=5)):
                print(f"Слот недоступен из-за пересечения с событием: {existing_start.time()} - {existing_end.time()}")
                return False

    print("Слот доступен")
    return True
