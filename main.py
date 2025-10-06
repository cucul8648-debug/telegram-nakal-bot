# filename: nabrutt_webhook.py
# install dulu:
# pip install python-telegram-bot==20.3 Flask==2.3.3

import os, asyncio, logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ================== KONFIG ==================
TOKEN = "8466148433:AAEsWgCp4dq8kqpsaPQko1yO4rjkT_HgRe0"

# GROUP + THREAD
GROUP_NABRUTT  = -1003098333444
THREAD_MENFESS = 1036
THREAD_PAP     = 393
THREAD_MOAN    = 2010

# CHANNEL
CHANNEL_MENFESS_ID = -1002989043936
CHANNEL_PAP_ID     = -1003189592682
CHANNEL_MOAN_ID    = -1003196180758

# URL Join / Redirect
URL_MENFESS    = "https://t.me/MenfessNABRUTT"
URL_PAP        = "https://t.me/PAPCABULNABRUTT"
URL_MOAN       = "https://t.me/MOAN18NABRUTT"
URL_NABRUTT    = "https://t.me/+a3Bd3FDl5HY2NjFl"
URL_GC_MENFESS = "https://t.me/+dD-sAhjjsJgxZGVl"
URL_GC_MOAN    = "https://t.me/+s8kHZK1gSKI3MWJl"
URL_GC_PAP     = "https://t.me/+c8BmNNzdXqo3NjFl"

# HEADER IMAGE (GitHub raw)
IMG_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cowo.png"
IMG_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cewe.png"

# SIMPAN DATA USER
user_data     = {}
emoji_counter = {}
user_vote     = {}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- HELPER ----------
def format_gender(gender: str) -> str:
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def static_comment_buttons(jenis: str):
    if jenis == "menfess": komentar_url = URL_GC_MENFESS
    elif jenis == "pap":   komentar_url = URL_GC_PAP
    elif jenis == "moan":  komentar_url = URL_GC_MOAN
    else: komentar_url = URL_NABRUTT
    return [[
        InlineKeyboardButton("💬 Komentar", url=komentar_url),
        InlineKeyboardButton("👥 GC Nabrutt", url=URL_NABRUTT)
    ]]

def emoji_buttons_only(counts, jenis):
    return [[
        InlineKeyboardButton(f"👍 {counts['👍']}", callback_data=f"like|{jenis}"),
        InlineKeyboardButton(f"❤️ {counts['❤️']}", callback_data=f"love|{jenis}"),
        InlineKeyboardButton(f"💦 {counts['💦']}", callback_data=f"splash|{jenis}")
    ]]

def emoji_keyboard_initial(jenis):
    return InlineKeyboardMarkup(
        emoji_buttons_only({"👍":0,"❤️":0,"💦":0}, jenis) + static_comment_buttons(jenis)
    )

