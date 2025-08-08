import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- Zaroori Cheezein ---
# Token ko Render ke Environment Variable se lega
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ek chhota web server banana (Flask ka use karke)
# Ye Render ko 'zinda' hone ka signal dega
app = Flask('')

@app.route('/')
def home():
    """Ye page bas 'I am alive' message dikhayega"""
    return "Bot is alive and running!"

def run_flask():
  """Flask server ko chalane ke liye function"""
  # Render, port ko 'PORT' environment variable me set karta hai. Hum usi ka istemaal karenge.
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Ek alag thread me Flask server ko chalana"""
    t = Thread(target=run_flask)
    t.start()

# --- Bot ka Logic (Pehle jaisa hi) ---
# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello {user_name}! 👋\n\nMain ek Video Stream Link Generator Bot hoon.\n"
             "Aap mujhe koi bhi video bhejein, main aapko uska direct streamable link dunga."
    )

async def generate_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processing_message = await update.message.reply_text(
        "✅ Video mil gayi hai...\n"
        "🔗 Link bana raha hoon, please wait..."
    )
    try:
        video_file_id = update.message.video.file_id
        bot_file = await context.bot.get_file(video_file_id)
        stream_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{bot_file.file_path}"
        await processing_message.edit_text(
            "🎉 Ye raha aapka stream link:\n\n"
            f"`{stream_url}`\n\n"
            "**Note:**\n"
            "1. Isko copy karke VLC/MX Player jaise player me chalaayein.\n"
            "2. Yeh link sirf ~1 ghante ke liye valid hai.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Error creating link: {e}")
        await processing_message.edit_text("❌ Maaf kijiye, link banane me koi problem aa gayi.")

# --- Bot ko Shuru Karne ka Main Hissa ---
if __name__ == '__main__':
    if not BOT_TOKEN:
        print("CRITICAL ERROR: BOT_TOKEN environment variable not set!")
    else:
        # 1. Sabse pehle, dummy web server ko background me chalu karo
        keep_alive()
        
        # 2. Ab bot ko shuru karo
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        start_handler = CommandHandler('start', start)
        video_handler = MessageHandler(filters.VIDEO, generate_link)
        application.add_handler(start_handler)
        application.add_handler(video_handler)
        
        print("Bot is running...")
        application.run_polling()
