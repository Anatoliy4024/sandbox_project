import sqlite3

#DATABASE_PATH = 'user_sessions.db'  # Укажите путь к вашей базе данных
DATABASE_PATH = 'sqlite.db'  # Укажите путь к вашей базе данных

def fetch_all_users():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
 #   cursor.execute("SELECT * FROM user_sessions")
    cursor.execute("SELECT * FROM users")
 #   cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == '__main__':
    fetch_all_users()
