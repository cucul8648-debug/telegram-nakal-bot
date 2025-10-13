# main_final.py
import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ================== KONFIG ==================
TOKEN = "8466148433:AAH9NFT_wrkBlZ-uO8hllAdxdTwFpLqip74"

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

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu ya:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== CEK JOIN ==================
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE, gender):
    user = update.callback_query.from_user
    # Untuk simplifikasi, kita anggap user join semua
    joined_all = True  # nanti bisa diganti cek real join
    if not joined_all:
        keyboard = [
            [InlineKeyboardButton("👉 Join Group Nabrutt", url=URL_NABRUTT)],
            [InlineKeyboardButton("👉 Join Channel Menfess", url=URL_GC_MENFESS)],
            [InlineKeyboardButton("👉 Join Channel PAP", url=URL_GC_PAP)],
            [InlineKeyboardButton("👉 Join Channel Moan", url=URL_GC_MOAN)],
            [InlineKeyboardButton("✅ Sudah Join Semua", callback_data=f"joined_{gender}")]
        ]
        await update.callback_query.edit_message_text(
            f"Gender kamu: {gender.upper()} ✅\n\n⚠️ Sebelum lanjut, wajib join semua group & channel di bawah ini:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await post_type_menu(update, context, gender)

# ================== PILIH JENIS POSTING ==================
async def post_type_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, gender):
    keyboard = [
        [
            InlineKeyboardButton("💌 Menfess 18+", callback_data=f"post_menfess_{gender}"),
            InlineKeyboardButton("📸 Pap Cabul", callback_data=f"post_pap_{gender}"),
            InlineKeyboardButton("🎙 Moan 18+", callback_data=f"post_moan_{gender}")
        ]
    ]
    await update.callback_query.edit_message_text(
        "✅ Semua step sudah selesai!\n\nPilih jenis postingan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== FORMAT CHANNEL ==================
def format_channel_caption(topik, emoji_topik, gender_raw, caption_text):
    gender_emoji = "🤵‍♂️" if gender_raw.lower() == "cowo" else "👩‍🦰"
    gender = gender_raw.upper()
    return (
        f"**{topik.upper()} {emoji_topik}**\n\n"
        f"> **GENDER 🕵️ : {gender} {gender_emoji}**\n\n"
        f"{caption_text.strip()}\n\n"
        f"> **BERIKAN REACT DAN NILAI!**\n"
        f"> **⭐ RATE 1–10**\n"
        f"> **💬 COMMENT!**\n\n"
        f"#{gender} #{topik.upper()}"
    )

# ================== CALLBACK HANDLER ==================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Pilih gender
    if data.startswith("gender_"):
        gender = data.split("_")[1]
        await check_join(update, context, gender)
    # Sudah join
    elif data.startswith("joined_"):
        gender = data.split("_")[1]
        await post_type_menu(update, context, gender)
    # Pilih posting
    elif data.startswith("post_"):
        jenis, gender = data.split("_")[1:]
        if jenis == "pap":
            keyboard = [
                [InlineKeyboardButton("📸 Foto", callback_data=f"pap_foto_{gender}")],
                [InlineKeyboardButton("🎥 Video", callback_data=f"pap_video_{gender}")]
            ]
            await query.edit_message_text(
                "📸 Kamu memilih PAP. Pilih tipe:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(f"🎙 Kamu memilih {jenis.upper()}. Kirim file / teks sekarang.")
    # PAP pilih foto/video
    elif data.startswith("pap_"):
        jenis_file, gender = data.split("_")[1:]
        await query.edit_message_text(f"Kamu memilih {jenis_file.upper()} untuk PAP. Kirim file sekarang.")

# ================== MAIN ==================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("Bot running...")

    # Webhook Render
    WEBHOOK_PATH = f"/{TOKEN}"
    WEBHOOK_URL = f"https://YOUR-RENDER-URL.onrender.com{WEBHOOK_PATH}"
    PORT = int(os.environ.get("PORT", 10000))
    app.run_webhook(listen="0.0.0.0", port=PORT, url_path=WEBHOOK_PATH, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    main()
