# filename: nabrutt_bot_final.py
# Install: pip install python-telegram-bot==20.3

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

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

# HEADER IMAGE (THREAD)
IMG_PAP_COWO      = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_PAP_CEWE      = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VIDEO_COWO    = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_VIDEO_CEWE    = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MENFESS_COWO  = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"
IMG_MENFESS_CEWE  = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"
IMG_MOAN_COWO     = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MOAN_CEWE     = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"

# SIMPAN DATA USER
user_data = {}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- HELPERS ----------
def format_gender(gender: str) -> str:
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def format_channel_caption(topik, emoji_topik, gender_raw, caption_text):
    gender_emoji = "🤵‍♂️" if gender_raw.lower() == "cowo" else "👩‍🦰"
    gender = gender_raw.upper()
    hashtag = f"#{gender} #{topik.upper()}"
    return (
        f"**{topik.upper()} {emoji_topik}**\n\n"
        f"> **GENDER 🕵️ : {gender} {gender_emoji}**\n\n"
        f"{caption_text.strip()}\n\n"
        f"> **BERIKAN REACT DAN NILAI!**\n"
        f"> **⭐ RATE 1–10**\n"
        f"> **💬 COMMENT!**\n\n"
        f"{hashtag}"
    )

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu ya:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- PILIH GENDER ----------
async def pilih_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data.replace("gender_", "")
    user_data[query.from_user.id] = {"gender": gender}

    keyboard = [
        [InlineKeyboardButton("💌 Menfess 18+", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap Cabul", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan 18+", callback_data="jenis_moan")]
    ]
    await query.edit_message_text(
        "✅ Semua step sudah selesai!\n\nPilih jenis postingan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- PILIH JENIS ----------
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
            [InlineKeyboardButton("📸 Foto", callback_data="pap_foto")],
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

# ---------- HANDLE MESSAGE ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data or "jenis" not in user_data[uid]:
        return

    jenis = user_data[uid]["jenis"]
    gender_raw = user_data[uid].get("gender", "")
    caption = update.message.caption or update.message.text or ""

    # Header images untuk thread
    header_img = {
        "menfess": IMG_MENFESS_COWO if gender_raw.lower() == "cowo" else IMG_MENFESS_CEWE,
        "pap_foto": IMG_PAP_COWO if gender_raw.lower() == "cowo" else IMG_PAP_CEWE,
        "pap_video": IMG_VIDEO_COWO if gender_raw.lower() == "cowo" else IMG_VIDEO_CEWE,
        "moan": IMG_MOAN_COWO if gender_raw.lower() == "cowo" else IMG_MOAN_CEWE
    }[jenis if jenis != "pap" else f"pap_{user_data[uid].get('pap_type', 'foto')}"]

    topik_dict = {
        "menfess": "MENFESSBRUTT",
        "pap": "PAPBRUTT",
        "moan": "MOANBRUTT"
    }
    topik = topik_dict[jenis if jenis != "pap" else "pap"]
    emoji_dict = {
        "menfess": "💌",
        "pap": "📸",
        "moan": "🎙"
    }
    emoji_topik = emoji_dict[jenis if jenis != "pap" else user_data[uid].get("pap_type","foto")]

    # ---------- SEND THREAD (GC NABRUTT) ----------
    await context.bot.send_photo(
        chat_id=GROUP_NABRUTT,
        message_thread_id={
            "menfess": THREAD_MENFESS,
            "pap": THREAD_PAP,
            "moan": THREAD_MOAN
        }[jenis if jenis != "pap" else "pap"],
        photo=header_img,
        caption=f"{topik} {emoji_topik}\n\nGender 🕵️ : {format_gender(gender_raw)}\n\n{caption}\n\n👉 Klik tombol untuk lihat full di channel",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_NABRUTT)]])
    )

    # ---------- SEND CHANNEL ----------
    channel_caption = format_channel_caption(topik, emoji_topik, gender_raw, caption)
    channel_id = {
        "menfess": CHANNEL_MENFESS_ID,
        "pap": CHANNEL_PAP_ID,
        "moan": CHANNEL_MOAN_ID
    }[jenis if jenis != "pap" else "pap"]
    if jenis == "pap" and update.message.photo:
        fid = update.message.photo[-1].file_id
        await context.bot.send_photo(channel_id, photo=fid, caption=channel_caption)
    elif jenis == "pap" and update.message.video:
        fid = update.message.video.file_id
        await context.bot.send_video(channel_id, video=fid, caption=channel_caption)
    elif jenis == "menfess":
        await context.bot.send_photo(channel_id, photo=header_img, caption=channel_caption)
    elif jenis == "moan" and update.message.voice:
        fid = update.message.voice.file_id
        await context.bot.send_voice(channel_id, voice=fid, caption=channel_caption)

    # Reset jenis
    user_data[uid].pop("jenis", None)
    if "pap_type" in user_data[uid]:
        user_data[uid].pop("pap_type")

# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pilih_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(pilih_jenis, pattern="^jenis_"))
    app.add_handler(CallbackQueryHandler(pilih_pap_type, pattern="^pap_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("🤖 Bot jalan...")
    app.run_polling(timeout=60)

if __name__ == "__main__":
    main()
