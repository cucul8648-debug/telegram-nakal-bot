# filename: nabrutt_auto_post_anon_comment.py
# pip install python-telegram-bot==20.3 Flask==2.3.3

import os, logging, asyncio, threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ========== KONFIGURASI ==========
TOKEN = "8167264410:AAHjVNwOT5RuZVLZ2pK8IP0d4-YR0cArlnc"
CHANNEL_ID = "@PAPCABULNABRUTT"  # Channel harus sudah terhubung ke grup diskusi

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== INISIALISASI FLASK ==========
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# ========== HANDLER / COMMAND ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kirim jenis konten (PAPBRUTT 📸, VIDEOBRUTT 🎥, MOANBRUTT 🎧, atau MENFESSBRUTT 💌).")

# ========== FUNGSI KIRIM OTOMATIS ==========
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.caption or update.message.text or "").upper()

    if "PAPBRUTT" in text:
        topic = "PAPBRUTT 📸"
    elif "VIDEOBRUTT" in text:
        topic = "VIDEOBRUTT 🎥"
    elif "MOANBRUTT" in text:
        topic = "MOANBRUTT 🎧"
    elif "MENFESSBRUTT" in text:
        topic = "MENFESSBRUTT 💌"
    else:
        return await update.message.reply_text("❌ Jenis tidak dikenali. Ketik PAPBRUTT / VIDEOBRUTT / MOANBRUTT / MENFESSBRUTT.")

    # GENDER (opsional, ambil dari teks user)
    gender = "COWO 👦" if "COWO" in text else "CEWE 👩‍🦰" if "CEWE" in text else "TIDAK DISEBUTKAN"

    # Caption posting
    caption_final = (
        f"**{topic}**\n\n"
        f"> **GENDER 🕵️ :** {gender}\n\n"
        f"{update.message.caption or 'Tanpa caption'}\n\n"
        f"> **BERIKAN REACT DAN NILAI!**\n"
        f"> **⭐ RATE 1–10**\n"
        f"> **💬 COMMENT**\n\n"
        f"#{gender.split()[0].upper()}"
    )

    # Kirim ke channel (anonim)
    if update.message.photo:
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption_final,
            parse_mode="Markdown"
        )
    elif update.message.video:
        await context.bot.send_video(
            chat_id=CHANNEL_ID,
            video=update.message.video.file_id,
            caption=caption_final,
            parse_mode="Markdown"
        )
    elif update.message.voice or update.message.audio:
        await context.bot.send_audio(
            chat_id=CHANNEL_ID,
            audio=(update.message.voice or update.message.audio).file_id,
            caption=caption_final,
            parse_mode="Markdown"
        )
    elif "MENFESSBRUTT" in text:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption_final,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Format tidak valid atau media tidak ditemukan.")

    await update.message.reply_text("✅ Posting terkirim ke channel secara anonim!")

# ========== DAFTAR HANDLER ==========
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_media))

# ========== FLASK WEBHOOK ==========
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    application.run_polling()
