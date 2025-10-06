# filename: nabrutt_bot_full_dual_webhook.py
# install dulu:
# pip install python-telegram-bot==20.3 Flask==2.3.3

import os, logging, asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatJoinRequestHandler,
    ContextTypes, filters
)
from zoneinfo import ZoneInfo

# ================== KONFIG TOKEN ==================
TOKEN_POSTING = "8466148433:AAEWIHjCONlIX5yVZgBj3WxaiM4jSLCVj5E"
TOKEN_WELCOME = "8490098646:AAHKK12F99k3nN3LrHCZlirzsIeelImpu6A"

# ================== KONFIG CHANNEL / GRUP ==================
CHANNEL_MENFESS_ID = -1002989043936
CHANNEL_PAP_ID     = -1003189592682
CHANNEL_MOAN_ID    = -1003196180758
URL_NABRUTT        = "https://t.me/+a3Bd3FDl5HY2NjFl"

IMG_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cowo.png"
IMG_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cewe.png"

# ================== WELCOME CONFIG ==================
LINKS = [
    ("🔥 GC 𝙉𝘼𝘽𝙍𝙐𝙏𝙏", "https://t.me/nabrutt11"),
    ("💌 CH 𝙈𝙀𝙉𝙁𝙀𝙎𝙎", "https://t.me/MenfessNabrutt"),
    ("📸 CH 𝙋𝘼𝙋𝘽𝙍𝙐𝙏𝙏", "https://t.me/papcabulnabrutt"),
    ("🔞 CH 𝙈𝙊𝘼𝙉", "https://t.me/Moan18Nabrutt"),
]
TIMEZONE = ZoneInfo("Asia/Jakarta")
AUTO_DELETE_SECONDS = 30

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== DATA ==================
user_data, emoji_counter, user_vote = {}, {}, {}

# ==========================================================
# ================== BOT 1: POSTING =========================
# ==========================================================
def format_gender(gender: str) -> str:
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def emoji_keyboard_initial(jenis):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍 0", callback_data=f"like|{jenis}"),
            InlineKeyboardButton("❤️ 0", callback_data=f"love|{jenis}"),
            InlineKeyboardButton("💦 0", callback_data=f"splash|{jenis}")
        ],
        [InlineKeyboardButton("👥 GC Nabrutt", url=URL_NABRUTT)]
    ])

async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

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

async def pilih_jenis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    jenis = q.data.replace("jenis_", "")
    user_data[q.from_user.id]["jenis"] = jenis
    await q.edit_message_text(f"Kirim konten untuk {jenis.upper()} sekarang!")

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
        ],
        [InlineKeyboardButton("👥 GC Nabrutt", url=URL_NABRUTT)]
    ])
    await q.message.edit_reply_markup(kb)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data: return
    jenis = user_data[uid]["jenis"]
    gender_raw = user_data[uid]["gender"]
    caption = update.message.caption or update.message.text or ""
    gender = format_gender(gender_raw)
    header_img = IMG_COWO if gender_raw == "cowo" else IMG_CEWE

    if jenis == "menfess":
        await context.bot.send_photo(
            CHANNEL_MENFESS_ID, photo=header_img,
            caption=f"💌 MENFESS 18+\n🕵️ Gender: {gender}\n\n{caption}",
            reply_markup=emoji_keyboard_initial("menfess"), has_spoiler=True
        )
    elif jenis == "pap" and update.message.photo:
        fid = update.message.photo[-1].file_id
        await context.bot.send_photo(
            CHANNEL_PAP_ID, photo=fid,
            caption=f"📸 PAPBRUTT\n🕵️ Gender: {gender}\n\n{caption}",
            reply_markup=emoji_keyboard_initial("pap"), has_spoiler=True
        )
    elif jenis == "moan" and update.message.voice:
        fid = update.message.voice.file_id
        await context.bot.send_voice(
            CHANNEL_MOAN_ID, voice=fid,
            caption=f"🎙 MOANBRUTT\n🕵️ Gender: {gender}\n\n{caption}",
            reply_markup=emoji_keyboard_initial("moan")
        )

def create_app_posting():
    app = Application.builder().token(TOKEN_POSTING).build()
    app.add_handler(CommandHandler("start", start_post))
    app.add_handler(CallbackQueryHandler(pilih_gender, "^gender_"))
    app.add_handler(CallbackQueryHandler(pilih_jenis, "^jenis_"))
    app.add_handler(CallbackQueryHandler(handle_emoji, "^(like|love|splash)\|"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    return app

# ==========================================================
# ================== BOT 2: WELCOME =========================
# ==========================================================
def build_links_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(t, url=u)] for t, u in LINKS])

async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    await req.approve()
    user = req.from_user
    await context.bot.send_message(
        req.chat.id,
        text=f"🌟 Selamat datang {user.mention_html()}!\nKlik tombol di bawah untuk akses semua area!",
        parse_mode="HTML",
        reply_markup=build_links_keyboard()
    )

def create_app_welcome():
    app = Application.builder().token(TOKEN_WELCOME).build()
    app.add_handler(ChatJoinRequestHandler(join_request_handler))
    return app

# ==========================================================
# ================== FLASK SERVER ==========================
# ==========================================================
flask_app = Flask(__name__)
posting_app = create_app_posting()
welcome_app = create_app_welcome()

@flask_app.route("/")
def home():
    return "🚀 NABRUTT BOT Webhook aktif!"

@flask_app.route("/posting", methods=["POST"])
async def webhook_posting():
    update = Update.de_json(await request.get_json(force=True), posting_app.bot)
    await posting_app.process_update(update)
    return "ok"

@flask_app.route("/welcome", methods=["POST"])
async def webhook_welcome():
    update = Update.de_json(await request.get_json(force=True), welcome_app.bot)
    await welcome_app.process_update(update)
    return "ok"

# ==========================================================
# ================== SETUP & RUN ==========================
# ==========================================================
async def setup_webhooks():
    # Ambil URL otomatis dari Render
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "https://nabrutt-bot.onrender.com")
    base_url = base_url.rstrip("/")
    await posting_app.bot.set_webhook(f"{base_url}/posting")
    await welcome_app.bot.set_webhook(f"{base_url}/welcome")
    logger.info(f"✅ Webhook diset ke {base_url}")

if __name__ == "__main__":
    asyncio.run(setup_webhooks())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
