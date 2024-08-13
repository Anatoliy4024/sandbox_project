import sqlite3

# Открываем соединение с базой данных
conn = sqlite3.connect('sqlite.db')

# Создаем курсор
cursor = conn.cursor()

# Выполняем команду PRAGMA для получения информации о таблице
cursor.execute("PRAGMA table_info(users);")
cursor.execute("PRAGMA table_info(orders);")

# Получаем и выводим результаты
columns = cursor.fetchall()
for column in columns:
    print(column)

# Закрываем соединение
conn.close()
