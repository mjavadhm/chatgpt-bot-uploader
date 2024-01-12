import asyncio
import telegram
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if 'has_started' not in context.chat_data.get(chat_id, {}):
        await context.bot.send_message(chat_id=chat_id, text="Hello coptain!\nSend me a file" )
        context.chat_data[chat_id]['has_started'] = True

    else:
        await context.bot.send_message(chat_id=chat_id, text="Good to see you again captain!")

if __name__ == '__main__':
    application = ApplicationBuilder().token('6821047694:AAHpK7nIUrQW-53ifVtPwBaQikGaHM4s_dg').build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()

