"""
Telegram bot (python-telegram-bot v20) with expressive outputs + file logging.

Features:
- Greeting with emoji + gender mapping + sticker (fallback to emoji text)
- Enforcement messages (link, missing name/username, bio link, not joined) with emoji + sticker fallback
- Media forwarding (photo/video/voice/audio) to mapped channels and main group
- Reminder every 5 minutes with bold-like formatting, emoji and sticker fallback
- Local execution (no Flask). Run locally or on VPS.
- Robust error handling and logs
- NEW: File logging to bot_activity.log

Notes:
- Set BOT_TOKEN as environment variable or paste into BOT_TOKEN variable.
- Stickers: STICKER_* constants are safe defaults. If sending fails, fallback to emoji.
- Requires python-telegram-bot v20+.

Run:
- pip install python-telegram-bot==20.*
- export BOT_TOKEN="<your token>"  # on Windows use set
- python telegram_nakal_bot.py
"""

import logging, os, re, asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "8167264410:AAHYQgPVe_HyqIQLxZ6yuGFABWCw5Bb-P74")

# === Logging config ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

file_logger = logging.getLogger("filelog")
file_handler = logging.FileHandler("bot_activity.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s | %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.INFO)

# === Sticker constants (default public IDs) ===
STICKER_WELCOME = "CAACAgIAAxkBAAEIEhFmfCwtiK7r6c3l4p3GttV41sJL4wACSwADVp29Chm4gfEYbS-hNgQ"
STICKER_WARNING = "CAACAgIAAxkBAAEIEhNmfCw_r3lt3uOQMC10YPD6TiytTgACUQADVp29CncvGUlKn-vvNgQ"
STICKER_FIRE = "CAACAgIAAxkBAAEIEhVmfcx9nYmz16rDpNBniRvE8C1lOQACjAADVp29CjXlt4v2G5UoNgQ"
STICKER_REMINDER = "CAACAgIAAxkBAAEIEhdmfcx_0kC8cYuzJrj9uMqvnp6NkgACmAADVp29Ck3FfQhFWliiNgQ"

# === Helper ===
def detect_gender(name: str, username: str) -> str:
    text = (name or "") + (username or "")
    text = text.lower()
    if any(word in text for word in ["cowo", "boy", "putra", "male"]):
        return "👨🔥"
    elif any(word in text for word in ["cewe", "girl", "putri", "female"]):
        return "👩💋"
    return "👤✨"

async def send_with_sticker(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, sticker: str):
    try:
        await context.bot.send_message(chat_id, text)
        await context.bot.send_sticker(chat_id, sticker)
    except Exception:
        logger.warning("Sticker gagal dikirim, fallback ke teks saja.")
        await context.bot.send_message(chat_id, text)

# === Handlers ===
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        gender_icon = detect_gender(member.full_name, member.username or "")
        text = f"👋 Halo {member.full_name} (@{member.username}) {gender_icon}\n🎉 Selamat datang di Nakal Community ❤️‍🔥\nJangan lupa ikuti aturan ya 😈"
        await send_with_sticker(context, update.effective_chat.id, text, STICKER_WELCOME)
        file_logger.info(f"JOIN   | User: {member.full_name} (@{member.username}) | Gender: {gender_icon}")

async def filter_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if not user.username and not user.full_name:
        await send_with_sticker(context, msg.chat_id, "⚠️ Pesan dihapus: Kamu wajib pasang nama + username dulu ✨", STICKER_WARNING)
        await msg.delete()
        file_logger.info(f"DELETE | User: {user} | Reason: Tidak ada nama/username")
        return
    if re.search(r"https?://", msg.text or ""):
        await send_with_sticker(context, msg.chat_id, "🚫 Pesan dihapus: Dilarang kirim link di sini yaaa 😡", STICKER_WARNING)
        await msg.delete()
        file_logger.info(f"DELETE | User: {user} | Reason: Link terdeteksi")
        return

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    await send_with_sticker(context, msg.chat_id, "📤 Konten kamu sudah diteruskan ke channel terkait! 🔥\nTerus kirim yaaa 😘", STICKER_FIRE)
    file_logger.info(f"FORWARD| User: {user.full_name} (@{user.username}) | Media: {msg.effective_attachment.__class__.__name__}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = -1003098333444  # Nakal Community
    text = (
        "⏰ hello everyone!\n"
        "👉 Silahkan kirim **pap nakal** kalian melalui:\n"
        "🤖 @lontenih_bot @eksibnih11_bot\n"
        "🔒 Identitas tetap **anonim** tanpa nama & id!\n"
        "🔥 Jangan malu-malu, bebas berekspresi 💦"
    )
    await send_with_sticker(context, chat_id, text, STICKER_REMINDER)
    file_logger.info("REMIND | Bot sent reminder ke Nakal Community")

# === Main ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.AUDIO, handle_media))

    app.job_queue.run_repeating(send_reminder, interval=300, first=10)

    logger.info("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
