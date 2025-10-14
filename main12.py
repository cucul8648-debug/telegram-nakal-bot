# main.py
# requirements (example): python-telegram-bot==20.3 Flask==3.0.3 python-dotenv==1.0.1
# Deploy notes:
# - Set environment variables: BOT_TOKEN, WEBHOOK_URL (e.g. https://your-app.onrender.com), PORT (optional)
# - Make bot admin in target group/channel if you want membership checks to work.

import os
import logging
import asyncio
from html import escape as html_escape
from flask import Flask, request, abort
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8466148433:AAHyMyVisRnEIaiGg6Fm7Oh6H-fDB0lYJfk")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://telegram-nakal-bot.onrender.com").rstrip("/")
PORT = int(os.environ.get("PORT", 10000))

# Group + thread IDs (replace if different)
GROUP_NABRUTT = int(os.environ.get("GROUP_NABRUTT", -1003098333444))
THREAD_MENFESS = int(os.environ.get("THREAD_MENFESS", 1036))
THREAD_PAP     = int(os.environ.get("THREAD_PAP", 393))
THREAD_MOAN    = int(os.environ.get("THREAD_MOAN", 2298))

# Channel IDs
CHANNEL_MENFESS_ID = int(os.environ.get("CHANNEL_MENFESS_ID", -1002989043936))
CHANNEL_PAP_ID     = int(os.environ.get("CHANNEL_PAP_ID", -1003189592682))
CHANNEL_MOAN_ID    = int(os.environ.get("CHANNEL_MOAN_ID", -1003196180758))

# Channel usernames (for mention links in thread)
CH_USERNAME = {
    "MENFESS": os.environ.get("CH_MENFESS_USERNAME", "@MenfessNABRUTT"),
    "PAP":     os.environ.get("CH_PAP_USERNAME", "@PAPCABULNABRUTT"),
    "MOAN":    os.environ.get("CH_MOAN_USERNAME", "@MOAN18NABRUTT")
}

# Header images (GitHub RAW)
IMG_PAP_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MENFESS_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_MOAN_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MOAN_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"

# Join links (fallback if membership check can't be performed)
URL_NABRUTT    = os.environ.get("URL_NABRUTT", "https://t.me/NABRUTT11")
URL_GC_MENFESS = os.environ.get("URL_GC_MENFESS", "https://t.me/MenfessNABRUTT")
URL_GC_PAP     = os.environ.get("URL_GC_PAP", "https://t.me/PAPCABULNABRUTT")
URL_GC_MOAN    = os.environ.get("URL_GC_MOAN", "https://t.me/MOAN18NABRUTT")

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---------------- APP & BOT ----------------
flask_app = Flask(__name__)

# We'll instantiate Application later (after BOT_TOKEN check)
application = None

# ---------------- Helpers ----------------
def start_keyboard():
    # vertical buttons (one per row)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess")],
        [InlineKeyboardButton("📸 PapBRUTT",    callback_data="post_pap")],
        [InlineKeyboardButton("🎧 MoanBRUTT",   callback_data="post_moan")]
    ])

def gender_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ])

def pap_type_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📷 Foto", callback_data="pap_foto")],
        [InlineKeyboardButton("🎥 Video", callback_data="pap_video")]
    ])

def retry_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess")],
        [InlineKeyboardButton("📸 PapBRUTT",    callback_data="post_pap")],
        [InlineKeyboardButton("🎧 MoanBRUTT",   callback_data="post_moan")],
        [InlineKeyboardButton("📩 Kirim Lagi", callback_data="repost_last")]
    ])

async def check_all_membership(bot: Bot, uid: int):
    # return list of urls not joined (empty => all joined)
    checks = [
        (GROUP_NABRUTT, URL_NABRUTT),
        (CHANNEL_MENFESS_ID, URL_GC_MENFESS),
        (CHANNEL_PAP_ID, URL_GC_PAP),
        (CHANNEL_MOAN_ID, URL_GC_MOAN)
    ]
    not_joined = []
    for cid, url in checks:
        try:
            mem = await bot.get_chat_member(cid, uid)
            if mem.status not in ["member", "administrator", "creator"]:
                not_joined.append(url)
        except Exception:
            # bot may not have permission, fallback ask to join
            not_joined.append(url)
    return not_joined

def emoji_for(topic_key, pap_type=None):
    if topic_key == "MENFESS": return "💌"
    if topic_key == "PAP": return "📸" if pap_type == "pap_foto" else "🎥"
    if topic_key == "MOAN": return "🎧"
    return ""

