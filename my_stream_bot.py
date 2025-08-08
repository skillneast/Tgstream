import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask
from threading import Thread

# --- Bot ka code waisa hi hai ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello {user_name}! 👋\n\nMujhe koi bhi video bhejo, main aapko uska direct streamable link dunga."
    )

async def generate_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processing_message = await update.message.reply_text("Video mil gayi hai... Link bana raha hoon, please wait...")
    try:
        video_file_id = update.message.video.file_id
        bot_file = await context.bot.get_file(video_file_id)
        stream_url = bot_file.get_download_url()
        await processing_message.edit_text(
            "Ye raha aapka stream link...\n\n"
            f"`{stream_url}`\n\n"
            "**Warning:** Yeh link sirf ~1 ghante ke liye valid hai.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Error creating link: {e}")
        await processing_message.edit_text("Maaf kijiye, link banane me koi problem aa gayi.")

# --- Yahan naya code shuru hota hai ---

# Ye ek dummy web server hai
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Yahan se bot chalaane ka code ---

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set!")
    else:
        # Dummy server ko chalu rakho
        keep_alive()
        
        # Ab bot ko shuru karo
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        start_handler = CommandHandler('start', start)
        video_handler = MessageHandler(filters.VIDEO, generate_link)
        application.add_handler(start_handler)
        application.add_handler(video_handler)
        print("Bot is running...")
        application.run_polling()
