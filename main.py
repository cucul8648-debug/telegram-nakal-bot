# filename: main_polling_final_joinquote_posting.py
# requirements:
#   python-telegram-bot==20.3
#   python-dotenv==1.0.1

import os
import logging
from html import escape as html_escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8466148433:AAHyMyVisRnEIaiGg6Fm7Oh6H-fDB0lYJfk")

GROUP_NABRUTT = int(os.environ.get("GROUP_NABRUTT", -1003098333444))
THREAD_MENFESS = int(os.environ.get("THREAD_MENFESS", 1036))
THREAD_PAP     = int(os.environ.get("THREAD_PAP", 393))
THREAD_MOAN    = int(os.environ.get("THREAD_MOAN", 2298))

CHANNEL_MENFESS_ID = int(os.environ.get("CHANNEL_MENFESS_ID", -1002989043936))
CHANNEL_PAP_ID     = int(os.environ.get("CHANNEL_PAP_ID", -1003189592682))
CHANNEL_MOAN_ID    = int(os.environ.get("CHANNEL_MOAN_ID", -1003196180758))

CH_USERNAME = {
    "MENFESS": "@MenfessNABRUTT",
    "PAP": "@PAPCABULNABRUTT",
    "MOAN": "@MOAN18NABRUTT"
}

IMG_PAP_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MENFESS_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_MOAN_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MOAN_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"

URL_NABRUTT    = "https://t.me/NABRUTT11"
URL_GC_MENFESS = "https://t.me/MenfessNABRUTT"
URL_GC_PAP     = "https://t.me/PAPCABULNABRUTT"
URL_GC_MOAN    = "https://t.me/MOAN18NABRUTT"

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---------------- KEYBOARDS ----------------
def gender_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ])

def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess")],
        [InlineKeyboardButton("📸 PapBRUTT", callback_data="post_pap")],
        [InlineKeyboardButton("🎙 MoanBRUTT", callback_data="post_moan")]
    ])

def pap_type_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📷 Foto", callback_data="pap_foto")],
        [InlineKeyboardButton("🎥 Video", callback_data="pap_video")]
    ])

def join_checker_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Sudah Join Semua", callback_data="join_done")]])

def retry_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess")],
        [InlineKeyboardButton("📸 PapBRUTT", callback_data="post_pap")],
        [InlineKeyboardButton("🎙 MoanBRUTT", callback_data="post_moan")],
        [InlineKeyboardButton("📩 Kirim Lagi", callback_data="repost_last")]
    ])

# ---------------- HELPERS ----------------
async def check_all_membership(bot: Bot, uid: int):
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
            not_joined.append(url)
    return not_joined

def emoji_for(topic_key, pap_type=None):
    if topic_key == "MENFESS": return "💌"
    if topic_key == "PAP": return "📸" if pap_type=="pap_foto" else "🎥"
    if topic_key == "MOAN": return "🎧"
    return ""

def title_for(topic_key, pap_type=None):
    if topic_key=="MENFESS": return "MENFESSBRUTT"
    if topic_key=="PAP": return "PAPBRUTT" if pap_type=="pap_foto" else "VIDEOBRUTT"
    if topic_key=="MOAN": return "MOANBRUTT"
    return topic_key

def header_image_url(topic_key, gender, pap_type=None):
    if topic_key=="MENFESS": return IMG_MENFESS_COWO if gender=="COWO" else IMG_MENFESS_CEWE
    if topic_key=="PAP":
        if pap_type=="pap_video": return IMG_VIDEO_COWO if gender=="COWO" else IMG_VIDEO_CEWE
        return IMG_PAP_COWO if gender=="COWO" else IMG_PAP_CEWE
    if topic_key=="MOAN": return IMG_MOAN_COWO if gender=="COWO" else IMG_MOAN_CEWE
    return None

def format_thread_caption_html(title, emoji, gender, caption_text, channel_mention):
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

