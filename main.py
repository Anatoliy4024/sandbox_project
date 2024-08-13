import os
import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from abstract_functions import create_connection, execute_query, execute_query_with_retry
import sqlite3
from constants import UserData, time_selection_headers, people_selection_headers, party_styles_headers, time_set_texts
from database_logger import log_message, log_query
from keyboards import language_selection_keyboard, yes_no_keyboard, generate_calendar_keyboard, generate_time_selection_keyboard, generate_person_selection_keyboard, generate_party_styles_keyboard
from message_handlers import handle_message, handle_city_confirmation
from constants import TemporaryData, DATABASE_PATH

# Включаем логирование и указываем файл для логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Установите уровень на DEBUG для детальной информации
    filename='db_operations.log',  # Укажите имя файла для логов
    filemode='w'  # 'w' - перезаписывать файл при каждом запуске, 'a' - добавлять к существующему файлу
)

logger = logging.getLogger(__name__)
logger.info(f"Database path: {DATABASE_PATH}")

#########################################################################
# добавление обработчика ошибок
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters, Application
from telegram.error import TelegramError

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # Notify the developer via Telegram (if desired)
    if isinstance(update, Update):
        await update.message.reply_text("An error occurred. The administrator has been notified.")

def add_username_column():
    conn = create_connection(DATABASE_PATH)
    if conn is not None:
        query = """
        ALTER TABLE users ADD COLUMN username TEXT
        """
        execute_query(conn, query)
    else:
        logging.error("Failed to create database connection")

# Пути к видеофайлам
VIDEO_PATHS = [
    'media/IMG_5981 (online-video-cutter.com).mp4',
    'media/IMG_6156 (online-video-cutter.com).mp4',
    'media/IMG_4077_1 (online-video-cutter.com).mp4',
    'media/IMG_6412 (online-video-cutter.com).mp4'
]

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = '7407529729:AAErOT5NBpMSO-V-HPAW-MDu_1WQt0TtXng'

# Создайте соединение с базой данных
conn = create_connection(DATABASE_PATH)

# Версия "соединение с базой данных" сделанная с 13.00 до 14.00 - 8.08.2024
import time
import sqlite3
import logging

def execute_query_with_retry(conn, query, params=(), max_retries=5):
    """Выполняет SQL-запрос с повторными попытками при блокировке базы данных."""
    retries = 0
    while retries < max_retries:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries += 1
                logging.warning(f"Database is locked, retrying {retries}/{max_retries}")
                time.sleep(1)  # Задержка перед повторной попыткой
            else:
                logging.error(f"Error executing query: {e}")
                raise e

import sqlite3
import time
from database_logger import log_message, log_query
from constants import DATABASE_PATH

def create_connection(db_file):
    """ create a database connection to the SQLite database specified by the db_file """
    try:
        conn = sqlite3.connect(db_file)
        log_message(f"Database connected: {db_file}")
        return conn
    except sqlite3.Error as e:
        log_message(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query, params=()):
    """Выполняет SQL-запрос."""
    try:
        c = conn.cursor()
        log_query(query, params)  # Логирование запроса
        c.execute(query, params)
        conn.commit()
        log_message(f"Query executed successfully: {query} with params {params}")
    except sqlite3.Error as e:
        log_message(f"Error executing query: {e}")

