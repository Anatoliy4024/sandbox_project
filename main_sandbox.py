import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import calendar
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# Ваш токен
BOT_TOKEN = '7365546887:AAFimfH_lZxsv-v2RyaSktBRk7ww_s5Vs0U'

# Генерация кнопок календаря
def generate_calendar_buttons(year, month, selected_day=None, disable=False):
    now = datetime.now()
    today = now.day
    current_year = now.year
    current_month = now.month

    first_weekday, num_days = calendar.monthrange(year, month)

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    buttons = [[InlineKeyboardButton(day, callback_data="none")] for day in weekdays]

    day = 1
    for col in range(5):
        for row in range(7):
            if col == 0 and row < first_weekday:
                buttons[row].append(InlineKeyboardButton(" ", callback_data="none"))
            elif day <= num_days:
                if year == current_year and month == current_month and day <= today:
                    buttons[row].append(InlineKeyboardButton(f"🔴 {day}", callback_data="none"))
                elif str(day) == selected_day:
                    buttons[row].append(InlineKeyboardButton(f"🔴 {day}", callback_data=f"day_{day}"))
                else:
                    text = f"🟢 {day}" if not disable else f"🟢 {day}"
                    callback_data = f"day_{day}" if not disable else 'none'
                    buttons[row].append(InlineKeyboardButton(text, callback_data=callback_data))
                day += 1
            else:
                buttons[row].append(InlineKeyboardButton(" ", callback_data="none"))

    while len(buttons[-1]) < 6:
        buttons[-1].append(InlineKeyboardButton(" ", callback_data="none"))

    buttons.append([
        InlineKeyboardButton("<", callback_data="prev_month" if not disable else "none"),
        InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="none"),
        InlineKeyboardButton(">", callback_data="next_month" if not disable else "none")
    ])

    return buttons

# Стартовый обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    year, month = now.year, now.month
    context.user_data['year'] = year
    context.user_data['month'] = month

    buttons = generate_calendar_buttons(year, month)
    message = await update.message.reply_text(
        "Выберите дату:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    context.user_data['last_message_id'] = message.message_id

# Обработчик нажатия на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data

    year = user_data.get('year')
    month = user_data.get('month')

    current_year = datetime.now().year
    current_month = datetime.now().month

    if query.data.startswith('day_'):
        selected_day = query.data.split('_')[1]
        user_data['selected_day'] = selected_day

        buttons = generate_calendar_buttons(year, month, selected_day=selected_day, disable=True)
        await query.message.edit_text("Выберите дату:", reply_markup=InlineKeyboardMarkup(buttons))

        await query.message.reply_text(
            f"Вы выбрали {year}-{month:02d}-{selected_day}, правильно?",
            reply_markup=yes_no_keyboard(disable=False)
        )

    elif query.data == 'prev_month':
        # Ограничение на переход к предыдущему месяцу
        if month == current_month and year == current_year:
            pass  # Не позволяем идти на месяц назад из текущего месяца
        else:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            user_data['year'] = year
            user_data['month'] = month
            buttons = generate_calendar_buttons(year, month)
            await query.message.edit_text("Выберите дату:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == 'next_month':
        # Ограничение на переход на два месяца вперед
        max_month = current_month + 2
        max_year = current_year
        if max_month > 12:
            max_month -= 12
            max_year += 1

        if year > max_year or (year == max_year and month >= max_month):
            pass  # Не позволяем идти дальше двух месяцев вперед
        else:
            month += 1
            if month > 12:
                month = 1
                year += 1
            user_data['year'] = year
            user_data['month'] = month
            buttons = generate_calendar_buttons(year, month)
            await query.message.edit_text("Выберите дату:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == 'yes':
        await query.message.edit_reply_markup(reply_markup=yes_no_keyboard(disable=True))
        await query.message.reply_text("Спасибо, тест закончен. Чтобы начать снова, нажмите /start.")

    elif query.data == 'no':
        buttons = generate_calendar_buttons(year, month)
        await query.message.edit_text("Выберите дату:", reply_markup=InlineKeyboardMarkup(buttons))

# Клавиатура для подтверждения
def yes_no_keyboard(disable=False):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Да", callback_data='yes' if not disable else 'none'),
            InlineKeyboardButton("Назад", callback_data='no' if not disable else 'none')
        ]
    ])

# Основная функция
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()

if __name__ == "__main__":
    main()
