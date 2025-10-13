# filename: main.py
# requirements.txt:
# python-telegram-bot==20.3
# Flask==2.3.3 (kalau mau tambah webhook nanti)

import os
import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
)

# ---------------- CONFIG ----------------
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8466148433:AAH9NFT_wrkBlZ-uO8hllAdxdTwFpLqip74")

# Group Threads
GROUP_NABRUTT = int(os.environ.get("GROUP_NABRUTT", -1003098333444))
THREAD_MENFESS = int(os.environ.get("THREAD_MENFESS", 1036))
THREAD_PAP = int(os.environ.get("THREAD_PAP", 393))
THREAD_MOAN = int(os.environ.get("THREAD_MOAN", 2298))

# Channels
CHANNEL_MENFESS = int(os.environ.get("CHANNEL_MENFESS", -1002989043936))
CHANNEL_PAP = int(os.environ.get("CHANNEL_PAP", -1003189592682))
CHANNEL_MOAN = int(os.environ.get("CHANNEL_MOAN", -1003196180758))

# Image Headers (GitHub RAW)
IMG_MENFESS_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_PAP_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MOAN_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MOAN_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"

# Group/Channel Join Links
JOIN_LINKS = [
    ("Group Nabrutt", "https://t.me/NABRUTT11"),
    ("Channel Menfess", "https://t.me/MenfessNABRUTT"),
    ("Channel PAP", "https://t.me/PAPCABULNABRUTT"),
    ("Channel Moan", "https://t.me/MOAN18NABRUTT")
]

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------- HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo"),
            InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")
        ]
    ]
    await update.message.reply_text(
        "**Selamat datang di EksibNih 🤖**\n\n"
        "> Pilih jenis kelaminmu dulu ya:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    gender = "COWO" if query.data == "gender_cowo" else "CEWE"
    context.user_data["gender"] = gender

    text = (
        f"**Gender kamu: {gender} ✅**\n\n"
        f"⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:\n"
    )

    join_buttons = [[InlineKeyboardButton(f"👉 {name}", url=url)] for name, url in JOIN_LINKS]
    join_buttons.append([InlineKeyboardButton("✅ Sudah Join Semua", callback_data="done_join")])

    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(join_buttons))


async def handle_done_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    menu_keyboard = [
        [
            InlineKeyboardButton("💌 MenfessBRUTT", callback_data="menfess"),
            InlineKeyboardButton("📸 PapBRUTT", callback_data="pap"),
            InlineKeyboardButton("🎧 MoanBRUTT", callback_data="moan")
        ]
    ]

    await query.edit_message_text(
        "**✅ Semua step sudah selesai!**\n\n> Pilih jenis postingan:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(menu_keyboard)
    )


# ---------------- POSTING TYPE ----------------

async def choose_post_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    gender = context.user_data.get("gender", "COWO")

    if data == "menfess":
        context.user_data["type"] = "menfess"
        await query.message.reply_text(
            "💌 Kamu memilih **MENFESSBRUTT**.\n\n> Masukkan caption atau teks menfess kamu:",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "pap":
        keyboard = [
            [
                InlineKeyboardButton("📷 Foto", callback_data="pap_foto"),
                InlineKeyboardButton("🎥 Video", callback_data="pap_video")
            ]
        ]
        await query.message.reply_text(
            "📸 Kamu memilih **PAPBRUTT**.\n\n> Pilih tipe PAP yang mau kamu kirim:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "moan":
        context.user_data["type"] = "moan"
        context.user_data["await_caption"] = True
        await query.message.reply_text(
            "🎙 Kamu memilih **MOANBRUTT**.\n\n> **Masukkan caption :**",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if context.user_data.get("await_caption"):
        context.user_data["caption"] = text
        context.user_data["await_caption"] = False
        context.user_data["await_media"] = True
        await update.message.reply_text(
            "✅ **Caption berhasil dimasukkan!**\n\n> Sekarang kirim moan yang kamu inginkan 🎧",
            parse_mode=ParseMode.MARKDOWN
        )
        return


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    gender = user_data.get("gender", "COWO")
    post_type = user_data.get("type")

    if not post_type:
        return

    # pilih thread & channel
    thread_id = THREAD_MENFESS if post_type == "menfess" else (
        THREAD_MOAN if post_type == "moan" else THREAD_PAP
    )
    channel_id = (
        CHANNEL_MENFESS if post_type == "menfess"
        else CHANNEL_MOAN if post_type == "moan"
        else CHANNEL_PAP
    )

    # pilih header image
    img_url = (
        IMG_MENFESS_COWO if gender == "COWO" else IMG_MENFESS_CEWE
    ) if post_type == "menfess" else (
        IMG_MOAN_COWO if post_type == "moan" and gender == "COWO" else
        IMG_MOAN_CEWE if post_type == "moan" else None
    )

    # thread message
    caption = user_data.get("caption") or (update.message.caption or update.message.text or "Tanpa caption")

    preview_text = (
        f"**{post_type.upper()}BRUTT {'💌' if post_type=='menfess' else '📸' if post_type=='pap' else '🎧'}**\n\n"
        f"> **Gender 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**\n\n"
        f"{caption}\n\n"
        f"> 👉 Klik tombol di bawah untuk lihat full di channel"
    )

    inline_view = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Lihat Full di Channel", url="https://t.me/MenfessNABRUTT")]
    ])

    # kirim header di thread
    if img_url:
        await update.get_bot().send_photo(
            GROUP_NABRUTT,
            photo=img_url,
            caption=preview_text,
            parse_mode=ParseMode.MARKDOWN,
            message_thread_id=thread_id,
            reply_markup=inline_view
        )

    # kirim media asli ke channel
    caption_channel = (
        f"**{post_type.upper()}BRUTT {'💌' if post_type=='menfess' else '📸' if post_type=='pap' else '🎧'}**\n\n"
        f"> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**\n\n"
        f"{caption}\n\n"
        "> **BERIKAN REACT DAN NILAI!**\n"
        "> **⭐ RATE 1–10**\n"
        "> **💬 COMMENT!**\n\n"
        f"#{gender} #{post_type.upper()}BRUTT"
    )

    if update.message.photo:
        file = update.message.photo[-1].file_id
        await update.get_bot().send_photo(channel_id, photo=file, caption=caption_channel,
                                          parse_mode=ParseMode.MARKDOWN, has_spoiler=True)
    elif update.message.video:
        file = update.message.video.file_id
        await update.get_bot().send_video(channel_id, video=file, caption=caption_channel,
                                          parse_mode=ParseMode.MARKDOWN, has_spoiler=True)
    elif update.message.voice:
        file = update.message.voice.file_id
        await update.get_bot().send_voice(channel_id, voice=file, caption=caption_channel,
                                          parse_mode=ParseMode.MARKDOWN, has_spoiler=True)

    # selesai posting
    await update.message.reply_text(
        "✅ **Postingan kamu berhasil dikirim!**\n\n> Mau kirim apa lagi?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💌 MenfessBRUTT", callback_data="menfess"),
                InlineKeyboardButton("📸 PapBRUTT", callback_data="pap"),
                InlineKeyboardButton("🎧 MoanBRUTT", callback_data="moan")
            ]
        ])
    )


# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(handle_done_join, pattern="^done_join$"))
    app.add_handler(CallbackQueryHandler(choose_post_type, pattern="^(menfess|pap|moan)$"))
    app.add_handler(CallbackQueryHandler(choose_post_type, pattern="^(pap_foto|pap_video)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption))
    app.add_handler(MessageHandler(filters.ALL, handle_media))

    print("🤖 Bot aktif dan berjalan polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