def title_for(topic_key, pap_type=None):
    if topic_key == "MENFESS": return "MENFESSBRUTT"
    if topic_key == "PAP": return "PAPBRUTT" if pap_type == "pap_foto" else "VIDEOBRUTT"
    if topic_key == "MOAN": return "MOANBRUTT"
    return topic_key

def header_image_url(topic_key, gender, pap_type=None):
    if topic_key == "MENFESS": return IMG_MENFESS_COWO if gender == "COWO" else IMG_MENFESS_CEWE
    if topic_key == "PAP":
        if pap_type == "pap_video": return IMG_VIDEO_COWO if gender == "COWO" else IMG_VIDEO_CEWE
        return IMG_PAP_COWO if gender == "COWO" else IMG_PAP_CEWE
    if topic_key == "MOAN": return IMG_MOAN_COWO if gender == "COWO" else IMG_MOAN_CEWE
    return None

def format_thread_caption_html(title, emoji, gender, caption_text, channel_mention):
    # use <blockquote> for gender and "Klik tombol..." lines
    safe_caption = html_escape(caption_text or "")
    return (
        f"<b>{html_escape(title)} {html_escape(emoji)}</b>\n\n"
        f"<blockquote><b>GENDER 🕵️ : {html_escape(gender)} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}</b></blockquote>\n\n"
        f"{safe_caption}\n\n"
        f"<blockquote>👉 Klik tombol paling bawah untuk lihat full di channel {html_escape(channel_mention)}</blockquote>"
    )

def format_channel_caption_html(title, emoji, gender, caption_text):
    safe_caption = html_escape(caption_text or "")
    return (
        f"<b>{html_escape(title)} {html_escape(emoji)}</b>\n\n"
        f"<blockquote><b>GENDER 🕵️ : {html_escape(gender)} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}</b></blockquote>\n\n"
        f"{safe_caption}\n\n"
        f"<blockquote><b>BERIKAN REACT DAN NILAI!</b>\n⭐ RATE 1–10\n💬 COMMENT!</blockquote>\n\n"
        f"#{html_escape(gender)} #{html_escape(title)}"
    )

# ---------------- Handlers ----------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Selamat datang di Nabrutt 🤖</b>\n\nPilih jenis postingan:",
        parse_mode=ParseMode.HTML,
        reply_markup=start_keyboard()
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    # post menu
    if data == "post_menfess":
        context.user_data["topic"] = "MENFESS"
        await query.message.reply_text("<b>💌 Kamu memilih MENFESSBRUTT.</b>\n\nKirim teks menfess kamu sekarang (atau kirim media jika mau).", parse_mode=ParseMode.HTML)
        return

    if data == "post_pap":
        # choose photo/video
        await query.message.reply_text("<b>📸 Kamu memilih PAPBRUTT.</b>\n\nPilih tipe:", parse_mode=ParseMode.HTML, reply_markup=pap_type_keyboard())
        return

    if data == "post_moan":
        context.user_data["topic"] = "MOAN"
        # ask for caption first
        context.user_data["await_moan_caption"] = True
        await query.message.reply_text("<b>🎙 Kamu memilih MOANBRUTT.</b>\n\nMasukkan caption :", parse_mode=ParseMode.HTML)
        return

    # pap type
    if data == "pap_foto":
        context.user_data["topic"] = "PAP"
        context.user_data["pap_type"] = "pap_foto"
        await query.message.reply_text("<b>📷 Kamu memilih PAP FOTO.</b>\n\nKirim foto kamu sekarang!", parse_mode=ParseMode.HTML)
        return

    if data == "pap_video":
        context.user_data["topic"] = "PAP"
        context.user_data["pap_type"] = "pap_video"
        await query.message.reply_text("<b>🎥 Kamu memilih PAP VIDEO.</b>\n\nKirim video kamu sekarang!", parse_mode=ParseMode.HTML)
        return

    # gender selection (callbacks expected 'gender_cowo'/'gender_cewe')
    if data in ("gender_cowo", "gender_cewe"):
        gender = "COWO" if data == "gender_cowo" else "CEWE"
        context.user_data["gender"] = gender

        # check join
        not_joined = await check_all_membership(context.bot, uid)
        if not_joined:
            # show links and button to confirm
            links_text = "\n".join(f"👉 {html_escape(u)}" for u in [URL_NABRUTT, URL_GC_MENFESS, URL_GC_PAP, URL_GC_MOAN])
            await query.message.reply_text(
                f"<b>Gender kamu: {html_escape(gender)} ✅</b>\n\n"
                f"<b>⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:</b>\n"
                f"<blockquote>{links_text}</blockquote>\n\n"
                f"Jika sudah join semua, tekan tombol di bawah.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Sudah Join Semua", callback_data="join_done")]])
            )
            return
        # if all joined -> show post menu
        await query.message.reply_text("<b>✅ Semua step sudah selesai!</b>\n\nPilih jenis postingan:", parse_mode=ParseMode.HTML, reply_markup=start_keyboard())
        return

    if data == "join_done":
        # just show menu (we don't strictly re-check here)
        await query.message.reply_text("<b>✅ Semua step sudah selesai!</b>\n\nPilih jenis postingan:", parse_mode=ParseMode.HTML, reply_markup=start_keyboard())
        return

    if data == "repost_last":
        # simple behavior: resend start menu for new post
        await query.message.reply_text("<b>📩 Kirim lagi</b>\n\nPilih jenis postingan:", parse_mode=ParseMode.HTML, reply_markup=start_keyboard())
        return

