from telegram import Update
from telegram.ext import Application, CommandHandler

async def start(update: Update, context):
    await update.message.reply_text('Hello!')

async def get_chat_id(update: Update, context):
    chat_id = update.message.chat_id
    await update.message.reply_text(f'Your chat ID is: {chat_id}')
    print(f'Chat ID: {chat_id}')

if __name__ == '__main__':
    application = Application.builder().token("7365546887:AAFimfH_lZxsv-v2RyaSktBRk7ww_s5Vs0U").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_chat_id", get_chat_id))

    application.run_polling()
