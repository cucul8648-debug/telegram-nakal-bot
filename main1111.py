# filename: main_final_render_autoset_fixed.py
# pip install python-telegram-bot==20.3 Flask==3.0.3

import os, logging, asyncio
from flask import Flask, request
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ================== KONFIG ==================
TOKEN = os.environ.get("BOT_TOKEN", "8466148433:AAH9NFT_wrkBlZ-uO8hllAdxdTwFpLqip74")
RENDER_URL = "https://telegram-nakal-bot.onrender.com"

# GROUP + THREAD
GROUP_NABRUTT  = -1003098333444
THREAD_MENFESS = 1036
THREAD_PAP     = 393
THREAD_MOAN    = 2298

# CHANNEL
CHANNEL_MENFESS_ID = -1002989043936
CHANNEL_PAP_ID     = -1003189592682
CHANNEL_MOAN_ID    = -1003196180758

# URL Join / Redirect
URL_NABRUTT    = "https://t.me/NABRUTT11"
URL_GC_MENFESS = "https://t.me/MenfessNABRUTT"
URL_GC_MOAN    = "https://t.me/MOAN18NABRUTT"
URL_GC_PAP     = "https://t.me/PAPCABULNABRUTT"

# HEADER IMAGE
IMG_PAP_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MENFESS_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_MOAN_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MOAN_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"

# ========== LOGGING ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== SETUP APLIKASI ==========
flask_app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# ================== /START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di Nabrutt 🤖\n\nPilih jenis kelaminmu dulu ya:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== CEK JOIN ==================
async def check_join(user_id, context: ContextTypes.DEFAULT_TYPE):
    groups = [
        (GROUP_NABRUTT, URL_NABRUTT),
        (CHANNEL_MENFESS_ID, URL_GC_MENFESS),
        (CHANNEL_PAP_ID, URL_GC_PAP),
        (CHANNEL_MOAN_ID, URL_GC_MOAN)
    ]
    not_joined = []
    for chat_id, url in groups:
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status in [ChatMember.LEFT, ChatMember.KICKED]:
                not_joined.append(url)
        except Exception as e:
            logger.warning(f"Check join error: {e}")
            not_joined.append(url)
    return not_joined

# ================== PILIH GENDER ==================
async def gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data.split("_")[1].upper()
    context.user_data["gender"] = gender

    not_joined = await check_join(query.from_user.id, context)
    if not_joined:
        buttons = [[InlineKeyboardButton(f"👉 Join {url.split('/')[-1]}", url=url)] for url in not_joined]
        buttons.append([InlineKeyboardButton("✅ Sudah Join Semua", callback_data="join_done")])
        await query.edit_message_text(
            f"Gender kamu: {gender} ✅\n\n⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await show_post_menu(query, gender)

async def show_post_menu(query, gender):
    keyboard = [
        [InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess")],
        [InlineKeyboardButton("📸 PapBRUTT", callback_data="post_pap")],
        [InlineKeyboardButton("🎙 MoanBRUTT", callback_data="post_moan")]
    ]
    await query.edit_message_text(
        "✅ Semua step sudah selesai!\n\nPilih jenis postingan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    gender = context.user_data.get("gender", "COWO")
    context.user_data["topik"] = data

    if data == "post_menfess":
        await query.edit_message_text("💌 Masukkan teks Menfess kamu:")
    elif data == "post_pap":
        keyboard = [
            [InlineKeyboardButton("📸 Foto", callback_data="pap_foto")],
            [InlineKeyboardButton("🎥 Video", callback_data="pap_video")]
        ]
        await query.edit_message_text("📸 Pilih tipe PAP:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "post_moan":
        await query.edit_message_text("🎙 Masukkan caption MOANBRUTT kamu:")

async def pap_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pap_type = query.data
    context.user_data["pap_type"] = pap_type
    await query.edit_message_text(f"Kamu memilih {pap_type.replace('pap_', '').upper()} untuk PAP. Kirim file sekarang.")

async def receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = context.user_data.get("gender", "COWO")
    topik = context.user_data.get("topik")
    pap_type = context.user_data.get("pap_type", "")
    text = update.message.text or ""
    media = None

    if update.message.voice:
        media = update.message.voice
    elif update.message.photo:
        media = update.message.photo[-1]
    elif update.message.video:
        media = update.message.video

    # Header image
    if topik == "post_menfess":
        header_img = IMG_MENFESS_COWO if gender == "COWO" else IMG_MENFESS_CEWE
        channel_id = CHANNEL_MENFESS_ID
        hashtag = f"#{gender} #MENFESSBRUTT"
        title = "💌 MENFESSBRUTT"
    elif topik == "post_pap":
        header_img = (IMG_PAP_COWO if gender == "COWO" else IMG_PAP_CEWE) if pap_type == "pap_foto" else (IMG_VIDEO_COWO if gender == "COWO" else IMG_VIDEO_CEWE)
        channel_id = CHANNEL_PAP_ID
        hashtag = f"#{gender} #PAPBRUTT"
        title = "📸 PAPBRUTT" if pap_type == "pap_foto" else "🎥 VIDEOBRUTT"
    else:
        header_img = IMG_MOAN_COWO if gender == "COWO" else IMG_MOAN_CEWE
        channel_id = CHANNEL_MOAN_ID
        hashtag = f"#{gender} #MOANBRUTT"
        title = "🎧 MOANBRUTT"

    caption = f"{title}\n\n> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**\n\n{text}\n\n⭐ Rate & 💬 Comment!\n\n{hashtag}"

    try:
        if update.message.photo:
            await context.bot.send_photo(channel_id, photo=media.file_id, caption=caption, parse_mode="Markdown")
        elif update.message.video:
            await context.bot.send_video(channel_id, video=media.file_id, caption=caption, parse_mode="Markdown")
        elif update.message.voice:
            await context.bot.send_voice(channel_id, voice=media.file_id, caption=caption, parse_mode="Markdown")
        else:
            await context.bot.send_message(channel_id, text=caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Gagal kirim ke channel: {e}")

    await update.message.reply_photo(
        photo=header_img,
        caption="✅ Postingan kamu berhasil dikirim!\n\nMau kirim apa lagi?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess")],
            [InlineKeyboardButton("📸 PapBRUTT", callback_data="post_pap")],
            [InlineKeyboardButton("🎙 MoanBRUTT", callback_data="post_moan")]
        ])
    )

bot_app.add_handler(CommandHandler("start", start, filters.ChatType.PRIVATE))
bot_app.add_handler(CallbackQueryHandler(gender_callback, pattern="^gender_"))
bot_app.add_handler(CallbackQueryHandler(post_callback, pattern="^post_"))
bot_app.add_handler(CallbackQueryHandler(pap_type_callback, pattern="^pap_"))
bot_app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO | filters.VIDEO, receive_content))

# ================== FLASK ENDPOINT (SINKRON) ==================
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot_app.bot)
        asyncio.run(bot_app.process_update(update))
        return "ok", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "error", 500

# ================== AUTO SET WEBHOOK ==================
def set_webhook():
    import requests
    url = f"{RENDER_URL}/{TOKEN}"
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}")
        if r.status_code == 200:
            logger.info(f"Webhook otomatis diset: {url}")
        else:
            logger.error(f"Gagal set webhook: {r.text}")
    except Exception as e:
        logger.error(f"Gagal set webhook otomatis: {e}")

# ================== RUN APP ==================
if __name__ == "__main__":
    set_webhook()
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
