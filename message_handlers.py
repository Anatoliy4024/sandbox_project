from telegram import Update
from telegram.ext import ContextTypes
from keyboards import yes_no_keyboard, generate_calendar_keyboard, generate_time_selection_keyboard, generate_person_selection_keyboard, generate_party_styles_keyboard
from constants import UserData
import logging
from datetime import datetime


from abstract_functions import create_connection, execute_query, execute_query_with_retry
from constants import TemporaryData, DATABASE_PATH


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data
    step = user_data.get_step()

    if step == 'greeting':
        await handle_name(update, context)
    elif step == 'preferences_request':
        await handle_preferences(update, context)
    elif step == 'city_request':
        await handle_city(update, context)
    else:
        await update.message.reply_text(
            get_translation(user_data, 'buttons_only'),  # Используем функцию для получения перевода
            reply_markup=get_current_step_keyboard(step, user_data)
        )

from telegram import Update
from telegram.ext import ContextTypes
from keyboards import yes_no_keyboard, generate_calendar_keyboard, generate_time_selection_keyboard, generate_person_selection_keyboard, generate_party_styles_keyboard
from constants import UserData
import logging

from abstract_functions import create_connection, execute_query, execute_query_with_retry
from constants import TemporaryData, DATABASE_PATH


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data
    step = user_data.get_step()

    if step == 'greeting':
        await handle_name(update, context)
    elif step == 'preferences_request':
        await handle_preferences(update, context)
    elif step == 'city_request':
        await handle_city(update, context)
    else:
        await update.message.reply_text(
            get_translation(user_data, 'buttons_only'),  # Используем функцию для получения перевода
            reply_markup=get_current_step_keyboard(step, user_data)
        )


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Инициализация данных пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    print("Принт 1: Начало функции handle_name")

    if update.callback_query:
        print("Принт 2: Обнаружен callback_query")
        user_data.set_name("Имя пользователя")
    else:
        print("Принт 3: Получено сообщение от пользователя")
        print(f"Принт 4: Значение из update.message.text: {update.message.text}")
        user_data.set_name(update.message.text)
        print(f"Принт 5: Имя пользователя, присвоенное в user_data: {user_data.get_name()}")

    print("Принт 6: После блока if update.callback_query")

    user_data.set_step('name_received')
    user_data.set_username(update.message.from_user.username if update.message else "Имя пользователя")

    print(f"Принт 7: Имя пользователя из update.message.text: {update.message.text}")

    language_code = user_data.get_language()
    print(f"Принт 8: Сохранение user_name: {user_data.get_name()} и username: {user_data.get_username()}")

    logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # Создайте соединение с базой данных
    conn = create_connection(DATABASE_PATH)
    if conn is not None:
        try:
            # Проверка существования пользователя
            logging.info(f"Проверка существования пользователя с user_id: {update.message.from_user.id}")
            select_query = "SELECT 1 FROM users WHERE user_id = ?"
            cursor = conn.cursor()
            cursor.execute(select_query, (update.message.from_user.id,))
            exists = cursor.fetchone()

            if exists:
                # Обновление имени пользователя в таблице orders
                logging.info(f"Обновление имени пользователя: {user_data.get_name()}")

                # Получаем session_number для обновления записи
                session_number_query = "SELECT MAX(session_number) FROM orders WHERE user_id = ?"
                cursor = conn.cursor()
                cursor.execute(session_number_query, (update.message.from_user.id,))
                session_number = cursor.fetchone()[0]

                if session_number is None:
                    logging.error("Не удалось получить session_number. Возможно, записи в базе данных отсутствуют.")
                else:
                    update_query = "UPDATE orders SET user_name = ? WHERE user_id = ? AND session_number = ?"
                    update_params = (user_data.get_name(), update.message.from_user.id, session_number)
                    execute_query_with_retry(conn, update_query, update_params)
            else:
                # Вставка нового пользователя в users
                logging.info(f"Вставка нового пользователя: {user_data.get_username()}")
                insert_query = "INSERT INTO users (user_id, username) VALUES (?, ?)"
                insert_params = (update.message.from_user.id, user_data.get_username())
                execute_query_with_retry(conn, insert_query, insert_params)

            # Теперь сохраняем user_id в таблицу orders
            save_user_id_to_orders(update.message.from_user.id)
            print(f"Принт 9: user_id {update.message.from_user.id} сохранен в таблицу orders")

        except Exception as e:
            logging.error(f"Ошибка базы данных: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных")

    greeting_texts = {
        'en': f'Hello {user_data.get_name()}! Do you want to see available dates?',
        'ru': f'Привет {user_data.get_name()}! Хочешь увидеть доступные даты?',
        'es': f'Hola {user_data.get_name()}! ¿Quieres ver las fechas disponibles?',
        'fr': f'Bonjour {user_data.get_name()}! Voulez-vous voir les dates disponibles?',
        'uk': f'Привіт {user_data.get_name()}! Хочеш подивитися які дати доступні?',
        'pl': f'Cześć {user_data.get_name()}! Chcesz zobaczyć dostępne daty?',
        'de': f'Hallo {user_data.get_name()}! Möchten Sie verfügbare Daten sehen?',
        'it': f'Ciao {user_data.get_name()}! Vuoi vedere le date disponibili?'
    }

    if update.message:
        print("Принт 12: Ответ пользователю с использованием update.message")
        await update.message.reply_text(
            greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
            reply_markup=yes_no_keyboard(language_code)
        )
    elif update.callback_query:
        print("Принт 13: Ответ пользователю с использованием update.callback_query")
        await update.callback_query.message.reply_text(
            greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
            reply_markup=yes_no_keyboard(language_code)
        )

    print("Принт 14: Конец функции handle_name")


