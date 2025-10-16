# filename: main_webhook_final_joinquote_posting_gudang_fixready.py
# requirements:
#   python-telegram-bot==20.3
#   python-dotenv==1.0.1
#   Flask==2.3.3

import os
import logging
from flask import Flask, request
from html import escape as html_escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ---------------- CONFIG ----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8466148433:AAHIsxkSbx4ddtT2giEWtGGIh6e3OPcv7FA")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://telegram-nakal-bot.onrender.com")

GROUP_NABRUTT = int(os.environ.get("GROUP_NABRUTT", -1003098333444))
THREAD_MENFESS = int(os.environ.get("THREAD_MENFESS", 1036))
THREAD_PAP     = int(os.environ.get("THREAD_PAP", 393))
THREAD_MOAN    = int(os.environ.get("THREAD_MOAN", 2298))

CHANNEL_MENFESS_ID  = int(os.environ.get("CHANNEL_MENFESS_ID", -1002989043936))
CHANNEL_PAP_ID      = int(os.environ.get("CHANNEL_PAP_ID", -1003163832814))
CHANNEL_PAP_COWO_ID = int(os.environ.get("CHANNEL_PAP_COWO_ID", -1003105091308))
CHANNEL_MOAN_ID     = int(os.environ.get("CHANNEL_MOAN_ID", -1003196180758))
CHANNEL_GUDANG_ID   = int(os.environ.get("CHANNEL_GUDANG_ID", -1003013806700))

CH_USERNAME = {
    "MENFESS": "@MenfessNABRUTT",
    "PAP_CEWE": "@NABRUTTRATECEWE",
    "MOAN": "@MOAN18NABRUTT"
}
CH_USERNAME_COWO = "@Nabruttcowo"

# gambar tetap
IMG_MENFESS_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_PAP_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
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

# ---------------- KEYBOARD ----------------
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
    return "💌" if topic_key=="MENFESS" else ("📸" if pap_type=="pap_foto" else "🎥" if pap_type=="pap_video" else "🎧")

def title_for(topic_key, pap_type=None):
    if topic_key == "MENFESS": return "MENFESSBRUTT"
    if topic_key == "PAP": return "PAPBRUTT" if pap_type=="pap_foto" else "VIDEOBRUTT"
    if topic_key == "MOAN": return "MOANBRUTT"
    return topic_key

def header_image_url(topic_key, gender, pap_type=None):
    if topic_key == "MENFESS": return IMG_MENFESS_COWO if gender=="COWO" else IMG_MENFESS_CEWE
    if topic_key == "PAP":
        return IMG_VIDEO_COWO if pap_type=="pap_video" and gender=="COWO" else \
               IMG_VIDEO_CEWE if pap_type=="pap_video" else \
               IMG_PAP_COWO if gender=="COWO" else IMG_PAP_CEWE
    if topic_key == "MOAN": return IMG_MOAN_COWO if gender=="COWO" else IMG_MOAN_CEWE
    return None

def format_thread_caption_html(title, emoji, gender, caption_text, channel_mention):
    safe = html_escape(caption_text or "")
    return (f"<b>{title} {emoji}</b>\n\n"
            f"<blockquote><b>GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}</b></blockquote>\n\n"
            f"{safe}\n\n<blockquote>👉 Lihat full di {channel_mention}</blockquote>")

def format_channel_caption_html(title, emoji, gender, caption_text):
    safe = html_escape(caption_text or "")
    return (f"<b>{title} {emoji}</b>\n\n"
            f"<blockquote><b>GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}</b></blockquote>\n\n"
            f"{safe}\n\n<blockquote><b>⭐ RATE 1–10 & 💬 COMMENT!</b></blockquote>\n\n"
            f"#{gender} #{title}")

