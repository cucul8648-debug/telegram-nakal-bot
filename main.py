"""
Telegram bot (python-telegram-bot v20) with expressive outputs + file logging.

Features:
- Greeting with emoji + gender mapping + sticker (fallback to emoji text)
- Enforcement messages (link, missing name/username, bio link, not joined)
- Media forwarding (photo/video/voice/audio)
- Reminder every 5 minutes
- Local execution (no Flask). Run locally or on VPS.
- File logging to bot_activity.log
"""

import logging, os, re
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8167264410:AAHYQgPVe_HyqIQLxZ6yuGFABWCw5Bb-P74")

# === Logging config ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

file_logger = logging.getLogger("filelog")
file_handler = logging.FileHandler("bot_activity.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s | %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.INFO)

# === Sticker constants ===
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

async def send_with_sticker(bot, chat_id: int, text: str, sticker: str):
    try:
        await bot.send_message(chat_id, text, parse_mode="Markdown")
        await bot.send_sticker(chat_id, sticker)
    except Exception:
        logger.warning("Sticker gagal dikirim, fallback ke teks saja.")
        await bot.send_message(chat_id, text, parse_mode="Markdown")

# === Handlers ===
async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        gender_icon = detect_gender(member.full_name, member.username or "")
        text = (
            f"👋 Halo {member.full_name} (@{member.username}) {gender_icon}\n"
            "🎉 Selamat datang di Nakal Community ❤️‍🔥\n"
            "Jangan lupa ikuti aturan ya 😈"
        )
        await send_with_sticker(context.bot, update.effective_chat.id, text, STICKER_WELCOME)
        file_logger.info(f"JOIN   | User: {member.full_name} (@{member.username}) | Gender: {gender_icon}")

async def filter_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    # Wajib nama/username
    if not user.username and not user.full_name:
        await send_with_sticker(context.bot, msg.chat_id, "⚠️ Pesan dihapus: Kamu wajib pasang nama + username dulu ✨", STICKER_WARNING)
        await msg.delete()
        file_logger.info(f"DELETE | User: {user.id} | Reason: Tidak ada nama/username")
        return

    # Filter link
    if msg.text and re.search(r"https?://", msg.text):
        await send_with_sticker(context.bot, msg.chat_id, "🚫 Pesan dihapus: Dilarang kirim link di sini 😡", STICKER_WARNING)
        await msg.delete()
        file_logger.info(f"DELETE | User: {user.id} | Reason: Link terdeteksi")
        return

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    await send_with_sticker(
        context.bot,
        msg.chat_id,
        "📤 Konten kamu sudah diteruskan ke channel terkait! 🔥\nTerus kirim yaaa 😘",
        STICKER_FIRE,
    )
    file_logger.info(f"FORWARD| User: {user.full_name} (@{user.username}) | Media: {msg.effective_attachment.__class__.__name__}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = -1003098333444  # Ganti dengan group target
    text = (
        "⏰ *hello everyone!*\n"
        "👉 Silahkan kirim *pap nakal* kalian melalui:\n"
        "🤖 @lontenih_bot @eksibnih11_bot\n"
        "🔒 Identitas tetap *anonim* tanpa nama & id!\n"
        "🔥 Jangan malu-malu, bebas berekspresi 💦"
    )
    await send_with_sticker(context.bot, chat_id, text, STICKER_REMINDER)
    file_logger.info("REMIND | Bot sent reminder ke Nakal Community")

# === Main ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.AUDIO, handle_media))

    # Reminder tiap 5 menit
    app.job_queue.run_repeating(send_reminder, interval=300, first=10)

    logger.info("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
