import os
import logging
import asyncio
from html import escape as html_escape
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 5000))

GROUP_NABRUTT = int(os.environ.get("GROUP_NABRUTT"))
THREAD_MENFESS = int(os.environ.get("THREAD_MENFESS"))
THREAD_PAP     = int(os.environ.get("THREAD_PAP"))
THREAD_MOAN    = int(os.environ.get("THREAD_MOAN"))

CHANNEL_MENFESS_ID  = int(os.environ.get("CHANNEL_MENFESS_ID"))
CHANNEL_PAP_ID      = int(os.environ.get("CHANNEL_PAP_ID"))
CHANNEL_PAP_COWO_ID = int(os.environ.get("CHANNEL_PAP_COWO_ID"))
CHANNEL_MOAN_ID     = int(os.environ.get("CHANNEL_MOAN_ID"))
CHANNEL_GUDANG_ID   = int(os.environ.get("CHANNEL_GUDANG_ID"))

CH_USERNAME = {
    "MENFESS": "@MenfessNABRUTT",
    "PAP_CEWE": "@NABRUTTRATECEWE",
    "MOAN": "@MOAN18NABRUTT"
}
CH_USERNAME_COWO = "@Nabruttcowo"

IMG_PAP_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MENFESS_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_MOAN_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MOAN_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"

URL_NABRUTT       = "https://t.me/NABRUTT11"
URL_GC_MENFESS    = "https://t.me/MenfessNABRUTT"
URL_GC_PAP        = "https://t.me/NABRUTTRATECEWE"
URL_GC_PAP_COWO   = "https://t.me/Nabruttcowo"
URL_GC_MOAN       = "https://t.me/MOAN18NABRUTT"

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---------------- FLASK APP ----------------
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

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
        [InlineKeyboardButton("🔁 Kirim Lagi", callback_data="repost_resetgender")]
    ])

