import sqlite3
import time
from database_logger import log_message, log_query
from constants import DATABASE_PATH
from constants import UserData

def create_connection(db_file):
    """Создает соединение с базой данных SQLite, указанной в db_file."""
    try:
        conn = sqlite3.connect(db_file)
        log_message(f"Database connected: {db_file}")
        return conn
    except sqlite3.Error as e:
        log_message(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query, params=()):
    """Выполняет SQL-запрос."""
    if conn is None:
        log_message("No database connection available")
        return False

    try:
        c = conn.cursor()
        log_query(query, params)  # Логирование запроса
        c.execute(query, params)
        conn.commit()
        log_message(f"Query executed successfully: {query} with params {params}")
        return True
    except sqlite3.Error as e:
        log_message(f"Error executing query: {e}")
        return False
    finally:
        try:
            conn.close()  # Закрытие соединения
            log_message("Database connection closed")
        except sqlite3.Error as e:
            log_message(f"Error closing database connection: {e}")


def execute_query_with_retry(query, params=(), user_data=None, max_retries=5):
    """Выполняет SQL-запрос с повторными попытками при блокировке базы данных."""
    retries = 0
    conn = None

    while retries < max_retries:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            if conn is None:
                log_message("Failed to create database connection")
                return False

            cursor = conn.cursor()
            log_query(query, params)  # Логирование запроса
            cursor.execute(query, params)
            conn.commit()
            log_message(f"Query executed successfully with retry: {query} with params {params}")

            # Использования user_data после успешного выполнения запроса
            if user_data:
                user_data.set_step('data_saved')  # Или другое обновление данных

            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries += 1
                log_message(f"Database is locked, retrying {retries}/{max_retries}")
                time.sleep(1)  # Задержка перед повторной попыткой
            else:
                log_message(f"Error executing query with retry: {e}")
                return False
        finally:
            if conn:
                try:
                    conn.close()
                    log_message("Database connection closed after retry")
                except sqlite3.Error as e:
                    log_message(f"Error closing database connection after retry: {e}")
