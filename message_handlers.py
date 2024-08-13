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
        #____________________________________________________________________________________________
        try:
            # Проверка существования пользователя
            logging.info(f"Проверка существования пользователя с user_id: {update.message.from_user.id}")
            select_query = "SELECT 1 FROM users WHERE user_id = ?"
            cursor = conn.cursor()
            cursor.execute(select_query, (update.message.from_user.id,))
            exists = cursor.fetchone()

            if exists:
                # Обновление данных пользователя
                logging.info(f"Обновление данных пользователя: {user_data.get_username()}")
                update_query = "UPDATE users SET username = ?, language = ?, user_name = ? WHERE user_id= ?"
                update_params = (user_data.get_username(), user_data.get_language(),user_data.get_name(), update.message.from_user.id)
                execute_query_with_retry(update_query, update_params)
            else:
                # Вставка нового пользователя
                logging.info(f"Вставка нового пользователя: {user_data.get_username()}")
                insert_query = "INSERT INTO users (user_id, username, language,user_name) VALUES (?, ?, ?,?)"
                insert_params = (update.message.from_user.id, user_data.get_username(), user_data.get_language(),user_data.get_name())
                execute_query_with_retry(insert_query, insert_params)

        except Exception as e:
            logging.error(f"Ошибка базы данных: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
            #_______________________________________________________________
    else:
        logging.error("Не удалось создать соединение с базой данных")

    # Сохранение в базу данных
    # conn = create_connection(DATABASE_PATH)
    # if conn is not None:
    #     print("Принт 9: Соединение с базой данных установлено")
    #     query = """
    #     INSERT INTO users (user_id, language, user_name, username)
    #     VALUES (?, ?, ?, ?)
    #     """
    #     params = (update.message.from_user.id, language_code, user_data.get_name(), user_data.get_username())
    #     execute_query_with_retry(query, params)
    #     print(f"Принт 10: Выполнен запрос INSERT с параметрами: {params}")
    # else:
    #     print("Принт 11: Не удалось создать соединение с базой данных")

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
        language_code = user_data.get_language()

        confirmation_texts = {
            'en': f'{user_data.get_name()}, your data has been saved. Calculating the cost for the proforma invoice.',
            'ru': f'{user_data.get_name()}, ваши данные сохранены. Рассчитываем стоимость для выдачи вам проформы.',
            'es': f'{user_data.get_name()}, sus datos han sido guardados. Calculando el costo para emitir la proforma.',
            'fr': f'{user_data.get_name()}, vos données ont été sauvegardées. Calcul du coût pour l\'émission de la facture proforma.',
            'uk': f'{user_data.get_name()}, ваші дані збережено. Розраховуємо вартість для видачі вам проформи.',
            'pl': f'{user_data.get_name()}, twoje dane zostały zapisane. Obliczanie kosztu wystawienia proformy.',
            'de': f'{user_data.get_name()}, Ihre Daten wurden gespeichert. Berechnung der Kosten für die Proformarechnung.',
            'it': f'{user_data.get_name()}, i tuoi dati sono stati salvati. Calcolo del costo per l\'emissione della fattura proforma.'
        }

        await update.message.reply_text(
            confirmation_texts.get(language_code,
                                   f'{user_data.get_name()}, your data has been saved. Calculating the cost for the proforma invoice.')
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

# Функция для получения перевода на основе языка пользователя
def get_translation(user_data, key):
    language_code = user_data.get_language()  # Получаем код языка пользователя
    return translations.get(language_code, translations['en'])  # Возвращаем перевод или английский по умолчанию