import sqlite3
import logging
from constants import DATABASE_PATH


def create_connection(db_file):
    """Создает соединение с базой данных SQLite, указанной в db_file."""
    try:
        conn = sqlite3.connect(db_file)
        logging.info(f"Соединение с базой данных установлено: {db_file}")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None


def update_order_data(query, params, user_id):
    """Обновляет данные в таблице orders с проверками и обработкой ошибок."""
    conn = create_connection(DATABASE_PATH)

    if conn is not None:
        try:
            # Проверка существования записи для данного user_id
            check_query = "SELECT 1 FROM orders WHERE user_id = ?"
            cursor = conn.cursor()
            cursor.execute(check_query, (user_id,))
            exists = cursor.fetchone()

            if exists:
                logging.info(f"Запись для user_id {user_id} уже существует в таблице orders.")
            else:
                logging.info(f"Вставка нового user_id {user_id} в таблицу orders.")
                insert_query = """
                    INSERT INTO orders (user_id, selected_date, start_time, end_time, duration, people_count, selected_party_style, city, preferences, status)
                    VALUES (?, null, null, null, null, null, null, null, null, 1)
                """
                cursor.execute(insert_query, (user_id,))
                conn.commit()
                logging.info(f"user_id {user_id} успешно добавлен в таблицу orders с null для полей.")

            # Выполнение обновления данных
            logging.info(f"Выполнение запроса: {query} с параметрами {params}")
            cursor.execute(query, params)
            conn.commit()
            logging.info(f"Запрос успешно выполнен: {query} с параметрами {params}")

        except sqlite3.Error as e:
            logging.error(f"Ошибка базы данных при выполнении запроса: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных для выполнения запроса")