# ---------------- HANDLERS ----------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private": return
    await update.message.reply_text(
        "👋 Selamat datang di Nabrutt!\n\nPilih jenis kelaminmu:",
        reply_markup=gender_keyboard(),
        protect_content=True
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    uid = query.from_user.id; data = query.data; ud = context.user_data

    if data == "repost_resetgender":
        ud.clear()
        await query.message.edit_text("🔁 Pilih gender baru kamu:", reply_markup=gender_keyboard())
        return

    if data in ("gender_cowo","gender_cewe"):
        ud["gender"] = "COWO" if data=="gender_cowo" else "CEWE"
        not_joined = await check_all_membership(context.bot, uid)
        if not_joined:
            txt = "\n".join(f"👉 {u}" for u in not_joined)
            await query.message.edit_text(
                f"<b>⚠️ Wajib join semua dulu:</b>\n{txt}",
                parse_mode=ParseMode.HTML,
                reply_markup=join_checker_keyboard()
            )
        else:
            await query.message.edit_text(
                "<b>✅ Sudah join semua!</b>\n\nPilih jenis postingan:",
                parse_mode=ParseMode.HTML,
                reply_markup=start_keyboard()
            )
        return

    if data == "join_done":
        not_joined = await check_all_membership(context.bot, uid)
        if not_joined:
            txt = "\n".join(f"👉 {u}" for u in not_joined)
            await query.message.edit_text(
                f"<b>⚠️ Belum join semua!</b>\n{txt}",
                parse_mode=ParseMode.HTML,
                reply_markup=join_checker_keyboard()
            )
            return
        await query.message.edit_text(
            "<b>✅ Terima kasih!</b>\n\nPilih jenis postingan:",
            parse_mode=ParseMode.HTML,
            reply_markup=start_keyboard()
        )
        return

    if data=="post_menfess":
        ud["topic"]="MENFESS"
        await query.message.edit_text("💌 Kirim teks menfess kamu:", parse_mode=ParseMode.HTML)
    elif data=="post_pap":
        await query.message.edit_text("📸 Pilih tipe PAP:", parse_mode=ParseMode.HTML, reply_markup=pap_type_keyboard())
    elif data=="post_moan":
        ud["topic"]="MOAN"; ud["await_moan_caption"]=True
        await query.message.edit_text("🎙 Masukkan caption untuk moan:", parse_mode=ParseMode.HTML)
    elif data in ("pap_foto","pap_video"):
        ud["topic"]="PAP"; ud["pap_type"]=data
        msg = "📷 Kirim foto sekarang!" if data=="pap_foto" else "🎥 Kirim video sekarang!"
        await query.message.edit_text(msg, parse_mode=ParseMode.HTML)

# ---------------- MESSAGE HANDLER ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private": return
    ud = context.user_data; topic = ud.get("topic"); gender = ud.get("gender","COWO")

    if ud.get("await_moan_caption"):
        ud["caption"]=update.message.text; ud.pop("await_moan_caption",None); ud["await_moan_media"]=True
        await update.message.reply_text("✅ Caption disimpan!\nKirim voice note sekarang 🎧", protect_content=True)
        return

    if ud.get("await_moan_media"):
        if update.message.voice or update.message.audio:
            await publish_post(update,context,"MOAN","voice",gender,ud.get("caption",""))
            ud.clear(); ud["gender"]=gender
        else:
            await update.message.reply_text("⚠️ Kirim voice/audio untuk moan.", protect_content=True)
        return

    if topic=="MENFESS" and update.message.text:
        await publish_post(update,context,"MENFESS",None,gender,update.message.text)
        ud.clear(); ud["gender"]=gender; return

    if topic=="PAP":
        if update.message.photo:
            await publish_post(update,context,"PAP","photo",gender,update.message.caption or "")
        elif update.message.video:
            await publish_post(update,context,"PAP","video",gender,update.message.caption or "")
        else:
            await update.message.reply_text("⚠️ Kirim foto/video sesuai pilihan.", protect_content=True)
        ud.clear(); ud["gender"]=gender; return

    await update.message.reply_text("Gunakan /start untuk memulai.", protect_content=True)

# ---------------- PUBLISH ----------------
async def publish_post(update, context, topik, media_type, gender, caption_text):
    pap_type=context.user_data.get("pap_type")
    emoji=emoji_for(topik,pap_type); title=title_for(topik,pap_type)
    header=header_image_url(topik,gender,pap_type)

    if topik=="PAP" and gender=="COWO":
        channel_id=CHANNEL_PAP_COWO_ID; channel_mention=CH_USERNAME_COWO; channel_url=URL_GC_PAP_COWO
    else:
        cmap={"MENFESS":CHANNEL_MENFESS_ID,"PAP":CHANNEL_PAP_ID,"MOAN":CHANNEL_MOAN_ID}
        channel_id=cmap[topik]; channel_mention=CH_USERNAME[topik]; channel_url=URL_GC_MENFESS if topik=="MENFESS" else URL_GC_PAP if topik=="PAP" else URL_GC_MOAN
    thread_map={"MENFESS":THREAD_MENFESS,"PAP":THREAD_PAP,"MOAN":THREAD_MOAN}
    thread_id=thread_map[topik]

    await context.bot.send_photo(
        chat_id=GROUP_NABRUTT, photo=header,
        caption=format_thread_caption_html(title,emoji,gender,caption_text,channel_mention),
        parse_mode=ParseMode.HTML,
        message_thread_id=thread_id,
        protect_content=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Lihat di Channel", url=channel_url)]])
    )

    channel_caption=format_channel_caption_html(title,emoji,gender,caption_text)
    if media_type=="photo" and update.message.photo:
        pid=update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=channel_id, photo=pid, caption=channel_caption, parse_mode=ParseMode.HTML, protect_content=True)
        await context.bot.send_photo(chat_id=CHANNEL_GUDANG_ID, photo=pid, protect_content=True)
    elif media_type=="video" and update.message.video:
        vid=update.message.video.file_id
        await context.bot.send_video(chat_id=channel_id, video=vid, caption=channel_caption, parse_mode=ParseMode.HTML, protect_content=True)
        await context.bot.send_video(chat_id=CHANNEL_GUDANG_ID, video=vid, protect_content=True)
    elif media_type in ("voice","audio"):
        v = update.message.voice or update.message.audio
        fid = v.file_id
        send_func = context.bot.send_voice if update.message.voice else context.bot.send_audio
        await send_func(chat_id=channel_id, voice=fid if update.message.voice else fid, caption=channel_caption, parse_mode=ParseMode.HTML, protect_content=True)
        await send_func(chat_id=CHANNEL_GUDANG_ID, voice=fid if update.message.voice else fid, protect_content=True)
    else:
        await context.bot.send_message(chat_id=channel_id, text=channel_caption, parse_mode=ParseMode.HTML, protect_content=True)

    await update.message.reply_text(
        "<b>✅ Postingan kamu berhasil dikirim!</b>\n\nMau kirim apa lagi?",
        parse_mode=ParseMode.HTML,
        reply_markup=retry_keyboard(),
        protect_content=True
    )

# ---------------- FLASK ----------------
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start_handler))
application.add_handler(CallbackQueryHandler(callback_handler))
application.add_handler(MessageHandler(filters.ALL, message_handler))

@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.headers.get("content-type") == "application/json":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "✅ Bot Nabrutt Webhook aktif.", 200

async def set_webhook():
    bot = Bot(token=BOT_TOKEN)
    url = f"{WEBHOOK_URL}/webhook"
    await bot.delete_webhook()
    await bot.set_webhook(url=url)
    logger.info(f"✅ Webhook diset: {url}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    import asyncio

    async def startup():
        await set_webhook()
        await application.initialize()
        await application.start()
        logger.info("✅ Application initialized & started")

    asyncio.get_event_loop().run_until_complete(startup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
