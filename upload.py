import asyncio
import telegram
import openai
import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackContext

openai.api_key = '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'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="hi!"
    )
#async def username(update: Update, contex: ContextTypes.DEFAULT_TYPE):
 #   await

async def reply_to_message(update: Update, context: CallbackContext):
    user_input = update.message.text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a chat bot."}, {"role": "user", "content": user_input}],
        n=1,
        stop=None
    )

    await update.message.reply_text(response.choices[0].message['content'])


if __name__ == '__main__':
    application = ApplicationBuilder().token('6594664984:AAFQtIMLpdppT2xFeaGmi7Tb0djSx4qVpQc').build()
    
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_message)
    start_handler = CommandHandler('start', start)


    application.add_handler(start_handler)
    application.add_handler(chat_handler)

    application.run_polling()