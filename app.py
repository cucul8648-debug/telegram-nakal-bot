import os
import logging
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# =======================
# KONFIGURASI
# =======================
BOT_TOKEN = os.getenv("8490098646:AAGI4qerdpRxuNLeNblgMN3fTxrniIsNvYo")  # dari Environment Variable di Render
TARGET_CHAT_ID = -1003098333444     # ganti dengan chat_id grup/kanal kamu

# =======================
# LOGGING
# =======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot_activity.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# =======================
# FLASK KEEP ALIVE
# =======================
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running fine!", 200

# =======================
# HANDLER BOT
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Halo! Bot ini aktif dan siap jalan.")

async def forward_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    log_text = f"[{user.id}] {user.first_name} ({user.username}) : {msg.text or 'media'}"
    logger.info(log_text)

    await msg.forward(chat_id=TARGET_CHAT_ID)

# Reminder tiap 5 menit
async def reminder_task(app: Application):
    while True:
        try:
            await app.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text="⏰ Hello everyone!\nSilahkan kirim pap nakal kalian melalui:\n👉 @lontenih_bot\n👉 @eksibnih11_bot\n\nIdentitas aman (anonim, tanpa nama & ID).",
            )
        except Exception as e:
            logger.error(f"Reminder error: {e}")
        await asyncio.sleep(300)  # 5 menit

# =======================
# MAIN
# =======================
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command
    application.add_handler(CommandHandler("start", start))

    # Semua pesan user -> forward
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    # Jalankan reminder background
    application.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text="⏰ Hello everyone!\nSilahkan kirim pap nakal kalian melalui:\n👉 @lontenih_bot\n👉 @eksibnih11_bot\n\nIdentitas aman (anonim, tanpa nama & ID).",
        ),
        interval=300,
        first=10,
    )

    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
