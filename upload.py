import asyncio
import telegram
import openai
import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackContext, ConversationHandler

alluser = ['admin','javad']
allpass = ['1234','0150']
USERNAME, PASSWORD, LOGGEDIN = range(3)


openai.api_key = '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'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    await update.message.reply_text("Enter your username.")
    return USERNAME

async def username(update, contex):
    global usern
    usern = update.message.text
    await update.message.reply_text('And now password')
    return PASSWORD

async def password(update, contex):
    global passn
    passn = update.message.text
    if usern in alluser and passn in allpass:
        await update.message.reply_text('Logged in succesfully!\nAsk me anything you want or just send me a file')
        return LOGGEDIN
    else:
        await update.message.reply_text('Access denied!\nTry again by using /start')
        return ConversationHandler.END

#async loggedin(update: Update, context: ContextTypes.DEFUALT_TYPES)

async def reply_to_message(update: Update, context: CallbackContext):
    user_input = update.message.text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "system", "content": "you are telegrambot which help people to solve their problem also you are a little foul-mouthed and angry."}, {"role": "user", "content": user_input}],
        n=1,
        stop=None
    )

    await update.message.reply_text(response.choices[0].message['content'])

async def uploader(update: Update, context ):
    if update.message.video:
        video_file = await context.bot.get_file(update.message.video.file_id)
        video_path = f'/var/www/html/telegram/{update.message.video.file_name}.mp4'
        await video_file.download_to_drive(video_path)
        await update.message.reply_text(f'Video {update.message.video.file_name} downloaded to {video_path}')
    elif update.message.document:
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f'/var/www/html/telegram/{update.message.document.file_name}'
        await file.download_to_drive(file_path)
        await update.message.reply_text(f'File {update.message.document.file_name} downloaded to {file_path}')
    else:
        await update.message.reply_text('Unsupported file type.')

        
if __name__ == '__main__':
    application = ApplicationBuilder().token('6594664984:AAFQtIMLpdppT2xFeaGmi7Tb0djSx4qVpQc').build()
#   start_handler = CommandHandler('start', start)
#    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_message)
#    upload_handler = MessageHandler(filters.Document.ALL | filters.VIDEO, uploader)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
            LOGGEDIN: [MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_message), MessageHandler(filters.Document.ALL | filters.VIDEO, uploader)],
        },
        fallbacks=[],
        allow_reentry=True
    )


    application.add_handler(conv_handler)
 #   application.add_handler(chat_handler)
#    application.add_handler(upload_handler)
    application.run_polling()