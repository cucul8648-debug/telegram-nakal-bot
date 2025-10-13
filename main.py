# filename: main.py
# deploy: pip install -r requirements.txt
# run: python main.py

import os
import logging
import asyncio
import threading
from flask import Flask, request, abort
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ---------------- CONFIG ----------------
# Use BOT_TOKEN env var (Render) or fallback to the token you provided
TOKEN = os.environ.get("BOT_TOKEN", "8466148433:AAH9NFT_wrkBlZ-uO8hllAdxdTwFpLqip74")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://telegram-nakal-bot-1.onrender.com")
WEBHOOK_PATH = f"/{TOKEN}"
PORT = int(os.environ.get("PORT", 10000))

# Group + thread IDs (keep as provided)
GROUP_NABRUTT = int(os.environ.get("GROUP_NABRUTT", -1003098333444))
THREAD_MENFESS = int(os.environ.get("THREAD_MENFESS", 1036))
THREAD_PAP = int(os.environ.get("THREAD_PAP", 393))
THREAD_MOAN = int(os.environ.get("THREAD_MOAN", 2298))

# Channel IDs
CHANNEL_MENFESS_ID = int(os.environ.get("CHANNEL_MENFESS_ID", -1002989043936))
CHANNEL_PAP_ID = int(os.environ.get("CHANNEL_PAP_ID", -1003189592682))
CHANNEL_MOAN_ID = int(os.environ.get("CHANNEL_MOAN_ID", -1003196180758))

# GitHub RAW header image URLs (unchanged)
IMG_PAP_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MENFESS_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_MOAN_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MOAN_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"

# URLs for join links (used in messages)
URL_NABRUTT = "https://t.me/NABRUTT11"
URL_GC_MENFESS = "https://t.me/MenfessNABRUTT"
URL_GC_PAP = "https://t.me/PAPCABULNABRUTT"
URL_GC_MOAN = "https://t.me/MOAN18NABRUTT"

# ---------------- Logging ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- Flask app for webhook ----------------
flask_app = Flask(__name__)

# ---------------- Helpers / Keyboards ----------------
def build_start_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo"),
        InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")
    ]])

def build_join_buttons(not_joined_urls):
    buttons = [[InlineKeyboardButton("👉 Join", url=url)] for url in not_joined_urls]
    buttons.append([InlineKeyboardButton("✅ Sudah Join Semua", callback_data="join_done")])
    return InlineKeyboardMarkup(buttons)

def build_post_menu():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess"),
        InlineKeyboardButton("📸 PapBRUTT", callback_data="post_pap"),
        InlineKeyboardButton("🎧 MoanBRUTT", callback_data="post_moan")
    ]])

def build_pap_type_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📷 Foto", callback_data="pap_foto"),
        InlineKeyboardButton("🎥 Video", callback_data="pap_video")
    ]])

def build_retry_menu():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess"),
        InlineKeyboardButton("📸 PapBRUTT", callback_data="post_pap"),
        InlineKeyboardButton("🎧 MoanBRUTT", callback_data="post_moan")
    ]])

async def check_all_membership(bot: Bot, user_id: int):
    """
    Return list of URLs the user hasn't joined (empty => all joined).
    If bot can't check (e.g. private channel or not admin), we include URL to force manual join.
    """
    checks = [
        (GROUP_NABRUTT, URL_NABRUTT),
        (CHANNEL_MENFESS_ID, URL_GC_MENFESS),
        (CHANNEL_PAP_ID, URL_GC_PAP),
        (CHANNEL_MOAN_ID, URL_GC_MOAN)
    ]
    not_joined = []
    for chat_id, url in checks:
        try:
            mem = await bot.get_chat_member(chat_id, user_id)
            if mem.status not in ["member", "administrator", "creator"]:
                not_joined.append(url)
        except Exception:
            # Can't verify -> ask user to join manually
            not_joined.append(url)
    return not_joined

def topik_emoji(topik_key, pap_type=None):
    if topik_key == "MENFESS":
        return "💌"
    if topik_key == "PAP":
        return "📸" if pap_type == "pap_foto" else "🎥"
    if topik_key == "MOAN":
        return "🎧"
    return ""

def topik_title(topik_key, pap_type=None):
    if topik_key == "MENFESS":
        return "MENFESSBRUTT"
    if topik_key == "PAP":
        return "PAPBRUTT" if pap_type == "pap_foto" else "VIDEOBRUTT"
    if topik_key == "MOAN":
        return "MOANBRUTT"
    return topik_key

def header_image_url(topik_key, gender, pap_type=None):
    if topik_key == "MENFESS":
        return IMG_MENFESS_COWO if gender == "COWO" else IMG_MENFESS_CEWE
    if topik_key == "PAP":
        if pap_type == "pap_video":
            return IMG_VIDEO_COWO if gender == "COWO" else IMG_VIDEO_CEWE
        else:
            return IMG_PAP_COWO if gender == "COWO" else IMG_PAP_CEWE
    if topik_key == "MOAN":
        return IMG_MOAN_COWO if gender == "COWO" else IMG_MOAN_CEWE
    return ""

