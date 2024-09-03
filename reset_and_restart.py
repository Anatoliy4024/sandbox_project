#
# import logging
# from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters
# from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
# from message_handlers import show_proforma, handle_message, handle_city, handle_city_confirmation
# from main import start, button_callback, error_handler, ContextTypes
#
# BOT_TOKEN = '7407529729:AAErOT5NBpMSO-V-HPAW-MDu_1WQt0TtXng'
#
# async def reset_and_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Функция для сброса всех сообщений и клавиатур, сохранения последнего сообщения и клавиатуры,
#     отображения проформы и предложения перезапустить процесс.
#     """
#     # Удаляем все сообщения с клавиатурами
#     try:
#         chat_id = update.effective_chat.id
#         messages_to_delete = context.user_data.get('messages_to_delete', [])
#
#         for message_id in messages_to_delete:
#             await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
#
#         # Сохраняем последнее сообщение перед удалением
#         last_message = update.effective_message.text
#         last_keyboard = update.effective_message.reply_markup
#
#         # Показываем проформу (текущий номер проформы и необходимые данные)
#         await show_proforma(update, context)
#
#         # Предлагаем перезапустить процесс
#         restart_button = InlineKeyboardButton(text="Начать сначала", callback_data='restart')
#         keyboard = InlineKeyboardMarkup([[restart_button]])
#         await context.bot.send_message(chat_id=chat_id, text="Процесс завершен. Хотите начать сначала?",
#                                        reply_markup=keyboard)
#
#     except Exception as e:
#         logging.error(f"Ошибка при сбросе сообщений и перезапуске: {e}")
#
#     # Обновляем список сообщений для удаления в будущем
#     context.user_data['messages_to_delete'] = []
#
#
# # Обработчик для перезапуска
# async def restart_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Здесь вы можете добавить логику для повторного вызова функции `start`
#     await start(update, context)
#
#
# if __name__ == '__main__':
#     application = ApplicationBuilder().token(BOT_TOKEN).build()
#     application.add_handler(CommandHandler('start', start))
#     application.add_handler(CallbackQueryHandler(button_callback))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#     application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_city_confirmation))
#
#     # Добавляем новый обработчик для перезапуска процесса
#     application.add_handler(CallbackQueryHandler(restart_process, pattern='restart'))
#
#     # Регистрация обработчика ошибок
#     application.add_error_handler(error_handler)
#
#     application.run_polling()