# ---------------- HANDLERS ----------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return
    await update.message.reply_text(
        "👋 Selamat datang di Nabrutt 🤖\n\nPilih jenis kelaminmu terlebih dahulu:",
        reply_markup=gender_keyboard()
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    user_data = context.user_data
    data = query.data

    # ---------- REPOST LAGI ----------
    if data=="repost_last":
        user_data.clear()
        await query.message.edit_text(
            "👋 Selamat datang di Nabrutt 🤖\n\nPilih jenis kelaminmu terlebih dahulu:",
            reply_markup=gender_keyboard()
        )
        return

    # ---------- GENDER & JOIN CHECK ----------
    if data in ("gender_cowo","gender_cewe"):
        gender = "COWO" if data=="gender_cowo" else "CEWE"
        user_data["gender"] = gender
        not_joined = await check_all_membership(context.bot, uid)
        if not_joined:
            links_text = "\n".join(f"👉 {html_escape(u)}" for u in not_joined)
            await query.message.edit_text(
                f"<b>Gender kamu: {html_escape(gender)} ✅</b>\n\n"
                f"<b>⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:</b>\n"
                f"<blockquote>{links_text}</blockquote>\n\n"
                f"Jika sudah join semua, tekan tombol di bawah.",
                parse_mode=ParseMode.HTML,
                reply_markup=join_checker_keyboard()
            )
            return
        await query.message.edit_text(
            "<b>✅ Terima kasih, kamu sudah join semua!</b>\n\nSilakan pilih jenis postingan:",
            parse_mode=ParseMode.HTML,
            reply_markup=start_keyboard()
        )
        return

    if data=="join_done":
        await query.message.edit_text(
            "<b>✅ Terima kasih, kamu sudah join semua!</b>\n\nSilakan pilih jenis postingan:",
            parse_mode=ParseMode.HTML,
            reply_markup=start_keyboard()
        )
        return

    # ---------- PILIH POSTINGAN (dari main_polling_final.py) ----------
    if data=="post_menfess":
        user_data["topic"] = "MENFESS"
        await query.message.edit_text("<b>💌 Kamu memilih MENFESSBRUTT.</b>\n\nKirim teks menfess kamu sekarang.", parse_mode=ParseMode.HTML)
        return

    if data=="post_pap":
        await query.message.edit_text("<b>📸 Kamu memilih PAPBRUTT.</b>\n\nPilih tipe:", parse_mode=ParseMode.HTML, reply_markup=pap_type_keyboard())
        return

    if data=="post_moan":
        user_data["topic"] = "MOAN"
        user_data["await_moan_caption"] = True
        await query.message.edit_text("<b>🎙 Kamu memilih MOANBRUTT.</b>\n\nMasukkan caption dulu:", parse_mode=ParseMode.HTML)
        return

    if data in ("pap_foto","pap_video"):
        user_data["topic"] = "PAP"
        user_data["pap_type"] = data
        msg = "<b>📷 Kamu memilih PAP FOTO.</b>\n\nKirim foto sekarang!" if data=="pap_foto" else "<b>🎥 Kamu memilih PAP VIDEO.</b>\n\nKirim video sekarang!"
        await query.message.edit_text(msg, parse_mode=ParseMode.HTML)
        return

# ---------------- MESSAGE HANDLER ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return

    user_data = context.user_data
    topic = user_data.get("topic")
    pap_type = user_data.get("pap_type")
    gender = user_data.get("gender","COWO")

    # MOAN caption dulu
    if user_data.get("await_moan_caption"):
        user_data["caption"] = update.message.text or ""
        user_data.pop("await_moan_caption", None)
        user_data["await_moan_media"] = True
        await update.message.reply_text("<b>✅ Caption berhasil dimasukkan!</b>\n\nKirim voice note (moan) sekarang 🎧", parse_mode=ParseMode.HTML)
        return

    # MOAN media
    if user_data.get("await_moan_media"):
        if update.message.voice or update.message.audio:
            await publish_post(update, context, topik="MOAN", media_type="voice", gender=gender, caption_text=user_data.get("caption",""))
            user_data.clear()
        else:
            await update.message.reply_text("⚠️ Mohon kirim file voice/audio untuk MOAN.", parse_mode=ParseMode.HTML)
        return

    # MENFESS → teks saja
    if topic=="MENFESS" and update.message.text:
        await publish_post(update, context, topik="MENFESS", media_type=None, gender=gender, caption_text=update.message.text)
        user_data.clear()
        return

    # PAP FOTO / VIDEO
    if topic=="PAP":
        if pap_type=="pap_foto" and update.message.photo:
            await publish_post(update, context, topik="PAP", media_type="photo", gender=gender, caption_text=update.message.caption or "")
            user_data.clear()
            return
        if pap_type=="pap_video" and update.message.video:
            await publish_post(update, context, topik="PAP", media_type="video", gender=gender, caption_text=update.message.caption or "")
            user_data.clear()
            return
        await update.message.reply_text("⚠️ Silakan kirim file sesuai tipe yang dipilih (Foto/Video).", parse_mode=ParseMode.HTML)
        return

    await update.message.reply_text("⚠️ Gunakan tombol menu untuk mulai (/start).", parse_mode=ParseMode.HTML)

# ---------------- PUBLISH FUNCTION ----------------
async def publish_post(update: Update, context: ContextTypes.DEFAULT_TYPE, topik: str, media_type: str, gender: str, caption_text: str):
    pap_type = context.user_data.get("pap_type")
    emoji = emoji_for(topik, pap_type=pap_type)
    title = title_for(topik, pap_type=pap_type)
    header = header_image_url(topik, gender, pap_type=pap_type)
    channel_mention = CH_USERNAME.get(topik,"")
    thread_map = {"MENFESS": THREAD_MENFESS,"PAP": THREAD_PAP,"MOAN": THREAD_MOAN}
    message_thread_id = thread_map.get(topik, THREAD_MENFESS)

    # ---------- Preview di thread group ----------
    try:
        await context.bot.send_photo(
            chat_id=GROUP_NABRUTT,
            photo=header,
            caption=format_thread_caption_html(title, emoji, gender, caption_text, channel_mention),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Lihat Full (Channel)", url=(URL_GC_MENFESS if topik=="MENFESS" else (URL_GC_PAP if topik=="PAP" else URL_GC_MOAN)))]]),
            message_thread_id=message_thread_id
        )
    except Exception as e:
        logger.exception("Failed to send thread preview: %s", e)
        await context.bot.send_message(chat_id=GROUP_NABRUTT, text=caption_text, parse_mode=ParseMode.HTML)

    # ---------- Kirim ke channel ----------
    channel_map = {"MENFESS": CHANNEL_MENFESS_ID,"PAP": CHANNEL_PAP_ID,"MOAN": CHANNEL_MOAN_ID}
    channel_id = channel_map.get(topik, CHANNEL_MENFESS_ID)
    channel_caption = format_channel_caption_html(title, emoji, gender, caption_text)

    try:
        if media_type=="photo" and update.message.photo:
            await context.bot.send_photo(chat_id=channel_id, photo=update.message.photo[-1].file_id, caption=channel_caption, parse_mode=ParseMode.HTML, has_spoiler=True)
        elif media_type=="video" and update.message.video:
            await context.bot.send_video(chat_id=channel_id, video=update.message.video.file_id, caption=channel_caption, parse_mode=ParseMode.HTML, has_spoiler=True)
        elif media_type=="voice" and update.message.voice:
            await context.bot.send_voice(chat_id=channel_id, voice=update.message.voice.file_id, caption=channel_caption, parse_mode=ParseMode.HTML)
        elif media_type=="audio" and update.message.audio:
            await context.bot.send_audio(chat_id=channel_id, audio=update.message.audio.file_id, caption=channel_caption, parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=channel_id, text=channel_caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception("Failed to send to channel: %s", e)
        await update.message.reply_text("⚠️ Gagal mengirim ke channel. Cek log.", parse_mode=ParseMode.HTML)
        return

    # ---------- Balas ke user + tombol kirim lagi ----------
    await update.message.reply_text("<b>✅ Postingan kamu berhasil dikirim!</b>\n\nMau kirim apa lagi?", parse_mode=ParseMode.HTML, reply_markup=retry_keyboard())

# ---------------- MAIN ----------------
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.ALL, message_handler))
    logger.info("Bot started in polling mode...")
    application.run_polling()

if __name__ == "__main__":
    main()