# Использование в вашей функции start:
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Функция start запущена")

    # Инициализация данных пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    # Установка начальных данных
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    username = update.message.from_user.username if update.message else update.callback_query.from_user.username
    user_data.set_user_id(user_id)
    user_data.set_username(username)
    user_data.set_step('start')
    user_data.set_language('en')  # Здесь можно задать язык или получить его от пользователя

    logging.info(f"Получен user_id: {user_id}, username: {username}, language: {user_data.get_language()}")

    # Создайте соединение с базой данных
    conn = create_connection(DATABASE_PATH)
    if conn is not None:
        try:
            # Проверка существования пользователя
            logging.info(f"Проверка существования пользователя с user_id: {user_id}")
            select_query = "SELECT 1 FROM users WHERE user_id = ?"
            cursor = conn.cursor()
            cursor.execute(select_query, (user_id,))
            exists = cursor.fetchone()

            if exists:
                # Обновление данных пользователя
                logging.info(f"Обновление данных пользователя: {username}")
                update_query = "UPDATE users SET username = ?, language = ? WHERE user_id= ?"
                update_params = (username, user_data.get_language(), user_id)
                execute_query_with_retry(conn, update_query, update_params)
            else:
                # Вставка нового пользователя
                logging.info(f"Вставка нового пользователя: {username}")
                insert_query = "INSERT INTO users (user_id, username, language) VALUES (?, ?, ?)"
                insert_params = (user_id, username, user_data.get_language())
                execute_query_with_retry(conn, insert_query, insert_params)

        except Exception as e:
            logging.error(f"Ошибка базы данных: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных")

    if update.message:
        await update.message.reply_text(
            f"Welcome {username}! Choose your language / Выберите язык / Elige tu idioma",
            reply_markup=language_selection_keyboard()
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            f"Welcome {username}! Choose your language / Выберите язык / Elige tu idioma",
            reply_markup=language_selection_keyboard()
        )
    logging.info("Функция start завершена")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Функция button_callback запущена")

    query = update.callback_query
    await query.answer()
    logging.info("Функция ??????????????????????? запущена")
    logging.info(query.data)
    logging.info("Функция ??????????????????????? запущена")



    # Инициализация данных пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    # Обработка выбора языка
    if query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)
        user_data.set_step('greeting')

        # Блокируем кнопки языков после выбора
        await query.edit_message_reply_markup(reply_markup=disable_language_buttons(query.message.reply_markup))

        # Обновляем язык в базе данных
        conn = create_connection(DATABASE_PATH)
        if conn is not None:
            try:
                update_query = "UPDATE users SET language = ? WHERE user_id = ?"
                update_params = (language_code, update.callback_query.from_user.id)
                execute_query_with_retry(conn, update_query, update_params)
            except Exception as e:
                logging.error(f"Ошибка обновления языка в базе данных: {e}")
            finally:
                conn.close()

        # Отправляем сообщение с "ожиданием" на выбранном языке
        loading_texts = {
            'en': 'Loading...',
            'ru': 'Ожидай...',
            'es': 'Cargando...',
            'fr': 'Chargement...',
            'uk': 'Завантаження...',
            'pl': 'Ładowanie...',
            'de': 'Laden...',
            'it': 'Caricamento...'
        }
        loading_message = await query.message.reply_text(
            loading_texts.get(language_code, 'Loading...'),
        )

        # Выбор случайного видео
        video_path = random.choice(VIDEO_PATHS)

        # Загрузка видео и обновление сообщения
        if os.path.exists(video_path):
            # Отправляем видео как документ
            with open(video_path, 'rb') as video_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=video_file,
                    disable_notification=True
                )
                # Удаляем сообщение с "ожиданием"
                await loading_message.delete()
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Video file not found.")
            await loading_message.delete()

        greeting_texts = {
            'en': 'Hello! What is your name?',
            'ru': 'Привет! Как вас зовут?',
            'es': '¡Hola! ¿Cómo te llamas?',
            'fr': 'Salut! Quel est votre nom ?',
            'uk': 'Привіт! Як вас звати?',
            'pl': 'Cześć! Jak masz на імʼя?',
            'de': 'Hallo! Wie heißt du?',
            'it': 'Ciao! Come ti chiami?'
        }
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=greeting_texts.get(language_code, 'Hello! What is your name?')
        )

    elif query.data == 'yes':
        if user_data.get_step() == 'name_received':
            user_data.set_step('calendar')
            await show_calendar(query, user_data.get_month_offset(), user_data.get_language())
        elif user_data.get_step() == 'date_confirmation':
            user_data.set_step('time_selection')
            await query.message.reply_text(
                time_selection_headers['start'].get(user_data.get_language(),
                                                    "Select start and end time (minimum duration 2 hours)"),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'start')
            )
        elif user_data.get_step() == 'time_confirmation':
            user_data.set_step('people_selection')
            await query.message.reply_text(
                people_selection_headers.get(user_data.get_language(), 'How many people are attending?'),
                reply_markup=generate_person_selection_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'people_confirmation':
            user_data.set_step('style_selection')
            await query.message.reply_text(
                party_styles_headers.get(user_data.get_language(), 'What style do you choose?'),
                reply_markup=generate_party_styles_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'style_confirmation':
            user_data.set_step('preferences_request')
            preferences_request_texts = {
                'en': 'Please write your preferences for table setting colors, food items (or exclusions), and desired table accessories (candles, glasses, etc.) - no more than 1000 characters.',
'ru': 'Напишите свои предпочтения по цвету сервировки, продуктам (или исключениям), и желаемые аксессуары для стола (свечи, бокалы и прочее) - не более 1000 знаков.',
'es': 'Escriba sus preferencias de colores para la mesa, artículos de comida (o exclusiones), y accesorios para la mesa (velas, copas, etc.) - no más de 1000 caracteres.',
'fr': 'Veuillez écrire vos préférences pour les couleurs de la table, les aliments (ou exclusions), et les accessoires de table désirés (bougies, verres, etc.) - pas plus de 1000 caractères.',
'uk': 'Напишіть свої уподобання щодо кольору сервірування, продуктів (або виключень), і бажані аксесуари для столу (свічки, келихи тощо) - не більше 1000 знаків.',
'pl': 'Napisz swoje preferencje dotyczące kolorów nakrycia stołu, produktów spożywczych (lub wykluczeń), i pożądanych akcesoriów do stołu (świece, szklanki itp.) - nie więcej niż 1000 znaków.',
'de': 'Bitte schreiben Sie Ihre Vorlieben für Tischfarben, Lebensmittel (oder Ausschlüsse), und gewünschte Tischaccessoires (Kerzen, Gläser usw.) - nicht mehr als 1000 Zeichen.',
'it': 'Scrivi le tue preferenze per i colori della tavola, gli alimenti (o esclusioni), e gli accessori desiderati per la tavola (candele, bicchieri, ecc.) - non più di 1000 caratteri.'
            }
            await query.message.reply_text(
                preferences_request_texts.get(user_data.get_language(),
                                              "Please write your preferences for table setting colors, food items (or exclusions), and desired table accessories (candles, glasses, etc.) - no more than 1000 characters.")
            )

        # Disable the "no" button
        await query.edit_message_reply_markup(reply_markup=disable_yes_no_buttons(query.message.reply_markup))

    elif query.data == 'no':
        logging.info(f"Текущее состояние user_data.get_step(): {user_data.get_step()}")
        if user_data.get_step() == 'calendar':
            user_data.set_step('name_received')
            logging.info("Лог перед вызовом handle_name")  # Лог до вызова
            await handle_name(query, context)
            logging.info("Лог после вызова handle_name")  # Лог после вызова
        elif user_data.get_step() == 'date_confirmation':
            user_data.set_step('calendar')
            await show_calendar(query, user_data.get_month_offset(), user_data.get_language())
        elif user_data.get_step() == 'name_received':
            user_data.set_step('greeting')
            await start(update, context)
        elif user_data.get_step() == 'time_selection':
            user_data.clear_time()
            await query.message.reply_text(
                time_selection_headers['start'].get(user_data.get_language(),
                                                    "Select start and end time (minimum duration 2 hours)"),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'start')
            )
        elif user_data.get_step() == 'time_confirmation':
            user_data.clear_time()
            await query.message.reply_text(
                time_selection_headers['start'].get(user_data.get_language(),
                                                    "Select start and end time (minimum duration 2 hours)"),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'start')
            )
        elif user_data.get_step() == 'people_selection':
            await query.message.reply_text(
                people_selection_headers.get(user_data.get_language(), 'How many people are attending?'),
                reply_markup=generate_person_selection_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'people_confirmation':
            user_data.set_step('people_selection')
            await query.message.reply_text(
                people_selection_headers.get(user_data.get_language(), 'How many people are attending?'),
                reply_markup=generate_person_selection_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'style_selection':
            await query.message.reply_text(
                party_styles_headers.get(user_data.get_language(), 'What style do you choose?'),
                reply_markup=generate_party_styles_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'style_confirmation':
            user_data.set_step('style_selection')
            await query.message.reply_text(
                party_styles_headers.get(user_data.get_language(), 'What style do you choose?'),
                reply_markup=generate_party_styles_keyboard(user_data.get_language())
            )

    elif query.data.startswith('date_'):
        selected_date = query.data.split('_')[1]
        user_data.set_step('date_confirmation')
        user_data.set_date(selected_date)

        # Меняем цвет кнопки на красный и делаем все остальные кнопки неактивными
        await query.edit_message_reply_markup(
            reply_markup=disable_calendar_buttons(query.message.reply_markup, selected_date))

        confirmation_texts = {
            'en': f'You selected {selected_date}, correct?',
            'ru': f'Вы выбрали {selected_date}, правильно?',
            'es': f'Seleccionaste {selected_date}, ¿correcto?',
            'fr': f'Vous avez sélectionné {selected_date}, correct ?',
            'uk': f'Ви вибрали {selected_date}, правильно?',
            'pl': f'Wybrałeś {selected_date}, poprawне?',
            'de': f'Sie haben {selected_date} gewählt, richtig?',
            'it': f'Hai selezionato {selected_date}, corretto?'
        }
        await query.message.reply_text(
            confirmation_texts.get(user_data.get_language(), f'You selected {selected_date}, correct?'),
            reply_markup=yes_no_keyboard(user_data.get_language())
        )

    elif query.data.startswith('time_'):
        selected_time = query.data.split('_')[1]
        if not user_data.get_start_time():
            user_data.set_start_time(selected_time)
            await query.message.reply_text(
                time_set_texts['start_time'].get(user_data.get_language(),
                                                 'Start time set to {}. Now select end time.').format(selected_time),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'end',
                                                              user_data.get_start_time())
            )
        else:
            user_data.set_end_time(selected_time)
            start_time = datetime.strptime(user_data.get_start_time(), '%H:%M')
            end_time = datetime.strptime(user_data.get_end_time(), '%H:%M')
            if (end_time - start_time).seconds >= 7200:
                user_data.set_step('time_confirmation')
                await query.message.reply_text(
                    time_set_texts['end_time'].get(user_data.get_language(),
                                                   'End time set to {}. Confirm your selection.').format(selected_time),
                    reply_markup=yes_no_keyboard(user_data.get_language())
                )
            else:
                await query.message.reply_text(
                    f"Minimum duration is 2 hours. Please select an end time at least 2 hours after the start time.",
                    reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'end',
                                                                  user_data.get_start_time())
                )
        await query.edit_message_reply_markup(
            reply_markup=disable_time_buttons(query.message.reply_markup, selected_time))

    elif query.data.startswith('person_'):
        selected_person = query.data.split('_')[1]
        user_data.set_step('people_confirmation')
        user_data.set_person_count(selected_person)

        # Меняем цвет кнопки на красный и делаем все остальные кнопки неактивными
        await query.edit_message_reply_markup(
            reply_markup=disable_person_buttons(query.message.reply_markup, selected_person))

        confirmation_texts = {
            'en': f'You selected {selected_person} people, correct?',
            'ru': f'Вы выбрали {selected_person} человек, правильно?',
            'es': f'Seleccionaste {selected_person} personas, ¿correctо?',
            'fr': f'Vous avez sélectionné {selected_person} personnes, correct ?',
            'uk': f'Ви вибрали {selected_person} людей, правильно?',
            'pl': f'Wybrałeś {selected_person} osób, poprawне?',
            'de': f'Sie haben {selected_person} Personen gewählt, richtig?',
            'it': f'Hai selezionato {selected_person} persone, corretto?'
        }
        await query.message.reply_text(
            confirmation_texts.get(user_data.get_language(), f'You selected {selected_person} people, correct?'),
            reply_markup=yes_no_keyboard(user_data.get_language())
        )

    elif query.data.startswith('style_'):
        selected_style = query.data.split('_')[1]
        user_data.set_step('style_confirmation')
        user_data.set_style(selected_style)

        # Меняем цвет кнопки на красный и делаем все остальные кнопки неактивными
        await query.edit_message_reply_markup(
            reply_markup=disable_style_buttons(query.message.reply_markup, selected_style))

        confirmation_texts = {
            'en': f'You selected {selected_style} style, correct?',
            'ru': f'Вы выбрали стиль {selected_style}, правильно?',
            'es': f'Seleccionaste el стиль {selected_style}, ¿correctо?',
            'fr': f'Vous avez sélectionné le стиль {selected_style}, correct ?',
            'uk': f'Ви вибрали стиль {selected_style}, правильно?',
            'pl': f'Wybrałeś {selected_style} стиль, правильно?',
            'de': f'Sie haben den стиль {selected_style} gewählt, richtig?',
            'it': f'Hai selezionato lo стиль {selected_style}, corretto?'
        }
        await query.message.reply_text(
            confirmation_texts.get(user_data.get_language(), f'You selected {selected_style} style, correct?'),
            reply_markup=yes_no_keyboard(user_data.get_language())
        )

    elif query.data.startswith('prev_month_') or query.data.startswith('next_month_'):
        month_offset = int(query.data.split('_')[2])
        user_data.set_month_offset(month_offset)
        await show_calendar(query, month_offset, user_data.get_language())

    logging.info("Функция button_callback завершена")


async def show_calendar(query, month_offset, language):
    logging.info(f"Функция show_calendar запущена с параметрами: month_offset={month_offset}, language={language}")

    # Ограничение значений month_offset
    if month_offset < -1:
        logging.info("month_offset был меньше -1, установлен в -1")
        month_offset = -1
    elif month_offset > 2:
        logging.info("month_offset был больше 2, установлен в 2")
        month_offset = 2

    # Генерация клавиатуры календаря
    calendar_keyboard = generate_calendar_keyboard(month_offset, language)
    logging.info(f"Календарная клавиатура сгенерирована для month_offset={month_offset}, language={language}")

    # Тексты для выбора даты на разных языках
    select_date_text = {
        'en': "Select a date:",
        'ru': "Выберите дату:",
        'es': "Seleccione una fecha:",
        'fr': "Sélectionnez une date:",
        'uk': "Виберіть дату:",
        'pl': "Wybierz datę:",
        'de': "Wählen Sie ein Datum:",
        'it': "Seleziona una data:"
    }

    # Отправка сообщения с клавиатурой календаря
    await query.message.reply_text(
        select_date_text.get(language, 'Select a date:'),
        reply_markup=calendar_keyboard
    )
    logging.info("Сообщение с клавиатурой календаря отправлено пользователю")


# async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Инициализация данных пользователя
#     user_data = context.user_data.get('user_data', UserData())
#     context.user_data['user_data'] = user_data
#
#     logging.info("Проверка выполнения: до блока if update.callback_query")
#
#     if update.callback_query:
#         user_data.set_name("Имя пользователя")
#     else:
#         logging.info(f"Получено значение из update.message.text: {update.message.text}")
#         user_data.set_name(update.message.text)
#         logging.info(f"Имя пользователя, присвоенное в user_data: {user_data.get_name()}")
#
#         # Вставляем print для вывода имени пользователя в терминал
#         print(f"Введенное имя: {update.message.text}")
#
#     logging.info("Проверка выполнения: после блока if update.callback_query")
#
#     user_data.set_step('name_received')
#     user_data.set_username(update.message.from_user.username if update.message else "Имя пользователя")
#
#     logging.info(f"Получено имя пользователя из update.message.text: {update.message.text}")
#
#     language_code = user_data.get_language()
#     logging.info(f"Saving user_name: {user_data.get_name()} and username: {user_data.get_username()}")
#
#     # Сохранение в базу данных
#     conn = create_connection(DATABASE_PATH)
#     if conn is not None:
#         query = """
#         INSERT INTO users (user_id, language, user_name, username)
#         VALUES (?, ?, ?, ?)
#         """
#         params = (update.message.from_user.id, language_code, user_data.get_name(), user_data.get_username())
#         execute_query_with_retry(conn, query, params)
#     else:
#         logging.error("Failed to create database connection")
#
#     greeting_texts = {
#         'en': f'Hello {user_data.get_name()}! Do you want to see available dates?',
#         'ru': f'Привет {user_data.get_name()}! Хочешь увидеть доступные даты?',
#         'es': f'Hola {user_data.get_name()}! ¿Quieres ver las fechas disponibles?',
#         'fr': f'Bonjour {user_data.get_name()}! Voulez-vous voir les dates disponibles?',
#         'uk': f'Привіт {user_data.get_name()}! Хочеш подивитися які дати доступні?',
#         'pl': f'Cześć {user_data.get_name()}! Chcesz zobaczyć dostępne daty?',
#         'de': f'Hallo {user_data.get_name()}! Möchten Sie verfügbare Daten sehen?',
#         'it': f'Ciao {user_data.get_name()}! Vuoi vedere le date disponibili?'
#     }
#
#     if update.message:
#         await update.message.reply_text(
#             greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
#             reply_markup=yes_no_keyboard(language_code)
#         )
#     elif update.callback_query:
#         await update.callback_query.message.reply_text(
#             greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
#             reply_markup=yes_no_keyboard(language_code)
#         )



def disable_calendar_buttons(reply_markup, selected_date):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(selected_date):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_date.split('-')[2]}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_time_buttons(reply_markup, selected_time):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(selected_time):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_time}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_person_buttons(reply_markup, selected_person):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(f'person_{selected_person}'):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_person}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_style_buttons(reply_markup, selected_style):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(f'style_{selected_style}'):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_style}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_yes_no_buttons(reply_markup):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

if __name__ == '__main__':
    temp_data = TemporaryData()


    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        # Уведомление разработчика через Telegram
        if isinstance(update, Update):
            try:
                if update.message:
                    await update.message.reply_text("An error occurred. The administrator has been notified.")
                elif update.callback_query:
                    await update.callback_query.message.reply_text(
                        "An error occurred. The administrator has been notified.")
            except Exception as e:
                logger.error(f"Error notifying the user: {e}")


    def disable_language_buttons(reply_markup):
        new_keyboard = []
        for row in reply_markup.inline_keyboard:
            new_row = []
            for button in row:
                # Делаем кнопку неактивной, присваивая ей callback_data='none'
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
            new_keyboard.append(new_row)
        return InlineKeyboardMarkup(new_keyboard)


    logging.basicConfig(level=logging.DEBUG)

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_city_confirmation))

    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)

    application.run_polling()
