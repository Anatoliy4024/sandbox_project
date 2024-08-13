import os

# Путь к базе данных SQLite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'sqlite.db')

# Заголовки для выбора времени
time_selection_headers = {
    'start': {
        'en': "Select start and end time (minimum duration 2 hours)",
        'ru': "Выберите начальное и конечное время (минимальная продолжительность 2 часа)"
    },
    'end': {
        'en': "Select the end time",
        'ru': "Выберите конечное время"
    }
}

# Заголовки для выбора количества людей
people_selection_headers = {
    'en': "How many people are attending?",
    'ru': "Сколько человек будет присутствовать?"
}

# Заголовки для выбора стиля мероприятия
party_styles_headers = {
    'en': "What style do you choose?",
    'ru': "Какой стиль вы выбираете?"
}

# Заголовки для выбора города
city_selection_headers = {
    'en': "Select your city",
    'ru': "Выберите ваш город"
}

# Заголовки для выбора предпочтений
preferences_headers = {
    'en': "Please specify your preferences",
    'ru': "Укажите ваши предпочтения"
}

# Статусы пользователей
user_statuses = {
    'active': 1,
    'inactive': 0
}

# Статусы заказов
order_statuses = {
    'pending': 0,
    'confirmed': 1,
    'canceled': 2
}

# Словарь всех возможных заголовков для удобства
all_headers = {
    'time_selection': time_selection_headers,
    'people_selection': people_selection_headers,
    'party_styles': party_styles_headers,
    'city_selection': city_selection_headers,
    'preferences': preferences_headers
}

# Класс для хранения временных данных
class TemporaryData:
    def __init__(self):
        self.user_name = None
        self.city = None
        self.preferences = None
        self.language = None  # Поддержка языка

    def set_user_name(self, user_name):
        self.user_name = user_name

    def get_user_name(self):
        return self.user_name

    def clear_user_name(self):
        self.user_name = None

    def set_city(self, city):
        self.city = city

    def get_city(self):
        return self.city

    def clear_city(self):
        self.city = None

    def set_preferences(self, preferences):
        self.preferences = preferences

    def get_preferences(self):
        return self.preferences

    def clear_preferences(self):
        self.preferences = None

    def set_language(self, language):
        self.language = language  # Метод для установки языка

    def get_language(self):
        return self.language  # Метод для получения языка

    def clear_language(self):
        self.language = None  # Метод для очистки языка


class UserData:
    def __init__(self, user_id=None, username=None, language='en'):
        self.user_id = user_id
        self.username = username
        self.language = language
        self.name = None
        self.preferences = None
        self.city = None
        self.month_offset = 0  # Добавьте это свойство
        self.step = None
        self.start_time = None
        self.end_time = None
        self.person_count = None
        self.style = None
        self.date = None

    def get_month_offset(self):
        return self.month_offset

    def set_month_offset(self, offset):
        self.month_offset = offset

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_language(self, language):
        self.language = language

    def get_language(self):
        return self.language

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_preferences(self, preferences):
        self.preferences = preferences

    def get_preferences(self):
        return self.preferences

    def set_city(self, city):
        self.city = city

    def get_city(self):
        return self.city

    def set_step(self, step):
        self.step = step

    def get_step(self):
        return self.step

    def set_start_time(self, start_time):
        self.start_time = start_time

    def get_start_time(self):
        return self.start_time

    def set_end_time(self, end_time):
        self.end_time = end_time

    def get_end_time(self):
        return self.end_time

    def set_person_count(self, person_count):
        self.person_count = person_count

    def get_person_count(self):
        return self.person_count

    def set_style(self, style):
        self.style = style

    def get_style(self):
        return self.style

    def set_date(self, date):
        self.date = date

    def get_date(self):
        return self.date

    def clear_time(self):
        self.start_time = None
        self.end_time = None

# Другие константы и определения...

time_set_texts = {
    'start_time': {
        'en': 'Start time set to {}. Now select end time.',
        'ru': 'Время начала установлено на {}. Теперь выберите время окончания.',
        'es': 'La hora de inicio se ha establecido en {}. Ahora selecciona la hora de finalización.',
        'fr': 'L\'heure de début est fixée à {}. Maintenant, sélectionnez l\'heure de fin.',
        'uk': 'Час початку встановлено на {}. Тепер виберіть час закінчення.',
        'pl': 'Czas rozpoczęcia ustawiono на {}. Teraz wybierz czas zakończenia.',
        'de': 'Startzeit auf {} gesetzt. Wählen Sie nun die Endzeit.',
        'it': 'L\'ora di inizio è stata impostata su {}. Ora seleziona l\'ora di fine.'
    },
    'end_time': {
        'en': 'End time set to {}. Confirm your selection.',
        'ru': 'Время окончания установлено на {}. Подтвердите свой выбор.',
        'es': 'La hora de finalización se ha establecido en {}. Confirma tu selección.',
        'fr': 'L\'heure de fin est fixée à {}. Confirmez votre sélection.',
        'uk': 'Час закінчення встановлено на {}. Підтвердіть свій вибір.',
        'pl': 'Czas zakończenia ustawiono na {}. Potwierdź swój wybór.',
        'de': 'Endzeit auf {} gesetzt. Bestätigen Sie Ihre Auswahl.',
        'it': 'L\'ora di fine è stata impostata su {}. Conferma la tua selezione.'
    }
}
