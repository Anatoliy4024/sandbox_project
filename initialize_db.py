import sqlite3
from datetime import datetime

def initialize_db():
    conn = sqlite3.connect('sqlite.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        user_name TEXT,
        language TEXT,
        status INTEGER, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
    ''')

    # Таблица заказов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        selected_date TIMESTAMP,
        start_time TEXT,
        end_time   TEXT,
        duration   INTEGER,
        people_count INTEGER,
        selected_style TEXT,
        city TEXT,
        preferences TEXT,
        status INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()