# ---------------- HELPERS ----------------
async def check_all_membership(bot: Bot, uid: int):
    checks = [
        (GROUP_NABRUTT, URL_NABRUTT),
        (CHANNEL_MENFESS_ID, URL_GC_MENFESS),
        (CHANNEL_PAP_ID, URL_GC_PAP),
        (CHANNEL_PAP_COWO_ID, URL_GC_PAP_COWO),
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
        reply_markup=gender_keyboard(),
        protect_content=True
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    user_data = context.user_data
    data = query.data

    # 🔁 “Kirim Lagi” — reset total, minta gender baru
    if data == "repost_resetgender":
        user_data.clear()
        await query.message.edit_text(
            "🔄 Kamu memilih untuk kirim lagi.\n\nPilih gender baru kamu:",
            reply_markup=gender_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    # --- gender pilih ---
    if data in ("gender_cowo","gender_cewe"):
        gender = "COWO" if data=="gender_cowo" else "CEWE"
        user_data["gender"] = gender
        not_joined = await check_all_membership(context.bot, uid)
        if not_joined:
            links_text = "\n".join(f"👉 {html_escape(u)}" for u in not_joined)
            await query.message.edit_text(
                f"<b>Gender kamu: {html_escape(gender)} ✅</b>\n\n"
                f"<b>⚠️ Wajib join semua group & channel di bawah ini:</b>\n"
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

    # --- join done ---
    if data == "join_done":
        not_joined = await check_all_membership(context.bot, uid)
        if not_joined:
            links_text = "\n".join(f"👉 {html_escape(u)}" for u in not_joined)
            await query.message.edit_text(
                f"<b>⚠️ Kamu belum join semua!</b>\n\n"
                f"<b>Wajib join semua link di bawah ini dulu sebelum lanjut:</b>\n"
                f"<blockquote>{links_text}</blockquote>",
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

    # --- menu posting ---
    if data=="post_menfess":
        user_data["topic"]="MENFESS"
        await query.message.edit_text("<b>💌 Kamu memilih MENFESSBRUTT.</b>\n\nKirim teks menfess kamu sekarang.", parse_mode=ParseMode.HTML)
        return
    if data=="post_pap":
        await query.message.edit_text("<b>📸 Kamu memilih PAPBRUTT.</b>\n\nPilih tipe:", parse_mode=ParseMode.HTML, reply_markup=pap_type_keyboard())
        return
    if data=="post_moan":
        user_data["topic"]="MOAN"
        user_data["await_moan_caption"]=True
        await query.message.edit_text("<b>🎙 Kamu memilih MOANBRUTT.</b>\n\nMasukkan caption dulu:", parse_mode=ParseMode.HTML)
        return
    if data in ("pap_foto","pap_video"):
        user_data["topic"]="PAP"
        user_data["pap_type"]=data
        msg="<b>📷 Kamu memilih PAP FOTO.</b>\n\nKirim foto sekarang!" if data=="pap_foto" else "<b>🎥 Kamu memilih PAP VIDEO.</b>\n\nKirim video sekarang!"
        await query.message.edit_text(msg, parse_mode=ParseMode.HTML)
        return

# ---------------- MESSAGE HANDLER ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return
    user_data=context.user_data
    topic=user_data.get("topic")
    pap_type=user_data.get("pap_type")
    gender=user_data.get("gender","COWO")

    if user_data.get("await_moan_caption"):
        user_data["caption"]=update.message.text or ""
        user_data.pop("await_moan_caption",None)
        user_data["await_moan_media"]=True
        await update.message.reply_text("<b>✅ Caption berhasil dimasukkan!</b>\n\nKirim voice note (moan) sekarang 🎧", parse_mode=ParseMode.HTML, protect_content=True)
        return
    if user_data.get("await_moan_media"):
        if update.message.voice or update.message.audio:
            await publish_post(update,context,"MOAN","voice",gender,user_data.get("caption",""))
            keys_to_clear = [k for k in user_data if k != "gender"]
            for k in keys_to_clear:
                user_data.pop(k)
        else:
            await update.message.reply_text("⚠️ Mohon kirim file voice/audio untuk MOAN.",parse_mode=ParseMode.HTML,protect_content=True)
        return

    if topic=="MENFESS" and update.message.text:
        await publish_post(update,context,"MENFESS",None,gender,update.message.text)
        keys_to_clear = [k for k in user_data if k != "gender"]
        for k in keys_to_clear:
            user_data.pop(k)
        return

    if topic=="PAP":
        if pap_type=="pap_foto" and update.message.photo:
            await publish_post(update,context,"PAP","photo",gender,update.message.caption or "")
            keys_to_clear = [k for k in user_data if k != "gender"]
            for k in keys_to_clear:
                user_data.pop(k)
            return
        if pap_type=="pap_video" and update.message.video:
            await publish_post(update,context,"PAP","video",gender,update.message.caption or "")
            keys_to_clear = [k for k in user_data if k != "gender"]
            for k in keys_to_clear:
                user_data.pop(k)
            return
        await update.message.reply_text("⚠️ Silakan kirim file sesuai tipe yang dipilih (Foto/Video).",parse_mode=ParseMode.HTML,protect_content=True)
        return

    await update.message.reply_text("⚠️ Gunakan tombol menu untuk mulai (/start).",parse_mode=ParseMode.HTML,protect_content=True)


# ---------------- PUBLISH FUNCTION ----------------
async def publish_post(update: Update, context: ContextTypes.DEFAULT_TYPE, topik:str, media_type:str, gender:str, caption_text:str):
    pap_type=context.user_data.get("pap_type")
    emoji=emoji_for(topik,pap_type)
    title=title_for(topik,pap_type)
    header=header_image_url(topik,gender,pap_type)

    if topik == "PAP" and gender == "COWO":
        channel_id = CHANNEL_PAP_COWO_ID
        channel_mention = CH_USERNAME_COWO
        channel_url = URL_GC_PAP_COWO
    else:
        channel_map = {"MENFESS": CHANNEL_MENFESS_ID, "PAP": CHANNEL_PAP_ID, "MOAN": CHANNEL_MOAN_ID}
        channel_id = channel_map.get(topik, CHANNEL_MENFESS_ID)
        channel_mention = CH_USERNAME.get(topik, "")
        channel_url = URL_GC_PAP if topik=="PAP" else (URL_GC_MENFESS if topik=="MENFESS" else URL_GC_MOAN)

    thread_map = {"MENFESS": THREAD_MENFESS, "PAP": THREAD_PAP, "MOAN": THREAD_MOAN}
    message_thread_id = thread_map.get(topik, THREAD_MENFESS)

    try:
        await context.bot.send_photo(
            chat_id=GROUP_NABRUTT,
            photo=header,
            caption=format_thread_caption_html(title, emoji, gender, caption_text, channel_mention),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Lihat Full (Channel)", url=channel_url)]]),
            message_thread_id=message_thread_id,
            protect_content=True
        )
    except Exception as e:
        logger.exception("Failed to send thread preview: %s", e)
        await context.bot.send_message(chat_id=GROUP_NABRUTT, text=caption_text, parse_mode=ParseMode.HTML, protect_content=True)

    channel_caption = format_channel_caption_html(title, emoji, gender, caption_text)
    try:
        # kirim ke channel utama
        if media_type=="photo" and update.message.photo:
            photo_id = update.message.photo[-1].file_id
            await context.bot.send_photo(chat_id=channel_id, photo=photo_id,
                                         caption=channel_caption, parse_mode=ParseMode.HTML, has_spoiler=True, protect_content=True)
            # kirim ke gudang (tanpa caption)
            await context.bot.send_photo(chat_id=CHANNEL_GUDANG_ID, photo=photo_id, protect_content=True)

        elif media_type=="video" and update.message.video:
            vid_id = update.message.video.file_id
            await context.bot.send_video(chat_id=channel_id, video=vid_id,
                                         caption=channel_caption, parse_mode=ParseMode.HTML, has_spoiler=True, protect_content=True)
            await context.bot.send_video(chat_id=CHANNEL_GUDANG_ID, video=vid_id, protect_content=True)

        elif media_type=="voice" and update.message.voice:
            v_id = update.message.voice.file_id
            await context.bot.send_voice(chat_id=channel_id, voice=v_id,
                                         caption=channel_caption, parse_mode=ParseMode.HTML, protect_content=True)
            await context.bot.send_voice(chat_id=CHANNEL_GUDANG_ID, voice=v_id, protect_content=True)

        elif media_type=="audio" and update.message.audio:
            a_id = update.message.audio.file_id
            await context.bot.send_audio(chat_id=channel_id, audio=a_id,
                                         caption=channel_caption, parse_mode=ParseMode.HTML, protect_content=True)
            await context.bot.send_audio(chat_id=CHANNEL_GUDANG_ID, audio=a_id, protect_content=True)

        else:
            await context.bot.send_message(chat_id=channel_id, text=channel_caption,
                                           parse_mode=ParseMode.HTML, protect_content=True)
    except Exception as e:
        logger.exception("Failed to send to channel/gudang: %s", e)
        await update.message.reply_text("⚠️ Gagal mengirim ke channel/gudang. Cek log.", parse_mode=ParseMode.HTML, protect_content=True)
        return

    await update.message.reply_text(
        "<b>✅ Postingan kamu berhasil dikirim!</b>\n\nMau kirim apa lagi?",
        parse_mode=ParseMode.HTML,
        reply_markup=retry_keyboard(),
        protect_content=True
    )

# ---------------- FLASK WEBHOOK ----------------
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.create_task(application.update_queue.put(update))
    return "OK", 200

# ---------------- MAIN ----------------
def main():
    logger.info(f"Setting webhook to {WEBHOOK_URL} ...")
    bot = application.bot
    bot.delete_webhook()
    bot.set_webhook(WEBHOOK_URL)
    
    logger.info("Starting Flask server for webhook...")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
