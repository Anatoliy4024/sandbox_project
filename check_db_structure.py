import sqlite3

def check_db_structure():
    conn = sqlite3.connect('user_sessions.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(user_sessions)")
    columns = cursor.fetchall()

    for column in columns:
        print(column)

    conn.close()

if __name__ == '__main__':
    check_db_structure()
