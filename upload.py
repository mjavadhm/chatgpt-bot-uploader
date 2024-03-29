import asyncio
import telegram
import openai
import logging
from telegram import Update, InlineQueryResultArticle , InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler, CallbackContext, ConversationHandler 

user_chat_history = {}
user_chat_setting = {}
alluser = ['admin','javad','Javad','Admin']
allpass = ['1234','0150','Admin']
fnum = 0
USERNAME, PASSWORD, CONVERSATION, WAIT_FOR_USER_MESSAGE, UPLOAD = range(5)



openai.api_key = '*****'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    user_id = update.effective_user.id
    if user_id not in user_chat_history:
        user_chat_setting[user_id] = "you are a Telegram bot designed to assist users in solving problems. You are helpful."
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("Ask me anything or use /about")
    return CONVERSATION

async def login(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("Enter your username")
    return USERNAME

async def about(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text('Another chatgpt bot but! youcan choose role and save your files\nlist of the commands in /commands\nGithub link : https://github.com/mjavadhm/juploadbot/')

async def commandsa(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("/start ---> Login\n/clear_history ---> Start new chat(clear history)\n/upload ---> Upload files\n/set_role ---> set bot role\n/reset_role ---> default setting for bot\n/about ---> More information about Bot")

async def username(update, context):
    global usern
    usern = update.message.text
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text('And now password')
    return PASSWORD

async def password(update, context):
    global passn
    passn = update.message.text
    if usern in alluser and passn in allpass:
        await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
        await update.message.reply_text('Logged in succesfully!🤝\nAsk me anything you want or just send me a file(use /about for more information)')
        return UPLOAD
    else:
        await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
        await update.message.reply_text('💩Access denied!💩')
        return CONVERSATION

async def role(update, context):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text(f'bot role is : {user_chat_setting[user_id]}')

async def set_role(update, context):
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text('Enter bot role:')
    return WAIT_FOR_USER_MESSAGE

async def get_user_message(update, context):
    user_id = update.effective_user.id
    user_chat_setting[user_id] = update.message.text
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text(f'Your bot role is: \'{user_chat_setting[user_id]}\'')
    return CONVERSATION

async def reset_role(update, context):
    user_id = update.effective_user.id
    user_chat_setting[user_id] = "you are a Telegram bot designed to assist users in solving problems. You are helpful."
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text(f'Done')

async def reply_to_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    user_id = update.effective_user.id

    if user_id not in user_chat_history:
        user_chat_history[user_id] = []

    user_chat_history[user_id].append({"role": "user", "content": user_input})
    
    generating_response_message = await update.message.reply_text("Generating response...")
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "system", "content": user_chat_setting[user_id]}, *user_chat_history[user_id]],
            n=1,
            stop=None
        )

        response_text = response.choices[0].message['content']
        max_message_length = 4096
        message_parts = [response_text[i:i + max_message_length] for i in range(0, len(response_text), max_message_length)]

        for part in message_parts:
            await context.bot.send_message(chat_id=update.message.chat_id, text=part, parse_mode='Markdown')


    finally:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=generating_response_message.message_id)

async def clear_history(update, context):
    user_id = update.effective_user.id
    user_chat_history[user_id] = []
    await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
    await update.message.reply_text("Chat history cleared.")


async def uploader(update: Update, context ):
    global fnum
    if update.message.video:

        await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
        video_file = await context.bot.get_file(update.message.video.file_id)
        video_path = f'/var/www/html/telegram/{update.message.video.file_name}{fnum}.mp4'
        fnum = fnum+1
        await video_file.download_to_drive(video_path)
        await update.message.reply_text(f'Video {update.message.video.file_name} downloaded to {video_path}')
        return CONVERSATION
    
    elif update.message.document:
    
        await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f'/var/www/html/telegram/{update.message.document.file_name}'
        await file.download_to_drive(file_path)
        await update.message.reply_text(f'File {update.message.document.file_name} downloaded to {file_path}')
        return CONVERSATION
    
    else:
    
        await context.bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.constants.ChatAction.TYPING)
        await update.message.reply_text('Unsupported file type.')
        return CONVERSATION

        
if __name__ == '__main__':
    application = ApplicationBuilder().token('*****').build()
    
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
                CommandHandler('upload',login),
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
            UPLOAD: [
                MessageHandler(filters.Document.ALL | filters.VIDEO | filters.ALL, uploader)
            ],
        },
        fallbacks=[],
        allow_reentry=True
    )


    application.add_handler(conv_handler)
    application.run_polling()