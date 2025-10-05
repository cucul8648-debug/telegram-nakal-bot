# filename: nabrutt_welcome_autoaccept_final.py
# install dulu: pip install python-telegram-bot==20.3

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler,
    ChatJoinRequestHandler, ContextTypes, filters
)

# ========== KONFIGURASI ==========
TOKEN = "8490098646:AAGI4qerdpRxuNLeNblgMN3fTxrniIsNvYo"

LINKS = [
    ("🔥 GC 𝙉𝘼𝘽𝙍𝙐𝙏𝙏", "https://t.me/nabrutt11"),
    ("💌 CH 𝙈𝙀𝙉𝙁𝙀𝙎𝙎", "https://t.me/MenfessNabrutt"),
    ("📸 CH 𝙋𝘼𝙋𝘽𝙍𝙐𝙏𝙏", "https://t.me/papcabulnabrutt"),
    ("🔞 CH 𝙈𝙊𝘼𝙉", "https://t.me/Moan18Nabrutt"),
]

AUTO_DELETE_SECONDS = 30
TIMEZONE = ZoneInfo("Asia/Jakarta")
# =================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# === Helper bikin tombol ===
def build_links_keyboard():
    keyboard = []
    for title, url in LINKS:
        keyboard.append([InlineKeyboardButton(text=title, url=url)])
    return InlineKeyboardMarkup(keyboard)


# === Helper hapus otomatis ===
async def auto_delete_message(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data.get("chat_id")
    message_id = context.job.data.get("message_id")

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"🧹 Pesan {message_id} dihapus otomatis.")
    except Exception as e:
        logger.warning(f"Gagal hapus pesan {message_id}: {e}")


# === Handler: auto-accept join request ===
async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user

    # Auto-approve join request
    await context.bot.approve_chat_join_request(chat_id=request.chat.id, user_id=user.id)
    logger.info(f"✅ Diterima join request dari: {user.full_name} ({user.id})")

    # Kirim pesan welcome ke grup
    who = f"@{user.username}" if user.username else user.full_name or "Anon Brutall"
    joined_at = datetime.now(TIMEZONE).strftime("%d %B %Y, %H:%M:%S")

    text = (
        "🌟 <b>SELAMAT DATANG DI 𝙉𝘼𝘽𝙍𝙐𝙏𝙏</b> 🌟\n\n"
        "━━━━━━━━━━━━━━\n"
        f"👤 <b>Nama:</b> {who}\n"
        f"🕒 <b>Waktu Join:</b> <i>{joined_at}</i>\n"
        f"💥 <b>Status:</b> <u>Masuk via permintaan join (auto diterima bot)</u>\n"
        "━━━━━━━━━━━━━━\n\n"
        "⚡ <b>Nakal & Brutall Zone</b> 🤖\n"
        "📌 Silakan akses semua area melalui tombol di bawah 👇\n\n"
        "✨ Nikmati pengalaman seru & jangan lupa bersenang-senang!"
    )

    try:
        sent = await context.bot.send_message(
            chat_id=request.chat.id,
            text=text,
            parse_mode="HTML",
            reply_markup=build_links_keyboard(),
        )

        # Jadwalkan penghapusan otomatis
        context.job_queue.run_once(
            auto_delete_message,
            AUTO_DELETE_SECONDS,
            data={"chat_id": sent.chat_id, "message_id": sent.message_id},
        )

    except Exception as e:
        logger.exception("❌ Error kirim pesan join autoaccept: %s", e)


# === Handler user join biasa (tanpa request) ===
async def new_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.new_chat_members:
        return

    for member in msg.new_chat_members:
        who = f"@{member.username}" if member.username else member.full_name or "Anon Brutall"
        joined_at = datetime.now(TIMEZONE).strftime("%d %B %Y, %H:%M:%S")

        text = (
            "🌟 <b>SELAMAT DATANG DI 𝙉𝘼𝘽𝙍𝙐𝙏𝙏</b> 🌟\n\n"
            "━━━━━━━━━━━━━━\n"
            f"👤 <b>Nama:</b> {who}\n"
            f"🕒 <b>Waktu Join:</b> <i>{joined_at}</i>\n"
            f"💥 <b>Status:</b> <u>Masuk via tautan General Bot</u>\n"
            "━━━━━━━━━━━━━━\n\n"
            "⚡ <b>Nakal & Brutall Zone</b> 🤖\n"
            "📌 Silakan akses semua area melalui tombol di bawah 👇\n\n"
            "✨ Nikmati pengalaman seru & jangan lupa bersenang-senang!"
        )

        try:
            sent = await msg.reply_html(
                text=text,
                reply_markup=build_links_keyboard(),
                quote=False,
            )
            logger.info("📢 Member baru: %s", who)

            # jadwalkan penghapusan otomatis
            context.job_queue.run_once(
                auto_delete_message,
                AUTO_DELETE_SECONDS,
                data={"chat_id": sent.chat_id, "message_id": sent.message_id},
            )

            # hapus pesan default join juga
            context.job_queue.run_once(
                auto_delete_message,
                AUTO_DELETE_SECONDS,
                data={"chat_id": msg.chat_id, "message_id": msg.message_id},
            )

        except Exception as e:
            logger.exception("❌ Error kirim pesan join: %s", e)


# === Command /start ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "🤖 <b>𝙉𝘼𝘽𝙍𝙐𝙏𝙏 Welcome Bot</b> aktif!\n"
        "Saya akan:\n"
        "1️⃣ Menerima otomatis permintaan join grup\n"
        "2️⃣ Kirim pesan sambutan bergaya <b>Nakal & Brutall</b>\n"
        "3️⃣ Auto hapus pesan setelah <b>30 detik</b>."
    )


# === MAIN ===
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_members_handler))
    app.add_handler(ChatJoinRequestHandler(join_request_handler))

    logger.info("🔥 NABRUTT WELCOME AUTO-ACCEPT BOT SIAP 🔥")
    app.run_polling(allowed_updates=["message", "chat_join_request"])


if __name__ == "__main__":
    main()