async def is_member(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def check_all_membership(bot, uid):
    return all([
        await is_member(bot, CHANNEL_MENFESS_ID, uid),
        await is_member(bot, CHANNEL_PAP_ID, uid),
        await is_member(bot, CHANNEL_MOAN_ID, uid),
        await is_member(bot, GROUP_NABRUTT, uid),
    ])

# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu ya:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def pilih_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data.replace("gender_", "")
    user_data[query.from_user.id] = {"gender": gender}
    uid = query.from_user.id
    if not await check_all_membership(context.bot, uid):
        keyboard = [
            [InlineKeyboardButton("👉 Join Group Nabrutt", url=URL_NABRUTT)],
            [InlineKeyboardButton("👉 Join Channel Menfess", url=URL_MENFESS)],
            [InlineKeyboardButton("👉 Join Channel PAP", url=URL_PAP)],
            [InlineKeyboardButton("👉 Join Channel Moan", url=URL_MOAN)],
            [InlineKeyboardButton("✅ Sudah Join Semua", callback_data="cek_join")]
        ]
        await query.edit_message_text(
            f"Gender kamu: {gender.upper()} ✅\n\n⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await tampilkan_menu(query)

async def cek_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_all_membership(context.bot, query.from_user.id):
        await tampilkan_menu(query)
    else:
        await query.edit_message_text("❌ Kamu belum join semua group/channel.\n\nSilakan join dulu baru lanjut.")

async def tampilkan_menu(query):
    keyboard = [
        [InlineKeyboardButton("💌 Menfess 18+", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap Cabul",   callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan 18+",    callback_data="jenis_moan")]
    ]
    await query.edit_message_text("✅ Semua step sudah selesai!\n\nPilih jenis postingan:", reply_markup=InlineKeyboardMarkup(keyboard))

async def pilih_jenis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    jenis = query.data.replace("jenis_", "")
    uid = query.from_user.id
    user_data.setdefault(uid, {})["jenis"] = jenis

    if jenis == "menfess":
        await query.edit_message_text("💌 Kamu memilih *MENFESS*.\n\nKirim teks menfess sekarang!", parse_mode="Markdown")
    elif jenis == "pap":
        keyboard = [
            [InlineKeyboardButton("📸 Foto",  callback_data="pap_foto")],
            [InlineKeyboardButton("🎥 Video", callback_data="pap_video")]
        ]
        await query.edit_message_text("📸 Kamu memilih *PAP*.\n\nPilih tipe:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text("🎙 Kamu memilih *MOAN*.\n\nKirim voice note + caption (opsional).", parse_mode="Markdown")

async def pilih_pap_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipe = query.data.replace("pap_", "")
    user_data[query.from_user.id]["pap_type"] = tipe
    await query.edit_message_text(f"✅ Kamu memilih PAP tipe *{tipe.upper()}*.\n\nKirim {tipe} sekarang!", parse_mode="Markdown")

async def handle_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid   = query.from_user.id
    mid   = query.message.message_id
    await query.answer()
    action, jenis = query.data.split("|", 1)
    if (mid, uid) in user_vote:
        await query.answer("❌ Kamu sudah memilih emoji.", show_alert=True)
        return
    user_vote[(mid, uid)] = action
    if mid not in emoji_counter:
        emoji_counter[mid] = {"👍": 0, "❤️": 0, "💦": 0}
    if action == "like": emoji_counter[mid]["👍"] += 1
    elif action == "love": emoji_counter[mid]["❤️"] += 1
    elif action == "splash": emoji_counter[mid]["💦"] += 1
    c = emoji_counter[mid]
    await query.message.edit_reply_markup(
        InlineKeyboardMarkup(emoji_buttons_only(c, jenis) + static_comment_buttons(jenis))
    )

# ---- Handle pesan tetap sama ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # (fungsi kamu yang panjang tadi tetap sama, tidak diubah sama sekali)
    pass  # <-- isi fungsi kamu yang asli di sini

# ========== BAGIAN BARU UNTUK WEBHOOK ==========
flask_app = Flask(__name__)
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(pilih_gender, pattern="^gender_"))
app.add_handler(CallbackQueryHandler(cek_join,    pattern="^cek_join$"))
app.add_handler(CallbackQueryHandler(pilih_jenis, pattern="^jenis_"))
app.add_handler(CallbackQueryHandler(pilih_pap_type, pattern="^pap_"))
app.add_handler(CallbackQueryHandler(handle_emoji,   pattern="^(like|love|splash)\|"))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

@flask_app.route("/")
def home():
    return "✅ Nabrutt Bot Webhook Aktif!"

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    asyncio.create_task(app.process_update(update))
    return "ok"

async def setup_webhook():
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "https://telegram-nabrutt-bot.onrender.com").rstrip("/")
    webhook_url = f"{base_url}/webhook"
    await app.bot.set_webhook(webhook_url)
    print(f"✅ Webhook diset ke: {webhook_url}")

if __name__ == "__main__":
    async def main():
        await app.initialize()
        await setup_webhook()
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    asyncio.run(main())
