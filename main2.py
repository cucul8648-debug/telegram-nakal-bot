# filename: main.py
# requirements:
# python-telegram-bot==20.3
# Flask==2.3.3

import os, logging, asyncio, threading
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from zoneinfo import ZoneInfo

# ================== TOKEN ==================
TOKEN_POSTING = "8466148433:AAEpJ5tdgjCft5wvBRa7TNUa205u2gFhLBE"

# ================== CHANNEL & GROUP ==================
CHANNEL_MENFESS_ID = -1002989043936
CHANNEL_PAP_ID     = -1003189592682
CHANNEL_MOAN_ID    = -1003196180758
GROUP_NABRUTT_ID   = -1003098333444
URL_NABRUTT        = "https://t.me/+a3Bd3FDl5HY2NjFl"

IMG_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cowo.png"
IMG_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cewe.png"

TIMEZONE = ZoneInfo("Asia/Jakarta")

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== DATA ==================
user_data, emoji_counter, user_vote = {}, {}, {}

# ================== UTIL ==================
def format_gender(gender: str) -> str:
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def emoji_keyboard_initial(jenis):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍 0", callback_data=f"like|{jenis}"),
            InlineKeyboardButton("❤️ 0", callback_data=f"love|{jenis}"),
            InlineKeyboardButton("💦 0", callback_data=f"splash|{jenis}")
        ]
    ])

# ================== CEK WAJIB JOIN ==================
async def is_member(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(GROUP_NABRUTT_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning(f"Gagal cek member: {e}")
        return False

# ================== START ==================
async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_member(context, user_id):
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("Gabung dulu ke GC 🔥", url=URL_NABRUTT)]])
        await update.message.reply_text("⚠️ Kamu harus join GC Nabrutt dulu sebelum posting.", reply_markup=btn)
        return

    kb = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================== PILIH GENDER ==================
async def pilih_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    gender = q.data.replace("gender_", "")
    user_data[q.from_user.id] = {"gender": gender}
    kb = [
        [InlineKeyboardButton("💌 Menfess", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan", callback_data="jenis_moan")]
    ]
    await q.edit_message_text(
        f"Gender kamu: {format_gender(gender)} ✅\n\nPilih jenis posting:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================== PILIH JENIS ==================
async def pilih_jenis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    jenis = q.data.replace("jenis_", "")
    user_data[q.from_user.id]["jenis"] = jenis
    await q.edit_message_text(f"Kirim konten untuk {jenis.upper()} sekarang!")

# ================== REACT EMOJI ==================
async def handle_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid, mid = q.from_user.id, q.message.message_id
    action, jenis = q.data.split("|", 1)

    if (mid, uid) in user_vote:
        await q.answer("Kamu sudah vote.", show_alert=True)
        return

    user_vote[(mid, uid)] = action
    emoji_counter.setdefault(mid, {"👍":0,"❤️":0,"💦":0})
    if action == "like": emoji_counter[mid]["👍"] += 1
    elif action == "love": emoji_counter[mid]["❤️"] += 1
    elif action == "splash": emoji_counter[mid]["💦"] += 1
    c = emoji_counter[mid]

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"👍 {c['👍']}", callback_data=f"like|{jenis}"),
            InlineKeyboardButton(f"❤️ {c['❤️']}", callback_data=f"love|{jenis}"),
            InlineKeyboardButton(f"💦 {c['💦']}", callback_data=f"splash|{jenis}")
        ]
    ])
    await q.message.edit_reply_markup(kb)

# ================== HANDLE PESAN ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data: return
    jenis = user_data[uid]["jenis"]
    gender_raw = user_data[uid]["gender"]
    caption = update.message.caption or update.message.text or ""
    gender = format_gender(gender_raw)
    header_img = IMG_COWO if gender_raw == "cowo" else IMG_CEWE

    # Format caption rapi
    if jenis == "menfess":
        cap = f"💌 MENFESS 18+\n Gender 🕵️: {gender}\n\n{caption}"
        await context.bot.send_photo(CHANNEL_MENFESS_ID, photo=header_img, caption=cap, reply_markup=emoji_keyboard_initial("menfess"), has_spoiler=True)

    elif jenis == "pap" and update.message.photo:
        fid = update.message.photo[-1].file_id
        cap = f"📸 PAP {gender.split()[0]}\nGender: {gender}\n\n{caption}\n\n💬 Berikan react dan nilai!\n⭐ Rate 1–10\n\n#{gender.split()[0]}"
        await context.bot.send_photo(CHANNEL_PAP_ID, photo=fid, caption=cap, reply_markup=emoji_keyboard_initial("pap"), has_spoiler=True)

    elif jenis == "moan" and update.message.voice:
        fid = update.message.voice.file_id
        cap = f"🎙 MOANBRUTT\n Gender 🕵️: {gender}\n\n{caption}"
        await context.bot.send_voice(CHANNEL_MOAN_ID, voice=fid, caption=cap, reply_markup=emoji_keyboard_initial("moan"))

# ================== BOT POSTING ==================
def create_app_posting():
    app = Application.builder().token(TOKEN_POSTING).build()
    app.add_handler(CommandHandler("start", start_post))
    app.add_handler(CallbackQueryHandler(pilih_gender, "^gender_"))
    app.add_handler(CallbackQueryHandler(pilih_jenis, "^jenis_"))
    app.add_handler(CallbackQueryHandler(handle_emoji, r"^(like|love|splash)\|"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    return app

# ================== FLASK SERVER ==================
flask_app = Flask(__name__)
posting_app = create_app_posting()

loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

@flask_app.route("/")
def home():
    return "🚀 NABRUTT BOT POSTING aktif!"

@flask_app.route("/posting", methods=["POST"])
def webhook_posting():
    update = Update.de_json(request.get_json(force=True), posting_app.bot)
    asyncio.run_coroutine_threadsafe(posting_app.process_update(update), loop)
    return "ok", 200

# ================== SETUP WEBHOOK ==================
async def setup_webhook():
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "https://telegram-nakal-bot.onrender.com").rstrip("/")
    await posting_app.bot.set_webhook(f"{base_url}/posting")
    logger.info(f"✅ Webhook diset ke {base_url}")

# ================== MAIN ==================
if __name__ == "__main__":
    async def main():
        await posting_app.initialize()
        await setup_webhook()
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    asyncio.run(main())