async def gender_prompt_after_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When user selected a topic, ask gender
    # This handler is bound to callback queries 'post_*' above which ask for gender via buttons in /start keyboard.
    # But to ensure user always gets gender buttons, we expose a command to ask gender if missing.
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("<b>Pilih gender kamu:</b>", parse_mode=ParseMode.HTML, reply_markup=gender_keyboard())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Central message handler:
     - If awaiting moan caption -> store and ask for voice
     - If awaiting media for PAP -> accept photo/video
     - If MENFESS -> treat text as menfess content
    """
    user = update.effective_user
    uid = user.id
    data = context.user_data
    topic = data.get("topic")
    pap_type = data.get("pap_type")
    gender = data.get("gender", "COWO")
    caption_text = data.get("caption", "")

    # If waiting for MOAN caption
    if data.get("await_moan_caption"):
        text = update.message.text or ""
        data["caption"] = text
        data.pop("await_moan_caption", None)
        data["await_moan_media"] = True
        await update.message.reply_text("<b>✅ Caption berhasil dimasukkan!</b>\n\nKirim voice note (moan) sekarang 🎧", parse_mode=ParseMode.HTML)
        return

    # If waiting for MOAN media
    if data.get("await_moan_media"):
        if update.message.voice or update.message.audio:
            # publish MOAN
            await publish_post(update, context, topik="MOAN", media_type="voice", gender=gender, caption_text=data.get("caption",""))
            data.clear()
            return
        else:
            await update.message.reply_text("⚠️ Mohon kirim file voice/audio untuk MOAN.", parse_mode=ParseMode.HTML)
            return

    # If topic is MENFESS and user sends text -> directly publish
    if topic == "MENFESS" and (update.message.text or update.message.caption):
        text = (update.message.text or update.message.caption or "")
        await publish_post(update, context, topik="MENFESS", media_type=None, gender=gender, caption_text=text)
        context.user_data.clear()
        return

    # If topic is PAP: expect photo/video according to pap_type
    if topic == "PAP":
        if pap_type == "pap_foto" and update.message.photo:
            caption_user = update.message.caption or ""
            await publish_post(update, context, topik="PAP", media_type="photo", gender=gender, caption_text=caption_user)
            context.user_data.clear()
            return
        if pap_type == "pap_video" and update.message.video:
            caption_user = update.message.caption or ""
            await publish_post(update, context, topik="PAP", media_type="video", gender=gender, caption_text=caption_user)
            context.user_data.clear()
            return
        await update.message.reply_text("⚠️ Silakan kirim file sesuai tipe yang dipilih (Foto/Video).", parse_mode=ParseMode.HTML)
        return

    # fallback
    await update.message.reply_text("⚠️ Gunakan tombol menu untuk mulai (/start).", parse_mode=ParseMode.HTML)

async def publish_post(update: Update, context: ContextTypes.DEFAULT_TYPE, topik: str, media_type: str, gender: str, caption_text: str):
    """
    Sends:
      1) preview to GROUP thread -> header (GitHub RAW) + <blockquote> gender + click instruction
      2) full post to CHANNEL -> file-asli (photo/video/voice) with channel caption using <blockquote>
    """
    pap_type = context.user_data.get("pap_type")
    emoji = emoji_for(topik, pap_type=pap_type)
    title = title_for(topik, pap_type=pap_type)
    header = header_image_url(topik, gender, pap_type=pap_type)
    channel_mention = CH_USERNAME.get(topik, "")

    thread_caption = format_thread_caption_html(title, emoji, gender, caption_text, channel_mention)
    thread_map = {"MENFESS": THREAD_MENFESS, "PAP": THREAD_PAP, "MOAN": THREAD_MOAN}
    message_thread_id = thread_map.get(topik, THREAD_MENFESS)

    # send preview to thread (header from GitHub)
    try:
        await context.bot.send_photo(
            chat_id=GROUP_NABRUTT,
            photo=header,
            caption=thread_caption,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Lihat Full (Channel)", url=(URL_GC_MENFESS if topik=="MENFESS" else (URL_GC_PAP if topik=="PAP" else URL_GC_MOAN)))]]),
            message_thread_id=message_thread_id
        )
    except Exception as e:
        logger.exception("Failed to send thread preview: %s", e)
        # fallback to text message
        await context.bot.send_message(chat_id=GROUP_NABRUTT, text=thread_caption, parse_mode=ParseMode.HTML)

    # prepare channel caption
    channel_caption = format_channel_caption_html(title, emoji, gender, caption_text)

    # pick channel id
    channel_map = {"MENFESS": CHANNEL_MENFESS_ID, "PAP": CHANNEL_PAP_ID, "MOAN": CHANNEL_MOAN_ID}
    channel_id = channel_map.get(topik, CHANNEL_MENFESS_ID)

    # send actual media to channel (file-asli). photos/videos set has_spoiler=True for 2x tap effect.
    try:
        if media_type == "photo" and update.message.photo:
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(chat_id=channel_id, photo=file_id, caption=channel_caption, parse_mode=ParseMode.HTML, has_spoiler=True)
        elif media_type == "video" and update.message.video:
            file_id = update.message.video.file_id
            await context.bot.send_video(chat_id=channel_id, video=file_id, caption=channel_caption, parse_mode=ParseMode.HTML, has_spoiler=True)
        elif media_type == "voice" and update.message.voice:
            file_id = update.message.voice.file_id
            await context.bot.send_voice(chat_id=channel_id, voice=file_id, caption=channel_caption, parse_mode=ParseMode.HTML)
        elif media_type == "audio" and update.message.audio:
            file_id = update.message.audio.file_id
            await context.bot.send_audio(chat_id=channel_id, audio=file_id, caption=channel_caption, parse_mode=ParseMode.HTML)
        else:
            # text-only (menfess)
            await context.bot.send_message(chat_id=channel_id, text=channel_caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception("Failed to send to channel: %s", e)
        await update.message.reply_text("⚠️ Gagal mengirim ke channel. Cek log.", parse_mode=ParseMode.HTML)
        return

    # send confirmation to user (private chat) with retry option
    await update.message.reply_text("<b>✅ Postingan kamu berhasil dikirim!</b>\n\nMau kirim lagi?", parse_mode=ParseMode.HTML, reply_markup=retry_keyboard())

# ---------------- Flask webhook endpoint ----------------
@flask_app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅", 200


@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    """Terima update dari Telegram (Render + PTB v20.3 compatible)"""
    data = await request.get_json()
    update = Update.de_json(data, bot)
    await application.update_queue.put(update)
    return "OK", 200


def main():
    global application, bot

    if BOT_TOKEN is None or BOT_TOKEN.strip() == "" or BOT_TOKEN.startswith("<PUT"):
        logger.error("BOT_TOKEN not set. Please set environment variable BOT_TOKEN.")
        return

    # Buat bot & app Telegram
    bot = Bot(BOT_TOKEN)
    application = Application.builder().token(BOT_TOKEN).build()

    # Tambahkan handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(callback_handler, pattern="^(post_menfess|post_pap|post_moan|pap_foto|pap_video|join_done|repost_last)$"))
    application.add_handler(CallbackQueryHandler(callback_handler, pattern="^(gender_cowo|gender_cewe)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.AUDIO, message_handler))

    # Set webhook (gunakan asyncio agar tidak ada warning)
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    logger.info("Setting webhook to %s", webhook_url)
    import asyncio
    asyncio.run(bot.set_webhook(webhook_url))

    # Jalankan Flask server
    logger.info("Starting Flask (webhook receiver) on port %s", PORT)
    flask_app.run(host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
