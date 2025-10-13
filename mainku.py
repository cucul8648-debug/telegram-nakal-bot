# filename: brutt_inline_webhook.py
# pip install python-telegram-bot==20.3 Flask==2.3.3

import os, logging, asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
)

# ====== CONFIG ======
TOKEN = "8167264410:AAGIXM4p2Si47xtiVYvSitCy5hf7wUP-i-A"
CHANNEL_PAP = "@PAPCABULNABRUTT"
CHANNEL_MOAN = "@MOAN18NABRUTT"
CHANNEL_MENFESS = "@MenfessNABRUTT"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== DATA USER ======
user_sessions = {}

# ====== FORMAT BRUTT ======
def format_brutt(topik: str, gender: str, caption: str) -> str:
    gender_emoji = "👩‍🦰" if gender.lower() == "cewe" else "🧑‍🦱"
    hashtag = "#CEWE" if gender.lower() == "cewe" else "#COWO"
    emoji_map = {"papbrutt":"📸", "videobrutt":"🎥", "moanbrutt":"🎧", "menfessbrutt":"💌"}
    emoji_topik = emoji_map.get(topik.lower(),"💬")
    return (
        f"**{topik.upper()} {emoji_topik}**\n\n"
        f"> **GENDER 🕵️ : {gender.upper()} {gender_emoji}**\n\n"
        f"{caption.strip()}\n\n"
        f"> **BERIKAN REACT DAN NILAI!**\n"
        f"> **⭐ RATE 1–10**\n"
        f"> **💬 COMMENT!**\n\n"
        f"{hashtag}"
    )