def format_channel_caption(topik_title_str, emoji_str, gender, caption_text):
    return (
        f"**{topik_title_str} {emoji_str}**\n\n"
        f"> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**\n\n"
        f"{caption_text.strip()}\n\n"
        f"> **BERIKAN REACT DAN NILAI!**\n"
        f"> **⭐ RATE 1–10**\n"
        f"> **💬 COMMENT!**\n\n"
        f"#{gender} #{topik_title_str}"
    )

# ---------------- Handlers ----------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Selamat datang di EksibNih 🤖**\n\n> Pilih jenis kelaminmu dulu ya:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=build_start_keyboard()
    )

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # Gender selection
    if data.startswith("gender_"):
        gender = "COWO" if data == "gender_cowo" else "CEWE"
        context.user_data["gender"] = gender

        # Check join
        not_joined = await check_all_membership(context.bot, user_id)
        if not_joined:
            # show join list and ask to confirm
            text = (
                f"**Gender kamu: {gender} ✅**\n\n"
                f"> ⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:\n\n"
                f"> 👉 {URL_NABRUTT}\n"
                f"> 👉 {URL_GC_MENFESS}\n"
                f"> 👉 {URL_GC_PAP}\n"
                f"> 👉 {URL_GC_MOAN}\n\n"
                f"> Jika sudah join semua, klik tombol di bawah 👇"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=build_join_buttons(not_joined))
            return

        # else show post menu
        await query.edit_message_text(
            "**✅ Semua step sudah selesai!**\n\n> Pilih jenis postingan:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_post_menu()
        )
        return

    # after user clicked join_done
    if data == "join_done":
        not_joined = await check_all_membership(context.bot, user_id)
        if not_joined:
            await query.answer("Kamu belum join semua group/channel. Cek link yang muncul.", show_alert=True)
            return
        await query.edit_message_text(
            "**✅ Semua step sudah selesai!**\n\n> Pilih jenis postingan:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=build_post_menu()
        )
        return

    # Post menu
    if data == "post_menfess":
        context.user_data["topik"] = "MENFESS"
        await query.message.reply_text("💌 Kamu memilih **MENFESSBRUTT**.\n\n> Kirim teks menfess kamu sekarang:", parse_mode=ParseMode.MARKDOWN)
        return

    if data == "post_pap":
        await query.message.reply_text("📸 Kamu memilih **PAPBRUTT**.\n\n> Pilih tipe yang mau kamu kirim:", parse_mode=ParseMode.MARKDOWN, reply_markup=build_pap_type_keyboard())
        return

    if data == "pap_foto":
        context.user_data["topik"] = "PAP"
        context.user_data["pap_type"] = "pap_foto"
        await query.message.reply_text("📷 Kamu memilih **PAP FOTO**.\n\n> Kirim foto kamu sekarang!", parse_mode=ParseMode.MARKDOWN)
        return

    if data == "pap_video":
        context.user_data["topik"] = "PAP"
        context.user_data["pap_type"] = "pap_video"
        await query.message.reply_text("🎥 Kamu memilih **PAP VIDEO**.\n\n> Kirim video kamu sekarang!", parse_mode=ParseMode.MARKDOWN)
        return

    if data == "post_moan":
        context.user_data["topik"] = "MOAN"
        context.user_data["awaiting_moan_caption"] = True
        await query.message.reply_text("🎙 Kamu memilih **MOANBRUTT**.\n\n> Masukkan caption :", parse_mode=ParseMode.MARKDOWN)
        return

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles text, photos, videos, voice.
    State machine relies on context.user_data.
    """
    # ignore non-message updates
    if not update.message:
        return

    user = update.message.from_user
    uid = user.id
    data = context.user_data
    topik = data.get("topik")
    pap_type = data.get("pap_type")
    gender = data.get("gender", "COWO")  # fallback

    # If user is in MOAN caption step
    if data.get("awaiting_moan_caption"):
        caption_text = update.message.text or ""
        data["moan_caption"] = caption_text
        data["awaiting_moan_caption"] = False
        data["awaiting_moan_media"] = True
        await update.message.reply_text("✅ Caption berhasil dimasukkan!\n\n> Sekarang kirim moan yang kamu inginkan 🎧", parse_mode=ParseMode.MARKDOWN)
        return

    # If waiting for MOAN media (voice)
    if data.get("awaiting_moan_media"):
        if update.message.voice:
            caption_text = data.get("moan_caption", "")
            await publish_post(update, context, topik="MOAN", media_type="voice", gender=gender, caption_text=caption_text)
            # reset
            data.pop("awaiting_moan_media", None)
            data.pop("moan_caption", None)
            data.pop("topik", None)
            return
        else:
            await update.message.reply_text("⚠️ Mohon kirim *voice note* untuk MOAN (file voice).", parse_mode=ParseMode.MARKDOWN)
            return

    # Normal flows (Menfess, Pap)
    if topik == "MENFESS":
        content = update.message.text or ""
        await publish_post(update, context, topik="MENFESS", media_type=None, gender=gender, caption_text=content)
        data.pop("topik", None)
        return

    if topik == "PAP":
        if pap_type == "pap_foto" and update.message.photo:
            caption_text = update.message.caption or ""
            await publish_post(update, context, topik="PAP", media_type="photo", gender=gender, caption_text=caption_text)
            data.pop("topik", None)
            data.pop("pap_type", None)
            return
        if pap_type == "pap_video" and update.message.video:
            caption_text = update.message.caption or ""
            await publish_post(update, context, topik="PAP", media_type="video", gender=gender, caption_text=caption_text)
            data.pop("topik", None)
            data.pop("pap_type", None)
            return
        await update.message.reply_text("⚠️ Silakan kirim file sesuai tipe yang dipilih (Foto/Video).", parse_mode=ParseMode.MARKDOWN)
        return

    # If nothing matched
    await update.message.reply_text("⚠️ Silakan gunakan menu /start untuk memulai posting.", parse_mode=ParseMode.MARKDOWN)

async def publish_post(update: Update, context: ContextTypes.DEFAULT_TYPE, topik: str, media_type: str, gender: str, caption_text: str):
    """
    Send preview to thread (with GitHub header image), then send full to channel (file-asli with has_spoiler=True where relevant).
    """
    pap_type = context.user_data.get("pap_type", "")
    emoji = topik_emoji(topik, pap_type=pap_type)
    title = topik_title(topik, pap_type=pap_type)
    header_url = header_image_url(topik, gender, pap_type=pap_type)

    # THREAD preview content (header image from GitHub, displayed directly; no 2x tap)
    thread_caption = (
        f"**{title} {emoji}**\n\n"
        f"> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**\n\n"
        f"{caption_text}\n\n"
        f"👉 Klik tombol untuk lihat full di channel"
    )

    thread_map = {"MENFESS": THREAD_MENFESS, "PAP": THREAD_PAP, "MOAN": THREAD_MOAN}
    thread_id = thread_map.get(topik, THREAD_MENFESS)

    try:
        # send header image to group thread
        await context.bot.send_photo(
            chat_id=GROUP_NABRUTT,
            photo=header_url,
            caption=thread_caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📨 Lihat Full", url=f"{WEBHOOK_URL}/channel-link-placeholder")]]),
            message_thread_id=thread_id
        )
    except Exception as e:
        logger.exception("Failed to send thread preview: %s", e)
        # fallback: send text to thread
        try:
            await context.bot.send_message(chat_id=GROUP_NABRUTT, text=thread_caption, parse_mode=ParseMode.MARKDOWN, message_thread_id=thread_id)
        except Exception:
            logger.exception("Also failed to send fallback thread message")

    # CHANNEL full post (file asli)
    channel_caption = format_channel_caption(title, emoji, gender, caption_text)

    channel_id_map = {"MENFESS": CHANNEL_MENFESS_ID, "PAP": CHANNEL_PAP_ID, "MOAN": CHANNEL_MOAN_ID}
    channel_id = channel_id_map.get(topik, CHANNEL_MENFESS_ID)

    try:
        if media_type == "photo" and update.message.photo:
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(chat_id=channel_id, photo=file_id, caption=channel_caption, parse_mode=ParseMode.MARKDOWN, has_spoiler=True)
        elif media_type == "video" and update.message.video:
            await context.bot.send_video(chat_id=channel_id, video=update.message.video.file_id, caption=channel_caption, parse_mode=ParseMode.MARKDOWN, has_spoiler=True)
        elif media_type == "voice" and update.message.voice:
            await context.bot.send_voice(chat_id=channel_id, voice=update.message.voice.file_id, caption=channel_caption, parse_mode=ParseMode.MARKDOWN, has_spoiler=True)
        else:
            # text (menfess)
            await context.bot.send_message(chat_id=channel_id, text=channel_caption, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.exception("Failed to send to channel: %s", e)
        try:
            await update.message.reply_text("⚠️ Gagal mengirim ke channel. Cek log server.", parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass

    # Affirmation to user in private chat + retry menu
    try:
        await update.message.reply_text("✅ **Postingan kamu berhasil dikirim!**\n\n> Mau kirim apa lagi?", parse_mode=ParseMode.MARKDOWN, reply_markup=build_retry_menu())
    except Exception:
        logger.exception("Failed to send confirmation to user")

# ---------------- Flask webhook endpoint ----------------
@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.method != "POST":
        abort(400)
    update_json = request.get_json(force=True)
    update = Update.de_json(update_json, application.bot)
    try:
        asyncio.run(application.process_update(update))
    except Exception:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(application.process_update(update))
        except Exception:
            logger.exception("Failed to process update")
    return "OK"

@flask_app.route("/", methods=["GET"])
def home():
    return "Bot is running."

# ---------------- Main ----------------
if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(MessageHandler(filters.ALL, message_handler))

    # Start Flask in background thread
    def run_flask():
        flask_app.run(host="0.0.0.0", port=PORT)
    threading.Thread(target=run_flask).start()

    webhook_full = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    logger.info("Setting webhook to %s", webhook_full)

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_full
    )
