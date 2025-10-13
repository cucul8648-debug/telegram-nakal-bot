# filename: eksibnih_webhook.py
# install di requirements.txt:
# python-telegram-bot==20.3
# Flask==2.3.3

import os, logging, asyncio, threading
from flask import Flask, request
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ========== KONFIGURASI ==========
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "https://your-render-app-url.onrender.com")
CHANNELS = {
    "MENFESS": "@menfess_channel",
    "PAP": "@pap_channel",
    "MOAN": "@moan_channel"
}
THREAD_GROUP = "@nabrutt_group"

# Header image GitHub RAW
HEADER_IMAGES = {
    "MENFESS_COWO": "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/header_menfess_cowo.jpg",
    "MENFESS_CEWE": "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/header_menfess_cewe.jpg",
    "PAP_COWO": "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/header_pap_cowo.jpg",
    "PAP_CEWE": "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/header_pap_cewe.jpg",
    "MOAN_COWO": "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/header_moan_cowo.jpg",
    "MOAN_CEWE": "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/header_moan_cewe.jpg",
}

# ========== FLASK SERVER ==========
app = Flask(__name__)
application = None  # akan diisi setelah setup bot

@app.route("/" + TOKEN, methods=["POST"])
def webhook_update():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/")
def index():
    return "EksibNih Bot Webhook Aktif ✅"

# ========== HANDLER FUNGSI ==========
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo"),
            InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")
        ]
    ]
    await update.message.reply_text(
        "**Selamat datang di EksibNih 🤖**\n\n"
        "Pilih jenis kelaminmu dulu ya:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def gender_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = "COWO" if "cowo" in query.data else "CEWE"
    user_data[query.from_user.id] = {"gender": gender}

    # Cek join group/channel
    keyboard = [
        [InlineKeyboardButton("👉 Join Group Nabrutt", url="https://t.me/nabrutt_group")],
        [InlineKeyboardButton("👉 Join Channel Menfess", url="https://t.me/menfess_channel")],
        [InlineKeyboardButton("👉 Join Channel PAP", url="https://t.me/pap_channel")],
        [InlineKeyboardButton("👉 Join Channel Moan", url="https://t.me/moan_channel")],
        [InlineKeyboardButton("✅ Sudah Join Semua", callback_data="joined_all")]
    ]
    await query.message.reply_text(
        f"**Gender kamu:** {gender} ✅\n\n"
        "⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def joined_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("💌 MenfessBrutt", callback_data="topik_menfess"),
            InlineKeyboardButton("📸 PapBrutt", callback_data="topik_pap"),
            InlineKeyboardButton("🎙 MoanBrutt", callback_data="topik_moan")
        ]
    ]
    await query.message.reply_text(
        "✅ Semua step sudah selesai!\n\n"
        "**Pilih jenis postingan:**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def pilih_topik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = user_data.get(query.from_user.id, {})
    gender = user.get("gender", "COWO")

    if query.data == "topik_menfess":
        await query.message.reply_text("💌 Kamu memilih **MENFESSBRUTT**.\n\nMasukkan caption menfess kamu:")
        user["mode"] = "MENFESS"

    elif query.data == "topik_pap":
        keyboard = [
            [
                InlineKeyboardButton("🖼 Foto", callback_data="pap_foto"),
                InlineKeyboardButton("🎥 Video", callback_data="pap_video")
            ]
        ]
        await query.message.reply_text(
            "📸 Kamu memilih **PAPBRUTT**.\n\nPilih tipe PAP yang ingin kamu kirim:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "topik_moan":
        await query.message.reply_text("🎙 Kamu memilih **MOANBRUTT**.\n\nMasukkan caption :", parse_mode="Markdown")
        user["mode"] = "MOAN"

    user_data[query.from_user.id] = user
    await query.answer()

async def pap_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = user_data.get(query.from_user.id, {})
    user["mode"] = "PAP_FOTO" if "foto" in query.data else "PAP_VIDEO"
    user_data[query.from_user.id] = user

    tipe = "foto" if "foto" in query.data else "video"
    await query.message.reply_text(
        f"📸 Kirim {tipe} PAP kamu sekarang!",
        parse_mode="Markdown"
    )

async def handle_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = user_data.get(update.effective_user.id, {})
    mode = user.get("mode")

    if mode in ["MENFESS", "MOAN"]:
        user["caption"] = update.message.text
        user_data[update.effective_user.id] = user

        if mode == "MENFESS":
            await update.message.reply_text("✅ Caption berhasil disimpan.\n\nKirim menfess kamu sekarang!")
        elif mode == "MOAN":
            await update.message.reply_text(
                "✅ *Caption berhasil dimasukkan!*\n\n"
                "Sekarang kirim *moan* yang kamu inginkan 🎙",
                parse_mode="Markdown"
            )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = user_data.get(update.effective_user.id, {})
    mode = user.get("mode")
    gender = user.get("gender", "COWO")

    if not mode:
        return await update.message.reply_text("Gunakan /start dulu untuk memulai.")

    caption = user.get("caption", "")
    # === THREAD OUTPUT ===
    header_key = f"{mode.split('_')[0]}_{gender}"
    header_url = HEADER_IMAGES.get(header_key, "")
    if header_url:
        await context.bot.send_photo(
            chat_id=THREAD_GROUP,
            photo=header_url,
            caption=(
                f"**{mode.replace('_','')} 💌📸🎧**\n\n"
                f"> **GENDER 🕵️ : {gender}**\n\n"
                f"{caption}\n\n"
                f"> 👉 Klik tombol untuk lihat full di channel"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 Lihat Full", url=f"https://t.me/{CHANNELS[mode.split('_')[0]]}")]]
            )
        )

    # === CHANNEL OUTPUT ===
    file = update.message.photo[-1].file_id if update.message.photo else (
        update.message.video.file_id if update.message.video else (
            update.message.voice.file_id if update.message.voice else None
        )
    )
    if file:
        await context.bot.copy_message(
            chat_id=CHANNELS[mode.split('_')[0]],
            from_chat_id=update.message.chat_id,
            message_id=update.message.id,
            caption=(
                f"**{mode.replace('_','')} 💌📸🎧**\n\n"
                f"> **GENDER 🕵️ : {gender}**\n\n"
                f"{caption}\n\n"
                f"> **BERIKAN REACT DAN NILAI!**\n"
                f"> ⭐ RATE 1–10\n"
                f"> 💬 COMMENT!\n\n"
                f"#{gender} #{mode.replace('_','')}"
            ),
            parse_mode="Markdown",
            has_spoiler=True
        )

    # === SELESAI ===
    keyboard = [
        [
            InlineKeyboardButton("💌 MenfessBrutt", callback_data="topik_menfess"),
            InlineKeyboardButton("📸 PapBrutt", callback_data="topik_pap"),
            InlineKeyboardButton("🎙 MoanBrutt", callback_data="topik_moan")
        ]
    ]
    await update.message.reply_text(
        "✅ *Postingan kamu berhasil dikirim!*\n\n"
        "Mau kirim apa lagi?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== SETUP BOT ==========
def run_bot():
    global application
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(gender_selected, pattern="^gender_"))
    application.add_handler(CallbackQueryHandler(joined_all, pattern="^joined_all$"))
    application.add_handler(CallbackQueryHandler(pilih_topik, pattern="^topik_"))
    application.add_handler(CallbackQueryHandler(pap_type_selected, pattern="^pap_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE, handle_media))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