# Функция для обработки выбора даты
async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор даты пользователем и обновляет поле start_time в таблице orders."""
    user_id = update.callback_query.from_user.id
    selected_date = update.callback_query.data.split('_')[1]  # Извлекаем выбранную дату из callback_data

    update_order_data(user_id, selected_date, "UPDATE orders SET selected_date = ? WHERE user_id = ?")
    print(f"Дата {selected_date} обновлена в таблице orders для user_id {user_id}")

    await update.callback_query.message.reply_text(f"Вы выбрали дату: {selected_date}")


# def update_order_date(user_id, start_time):
#     """Обновляет дату в таблице orders для указанного user_id."""
#     conn = create_connection(DATABASE_PATH)
#     if conn is not None:
#         try:
#             logging.info(f"Обновление записи в orders для user_id: {user_id} с датой: {start_time}")
#             date_object = datetime.strptime(start_time, "%Y-%m-%d")
#             update_query = "UPDATE orders SET selected_date = ? WHERE user_id = ?"
#             execute_query_with_retry(conn, update_query, (date_object, user_id))
#             logging.info(f"Принт: Дата {start_time} успешно обновлена для user_id {user_id}")
#             logging.info(f"Дата {start_time} успешно обновлена для user_id {user_id}")
#             print(f"Принт: +++++++++++++++++++Дата {start_time} успешно обновлена для user_id {user_id}")
#         except Exception as e:
#             logging.error(f"Ошибка базы данных при обновлении даты в таблице orders: {e}")
#         finally:
#             conn.close()
#             logging.info("Соединение с базой данных закрыто")
#     else:
#         logging.error("Не удалось создать соединение с базой данных для работы с таблицей orders")

# def update_order_data(user_id, object, query):
#     """Обновляет дату в таблице orders для указанного user_id."""
#     conn = create_connection(DATABASE_PATH)
#     if conn is not None:
#         try:
#             logging.info(f"Обновление записи в orders для user_id: {user_id} с датой: {object}")
#             if isinstance(object,datetime):
#                 object = datetime.strptime(object, "%Y-%m-%d")
#             elif isinstance(object,int):
#                 object = object
#             execute_query_with_retry(conn, query, (object, user_id))
#             logging.info(f"Принт: Дата {object} успешно обновлена для user_id {user_id}")
#             logging.info(f"Дата {object} успешно обновлена для user_id {user_id}")
#             print(f"Принт: +++++++++++++++++++Дата {object} успешно обновлена для user_id {user_id}")
#         except Exception as e:
#             logging.error(f"Ошибка базы данных при обновлении даты в таблице orders: {e}")
#         finally:
#             conn.close()
#             logging.info("Соединение с базой данных закрыто")
#     else:
#         logging.error("Не удалось создать соединение с базой данных для работы с таблицей orders")
#
#
# # Словарь с переводами сообщения "Выбор только кнопками" на разные языки
# translations = {
#     'en': "Please use the buttons",
#     'ru': "Выбор только кнопками",
#     'es': "Por favor, usa los botones",
#     'fr': "Veuillez utiliser les boutons",
#     'de': "Bitte verwenden Sie die Tasten",
#     'it': "Si prega di utilizzare i pulsanti",
#     'uk': "Будь ласка, використовуйте кнопки",
#     'pl': "Proszę użyć przycisków"
# }

def get_translation(user_data, key):
    language_code = user_data.get_language()  # Получаем код языка пользователя
    return translations.get(language_code, translations['en'])  # Возвращаем перевод или английский по умолчанию



# Функция для обработки имени
async def handle__name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    user_data = context.user_data.get('user_data', UserData())
    user_data.set_name(update.message.text)
    user_data.set_step('name_received')
    context.user_data['user_data'] = user_data

    language_code = user_data.get_language()

    greeting_texts = {
        'en': f'Hello {user_data.get_name()}! Do you want to see available dates?',
        'ru': f'Привет {user_data.get_name()}! Хочешь увидеть доступные даты?',
        'es': f'¡Hola {user_data.get_name()}! ¿Quieres ver las fechas disponibles?',
        'fr': f'Bonjour {user_data.get_name()}! Voulez-vous voir les dates disponibles?',
        'uk': f'Привіт {user_data.get_name()}! Хочеш подивитися доступні дати?',
        'pl': f'Cześć {user_data.get_name()}! Chcesz zobaczyć dostępne daty?',
        'de': f'Hallo {user_data.get_name()}! Möchten Sie verfügbare Daten sehen?',
        'it': f'Ciao {user_data.get_name()}! Vuoi vedere le date disponibili?'
    }

    await update.message.reply_text(
        greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
        reply_markup=yes_no_keyboard(language_code)
    )


# Функция для обработки предпочтений
async def handle_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    user_data.set_preferences(update.message.text)
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    # Получаем session_number для обновления записи
    session_number_query = "SELECT MAX(session_number) FROM orders WHERE user_id = ?"
    conn = create_connection(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(session_number_query, (user_data.get_user_id(),))
    session_number = cursor.fetchone()[0]

    if session_number is None:
        logging.error("Не удалось получить session_number. Возможно, записи в базе данных отсутствуют.")
    else:
        logging.info(f"Используем session_number: {session_number} для обновления.")

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET preferences = ? WHERE user_id = ? AND session_number = ?",
            (update.message.text, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

    user_data.set_step('preferences_received')
    context.user_data['user_data'] = user_data

    language_code = user_data.get_language()

    city_request_texts = {
        'en': 'Please specify the city for the event.',
        'ru': 'Пожалуйста укажите город проведения ивента.',
        'es': 'Por favor, especifique la ciudad para el evento.',
        'fr': 'Veuillez indiquer la ville pour l\'événement.',
        'uk': 'Будь ласка, вкажіть місто проведення івенту.',
        'pl': 'Proszę podać miasto, w którym odbędzie się wydarzenie.',
        'de': 'Bitte geben Sie die Stadt für die Veranstaltung an.',
        'it': 'Si prega di specificare la città per l\'evento.'
    }

    await update.message.reply_text(
        city_request_texts.get(language_code, 'Please specify the city for the event.')
    )
    user_data.set_step('city_request')


# Функция для обработки города
async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    user_data.set_city(update.message.text)
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    # Получаем session_number для обновления записи
    session_number_query = "SELECT MAX(session_number) FROM orders WHERE user_id = ?"
    conn = create_connection(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(session_number_query, (user_data.get_user_id(),))
    session_number = cursor.fetchone()[0]

    if session_number is None:
        logging.error("Не удалось получить session_number. Возможно, записи в базе данных отсутствуют.")
    else:
        logging.info(f"Используем session_number: {session_number} для обновления.")

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET city = ? WHERE user_id = ? AND session_number = ?",
            (update.message.text, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

    context.user_data['user_data'] = user_data

    language_code = user_data.get_language()

    confirmation_texts = {
        'en': f'City: {user_data.get_city()}, correct?',
        'ru': f'Город: {user_data.get_city()}, правильно?',
        'es': f'Ciudad: {user_data.get_city()}, ¿correcto?',
        'fr': f'Ville: {user_data.get_city()}, correct ?',
        'uk': f'Місто: {user_data.get_city()}, правильно?',
        'pl': f'Miasto: {user_data.get_city()}, poprawne?',
        'de': f'Stadt: {user_data.get_city()}, richtig?',
        'it': f'Città: {user_data.get_city()}, corretto?'
    }

    await update.message.reply_text(
        confirmation_texts.get(language_code, f'City: {user_data.get_city()}, correct?'),
        reply_markup=yes_no_keyboard(language_code)
    )
    user_data.set_step('city_confirmation')

async def handle_city_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())

    if user_data.get_step() == 'city_confirmation':
        # Сохраняем введенный город
        city = update.message.text
        user_data.set_city(city)

        language_code = user_data.get_language()

        # Подтверждение сохранения данных
        confirmation_texts = {
            'en': f'{user_data.get_name()}, your city "{city}" has been saved. Calculating the cost for the proforma invoice.',
            'ru': f'{user_data.get_name()}, ваш город "{city}" сохранен. Рассчитываем стоимость для выдачи вам проформы.',
            'es': f'{user_data.get_name()}, su ciudad "{city}" ha sido guardada. Calculando el costo para emitir la proforma.',
            'fr': f'{user_data.get_name()}, votre ville "{city}" a été enregistrée. Calcul du coût pour l\'émission de la facture proforma.',
            'uk': f'{user_data.get_name()}, ваш місто "{city}" збережено. Розраховуємо вартість для видачі вам проформи.',
            'pl': f'{user_data.get_name()}, twoje miasto "{city}" zostało zapisane. Obliczanie kosztu wystawienia proformy.',
            'de': f'{user_data.get_name()}, Ihre Stadt "{city}" wurde gespeichert. Berechnung der Kosten für die Proformarechnung.',
            'it': f'{user_data.get_name()}, la tua città "{city}" è stata salvata. Calcolo del costo per l\'emissione della fattura proforma.'
        }

        await update.message.reply_text(
            confirmation_texts.get(language_code,
                                   f'{user_data.get_name()}, your city "{city}" has been saved. Calculating the cost for the proforma invoice.')
        )

        user_data.set_step('data_saved')


# Функция для получения текущей клавиатуры для шага
def get_current_step_keyboard(step, user_data):
    language = user_data.get_language()
    if step == 'calendar':
        month_offset = user_data.get_month_offset() if hasattr(user_data, 'get_month_offset') else 0
        return generate_calendar_keyboard(month_offset, language)
    elif step == 'time_selection':
        return generate_time_selection_keyboard(language, 'start')
    elif step == 'people_selection':
        return generate_person_selection_keyboard(language)
    elif step == 'style_selection':
        return generate_party_styles_keyboard(language)
    else:
        return None


# Словарь с переводами сообщения "Выбор только кнопками" на разные языки
translations = {
    'en': "Please use the buttons",
    'ru': "Выбор только кнопками",
    'es': "Por favor, usa los botones",
    'fr': "Veuillez utiliser les boutons",
    'de': "Bitte verwenden Sie die Tasten",
    'it': "Si prega di utilizzare i pulsanti",
    'uk': "Будь ласка, використовуйте кнопки",
    'pl': "Proszę użyć przycisków"
}

def save_user_id_to_orders(user_id):
    """Сохраняет user_id в таблицу orders с начальным значением null для даты."""
    conn = create_connection(DATABASE_PATH)
    if conn is not None:
        try:
            logging.info(f"Проверка существования записи в orders для user_id: {user_id}")
            select_query = "SELECT 1 FROM orders WHERE user_id = ?"
            cursor = conn.cursor()
            cursor.execute(select_query, (user_id,))
            exists = cursor.fetchone()

            if exists:
                logging.info(f"Запись для user_id {user_id} уже существует в таблице orders.")
            else:
                logging.info(f"Вставка нового user_id {user_id} с null датой в таблицу orders.")
                insert_query = "INSERT INTO orders (user_id, selected_date) VALUES (?, ?)"
                cursor.execute(insert_query, (user_id, None))  # Передаем None для заполнения null в базе данных
                conn.commit()
                logging.info(f"user_id {user_id} успешно добавлен в таблицу orders с null датой.")

        except Exception as e:
            logging.error(f"Ошибка базы данных при работе с таблицей orders: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных для работы с таблицей orders")



#№№№Функция для получения перевода на основе языка пользователя
def get_translation(user_data, key):
    language_code = user_data.get_language()  # Получаем код языка пользователя
    return translations.get(language_code, translations['en'])  # Возвращаем перевод или английский по умолчанию