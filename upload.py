import asyncio
import telegram
import openai
import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackContext, ConversationHandler

user_chat_history = {}
user_chat_setting = {}
alluser = ['admin','javad','Javad','Admin']
allpass = ['1234','0150','Admin']
USERNAME, PASSWORD, LOGGEDIN, WAIT_FOR_USER_MESSAGE = range(4)



openai.api_key = '******'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    user_id = update.effective_user.id
    if user_id not in user_chat_history:
        user_chat_setting[user_id] = "you are a Telegram bot designed to assist users in solving problems. You are helpful."

    await update.message.reply_text("Enter your username")
    return USERNAME

async def about(update, context):
    await update.message.reply_text('Another chatgpt bot but! youcan choose role and save your files\n(🤥We respect your privacy🤥)\nyou can see list of the commands in /commands\nGithub link : https://github.com/mjavadhm/juploadbot/')

async def commandsa(update, contex):
    await update.message.reply_text("/start ---> Login\n/clear_history ---> Start new chat and clear history\n/set_role <input> ---> set bot role\n/reset_role ---> default setting for bot\n/about ---> More information about Bot")

async def username(update, contex):
    global usern
    usern = update.message.text
    await update.message.reply_text('And now password')
    return PASSWORD

async def password(update, contex):
    global passn
    passn = update.message.text
    if usern in alluser and passn in allpass:
        await update.message.reply_text('Logged in succesfully!\nAsk me anything you want or just send me a file(use /about for more information)')
        return LOGGEDIN
    else:
        await update.message.reply_text('Access denied!\nTry again by using /start')
        return ConversationHandler.END

async def role(update, context):
    user_id = update.effective_user.id
    await update.message.reply_text(f'Your role has been set to: {user_chat_setting[user_id]}')

async def set_role(update, context):
    await update.message.reply_text('Enter bot role:')
    return WAIT_FOR_USER_MESSAGE

async def get_user_message(update, context):
    user_id = update.effective_user.id
    user_chat_setting[user_id] = update.message.text
    await update.message.reply_text(f'Your role has been set to: {user_chat_setting[user_id]}')
    return LOGGEDIN

async def reset_role(update, contex):
    user_id = update.effective_user.id
    user_chat_setting[user_id] = "you are a Telegram bot designed to assist users in solving problems. You are helpful."

async def reply_to_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    user_id = update.effective_user.id

    if user_id not in user_chat_history:
        user_chat_history[user_id] = []
#    if user_id not in user_chat_history:
#       user_chat_setting[user_id] = "you are a Telegram bot designed to assist users in solving problems. You are helpful."

    user_chat_history[user_id].append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "system", "content": user_chat_setting[user_id] }, *user_chat_history[user_id]],
        n=1,
        stop=None
    )

    await update.message.reply_text(response.choices[0].message['content'])

async def clear_history(update, contex):
    user_id = update.effective_user.id
    user_chat_history[user_id] = []
    await update.message.reply_text("Chat history cleared.")


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
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, username)
            ],
            PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, password)
            ],
            LOGGEDIN: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_message),
                MessageHandler(filters.Document.ALL | filters.VIDEO, uploader),
                CommandHandler('clear_history',clear_history),
                CommandHandler('about',about),
                CommandHandler('commands',commandsa),
                CommandHandler('role',role),
                CommandHandler('set_role', set_role),
                CommandHandler('reset_role', reset_role)
            ],
            WAIT_FOR_USER_MESSAGE: [
                MessageHandler(filters.TEXT, get_user_message)
            ],
        },
        fallbacks=[],
        allow_reentry=True
    )


    application.add_handler(conv_handler)
    application.run_polling()