# ====== START ======
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard_gender = [
        [InlineKeyboardButton("👨 Cowok", callback_data="gender_cowo"),
         InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu ya:",
        reply_markup=InlineKeyboardMarkup(keyboard_gender)
    )

# ====== PILIH GENDER ======
async def pilih_gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    gender = q.data.replace("gender_", "")
    user_sessions[q.from_user.id] = {"gender": gender}

    keyboard_jenis = [
        [InlineKeyboardButton("💌 MenfessBrutt", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 PapBrutt", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎥 VideoBrutt", callback_data="jenis_video")],
        [InlineKeyboardButton("🎧 MoanBrutt", callback_data="jenis_moan")]
    ]
    await q.edit_message_text(
        f"Gender kamu: {gender.upper()} ✅\n\nPilih jenis postingan:",
        reply_markup=InlineKeyboardMarkup(keyboard_jenis)
    )

# ====== PILIH JENIS ======
async def pilih_jenis_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    jenis_raw = q.data.replace("jenis_", "")
    if q.from_user.id not in user_sessions:
        user_sessions[q.from_user.id] = {}
    if jenis_raw == "video":
        user_sessions[q.from_user.id]["jenis"] = "videobrutt"
    elif jenis_raw == "pap":
        user_sessions[q.from_user.id]["jenis"] = "papbrutt"
    elif jenis_raw == "moan":
        user_sessions[q.from_user.id]["jenis"] = "moanbrutt"
    else:
        user_sessions[q.from_user.id]["jenis"] = "menfessbrutt"
    await q.edit_message_text("Silakan kirim caption (teks). Untuk PAP/VIDEO/MOAN, setelah caption kirim media.")

# ====== HANDLE MESSAGE ======
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_sessions or "jenis" not in user_sessions[uid] or "gender" not in user_sessions[uid]:
        return await update.message.reply_text("Ketik /start dulu untuk mulai.")
    
    sesi = user_sessions[uid]
    jenis = sesi["jenis"]
    gender = sesi["gender"]
    caption_text = update.message.caption if update.message.caption else (update.message.text or "")

    pending_caption = sesi.get("pending_caption", "")
    if caption_text and not any([update.message.photo, update.message.video, update.message.voice, update.message.audio]) and jenis != "menfessbrutt":
        sesi["pending_caption"] = caption_text
        sesi["awaiting_media"] = True
        return await update.message.reply_text("📎 Caption diterima. Sekarang kirim medianya (foto/video/voice).")

    # MENFESS
    if jenis == "menfessbrutt":
        formatted = format_brutt("MENFESSBRUTT", gender, caption_text or "Tanpa caption")
        try:
            await context.bot.send_message(chat_id=CHANNEL_MENFESS, text=formatted, parse_mode="Markdown")
        except:
            return await update.message.reply_text("❌ Gagal kirim MENFESS ke channel.")
        user_sessions.pop(uid, None)
        return await send_confirmation(update, context)

    # Media posting (PAP/VIDEO/MOAN)
    try:
        caption_final = (update.message.caption or pending_caption or "Tanpa caption")
        if jenis == "papbrutt" and update.message.photo:
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(CHANNEL_PAP, photo=file_id, caption=format_brutt("PAPBRUTT", gender, caption_final), parse_mode="Markdown", has_spoiler=True)
        elif jenis == "videobrutt" and update.message.video:
            file_id = update.message.video.file_id
            await context.bot.send_video(CHANNEL_PAP, video=file_id, caption=format_brutt("VIDEOBRUTT", gender, caption_final), parse_mode="Markdown", has_spoiler=True)
        elif jenis == "moanbrutt":
            if update.message.voice:
                file_id = update.message.voice.file_id
                await context.bot.send_voice(CHANNEL_MOAN, voice=file_id, caption=format_brutt("MOANBRUTT", gender, caption_final))
            elif update.message.audio:
                file_id = update.message.audio.file_id
                await context.bot.send_audio(CHANNEL_MOAN, audio=file_id, caption=format_brutt("MOANBRUTT", gender, caption_final))
            elif update.message.video:
                file_id = update.message.video.file_id
                await context.bot.send_video(CHANNEL_MOAN, video=file_id, caption=format_brutt("MOANBRUTT", gender, caption_final), parse_mode="Markdown", has_spoiler=True)
            else:
                return await update.message.reply_text("❌ Kirim voice/audio untuk MOANBRUTT.")
        else:
            return await update.message.reply_text("❌ Media tidak valid untuk jenis ini.")
    except Exception as e:
        logger.error(e)
        return await update.message.reply_text("❌ Gagal kirim ke channel.")

    user_sessions.pop(uid, None)
    return await send_confirmation(update, context)

# ====== KIRIM KONFIRMASI ======
async def send_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard_again = [
        [InlineKeyboardButton("💌 MenfessBrutt", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 PapBrutt", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎥 VideoBrutt", callback_data="jenis_video")],
        [InlineKeyboardButton("🎧 MoanBrutt", callback_data="jenis_moan")]
    ]
    await update.message.reply_text(
        "✅ Postingan berhasil dikirim!\n\nMau kirim apa lagi?",
        reply_markup=InlineKeyboardMarkup(keyboard_again)
    )

# ====== FLASK APP ======
flask_app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start_handler))
bot_app.add_handler(CallbackQueryHandler(pilih_gender_callback, pattern="^gender_"))
bot_app.add_handler(CallbackQueryHandler(pilih_jenis_callback, pattern="^jenis_"))
bot_app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run_coroutine_threadsafe(bot_app.process_update(update), asyncio.get_event_loop())
    return "ok"

@flask_app.route("/")
def index():
    return "BRUTT Inline Bot Webhook Running!"

# ====== SET WEBHOOK ======
async def set_webhook():
    url = os.environ.get("WEBHOOK_URL")  # Contoh: https://yourdomain.com/<TOKEN>
    if not url:
        logger.error("WEBHOOK_URL belum di set di environment variables!")
        return
    webhook_url = f"{url}/{TOKEN}"
    await bot_app.bot.set_webhook(webhook_url)
    logger.info(f"Webhook terpasang: {webhook_url}")

if __name__ == "__main__":
    # run webhook
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
