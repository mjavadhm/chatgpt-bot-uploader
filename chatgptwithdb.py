import asyncio
import telegram
import openai
import logging
import sqlite3
from datetime import datetime
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackContext, ConversationHandler

# Initialize database connection and create tables
conn = sqlite3.connect('telegram_bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TEXT,
        role TEXT,
        message TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
''')

# Initialize user settings and other global variables
user_chat_setting = {}
USERNAME, PASSWORD, CONVERSATION, WAIT_FOR_USER_MESSAGE, UPLOAD = range(5)

openai.api_key = 'aa-9qPdX1kXoq7cpvwEHuxlOzak3ZWXOnGsciFpWk2GuU3MRnf9'
openai.api_base = 'https://api.avalai.ir/v1'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Define functions for various bot commands
async def start(update, context):
    user = update.effective_user
    user_id = user.id
    name = user.first_name
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, name))
    conn.commit()
    if user_id not in user_chat_setting:
        user_chat_setting[user_id] = "you are a Telegram bot designed to assist users in solving problems. You are helpful."
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("Ask me anything or use /about")
    return CONVERSATION

async def login(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("Enter your username")
    return USERNAME

async def about(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text('Another chatgpt bot but! you can choose role and save your files\nlist of the commands in /commands\nGithub link : https://github.com/mjavadhm/juploadbot/')

async def commandsa(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("/start ---> Login\n/clear_history ---> Start new chat(clear history)\n/upload ---> Upload files\n/set_role ---> set bot role\n/reset_role ---> default setting for bot\n/about ---> More information about Bot")

async def username(update, context):
    global usern
    usern = update.message.text
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text('And now password')
    return PASSWORD

async def password(update, context):
    global passn
    passn = update.message.text
    user_id = update.effective_user.id
    if usern in alluser and passn in allpass:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, usern))
        conn.commit()
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
        await update.message.reply_text('Logged in successfully!🤝\nAsk me anything you want or just send me a file(use /about for more information)')
        return UPLOAD
    else:
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
        await update.message.reply_text('💩Access denied!💩')
        return CONVERSATION

async def role(update, context):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text(f'bot role is : {user_chat_setting[user_id]}')

async def set_role(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text('Enter bot role:')
    return WAIT_FOR_USER_MESSAGE

async def get_user_message(update, context):
    user_id = update.effective_user.id
    user_chat_setting[user_id] = update.message.text
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text(f'Your bot role is: \'{user_chat_setting[user_id]}\'')
    return CONVERSATION

async def reset_role(update, context):
    user_id = update.effective_user.id
    user_chat_setting[user_id] = "you are a Telegram bot designed to assist users in solving problems. You are helpful."
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text(f'Done')

def get_chat_history(user_id):
    cursor.execute("SELECT role, message FROM chat_history WHERE user_id=? ORDER BY timestamp", (user_id,))
    return cursor.fetchall()

async def reply_to_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.effective_user.id

    cursor.execute("INSERT INTO chat_history (user_id, timestamp, role, message) VALUES (?, ?, ?, ?)",
                   (user_id, datetime.now(), "user", user_input))
    conn.commit()

    generating_response_message = await update.message.reply_text("Generating response...")
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)

    try:
        chat_history = get_chat_history(user_id)
        messages = [{"role": "system", "content": user_chat_setting[user_id]}]
        for role, message in chat_history:
            messages.append({"role": role, "content": message})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            n=1,
            stop=None
        )

        response_text = response.choices[0].message['content']
        cursor.execute("INSERT INTO chat_history (user_id, timestamp, role, message) VALUES (?, ?, ?, ?)",
                       (user_id, datetime.now(), "assistant", response_text))
        conn.commit()

        max_message_length = 4096
        message_parts = [response_text[i:i + max_message_length] for i in range(0, len(response_text), max_message_length)]

        for part in message_parts:
            await context.bot.send_message(chat_id=update.message.chat_id, text=part, parse_mode='Markdown')

    finally:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=generating_response_message.message_id)

async def clear_history(update, context):
    user_id = update.effective_user.id
    cursor.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
    conn.commit()
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("Chat history cleared.")

async def uploader(update: Update, context):
    global fnum
    user_id = update.effective_user.id
    if update.message.video:
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
        video_file = await context.bot.get_file(update.message.video.file_id)
        video_path = f'/var/www/html/telegram/{update.message.video.file_name}{fnum}.mp4'
        fnum += 1
        await video_file.download_to_drive(video_path)
        await update.message.reply_text(f'Video {update.message.video.file_name} downloaded to {video_path}')
        return CONVERSATION
    elif update.message.document:
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f'/var/www/html/telegram/{update.message.document.file_name}'
        await file.download_to_drive(file_path)
        await update.message.reply_text(f'File {update.message.document.file_name} downloaded to {file_path}')
        return CONVERSATION
    else:
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.constants.ChatAction.TYPING)
        await update.message.reply_text('Unsupported file type.')
        return CONVERSATION

async def restartmessage(context):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    restart_message = "The bot has been restarted. Please use /start to restart the bot."
    for user in users:
        try:
            await context.bot.send_message(chat_id=user[0], text=restart_message)
        except Exception as e:
            logging.error(f"Error sending restart message to user {user[0]}: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token('6803449290:AAHU-0V179di9czKWZ1rxP1_jOJsn0eLh30').build()
    application.job_queue.run_once(restartmessage, when=0)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, username)
            ],
            PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, password)
            ],
            CONVERSATION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_message),
                CommandHandler('upload', login),
                CommandHandler('clear_history', clear_history),
                CommandHandler('about', about),
                CommandHandler('commands', commandsa),
                CommandHandler('role', role),
                CommandHandler('set_role', set_role),
                CommandHandler('reset_role', reset_role)
            ],
            WAIT_FOR_USER_MESSAGE: [
                MessageHandler(filters.TEXT, get_user_message)
            ],
            UPLOAD: [
                MessageHandler(filters.Document.ALL | filters.VIDEO | filters.ALL, uploader)
            ],
        },
        fallbacks=[],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.run_polling()
