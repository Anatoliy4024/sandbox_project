import sqlite3
from datetime import datetime

def initialize_db():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    # Таблица пользователей (без user_name и language)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        status INTEGER, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
    ''')

    # Таблица заказов (добавлены user_name, session_number и language)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_number INTEGER,  -- Добавлено поле для хранения номера сессии
        user_name TEXT,  -- Добавлено поле для хранения имени пользователя
        language TEXT,  -- Добавлено поле для хранения языка
        selected_date TIMESTAMP,
        start_time TEXT,
        end_time   TEXT,
        duration   INTEGER,
        people_count INTEGER,
        selected_style TEXT,
        preferences TEXT,
        city TEXT,
        status INTEGER,
        calculated_cost INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()
