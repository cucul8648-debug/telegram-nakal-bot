import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

# SIMPAN DATA USER
user_data = {}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- HELPER ----------
def format_gender(gender: str):
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def format_hashtag(gender: str, topik: str):
    return f"#{gender.upper()} #{topik.upper()}"

def get_header_image(topik, gender):
    if topik == "menfess":
        return IMG_MENFESS_COWO if gender=="cowo" else IMG_MENFESS_CEWE
    elif topik == "pap":
        return IMG_PAP_COWO if gender=="cowo" else IMG_PAP_CEWE
    elif topik == "video":
        return IMG_VIDEO_COWO if gender=="cowo" else IMG_VIDEO_CEWE
    elif topik == "moan":
        return IMG_MOAN_COWO if gender=="cowo" else IMG_MOAN_CEWE

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
    uid = query.from_user.id

    if not await check_all_membership(context.bot, uid):
        keyboard = [
            [InlineKeyboardButton("👉 Join Group Nabrutt", url=URL_NABRUTT)],
            [InlineKeyboardButton("👉 Join GC Menfess", url=URL_GC_MENFESS)],
            [InlineKeyboardButton("👉 Join GC PAP", url=URL_GC_PAP)],
            [InlineKeyboardButton("👉 Join GC Moan", url=URL_GC_MOAN)],
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

# ---------- HANDLE MESSAGE ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data or "jenis" not in user_data[uid]:
        return

    jenis = user_data[uid]["jenis"]
    gender_raw = user_data[uid].get("gender", "")
    gender = format_gender(gender_raw)
    caption = update.message.caption or ""
    text = update.message.text or ""
    header_img = get_header_image(jenis if jenis!="pap" else user_data[uid].get("pap_type","foto"), gender_raw)

    hashtag = format_hashtag(gender_raw, jenis.upper() if jenis!="pap" else f"{user_data[uid].get('pap_type','foto').upper()}BRUTT")
    topik_display = f"{jenis.upper()}BRUTT" if jenis!="pap" else f"{user_data[uid].get('pap_type','foto').upper()}BRUTT"

    # ---------- THREAD GC ----------
    await context.bot.send_photo(
        chat_id=GROUP_NABRUTT,
        message_thread_id={ "menfess": THREAD_MENFESS, "pap": THREAD_PAP, "moan": THREAD_MOAN }[jenis],
        photo=header_img,
        caption=f"{topik_display}\n\nGender 🕵️ : {gender}\n\n{caption or text}\n\n👉 Klik tombol untuk lihat full di channel",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url={
            "menfess": URL_GC_MENFESS,
            "pap": URL_GC_PAP,
            "moan": URL_GC_MOAN
        }[jenis]]]])
    )

    # ---------- CHANNEL ----------
    if jenis == "menfess":
        await context.bot.send_message(
            chat_id=CHANNEL_MENFESS_ID,
            text=f"**{topik_display} 💌**\n\n> **GENDER 🕵️ : {gender_raw.upper()} {gender}**\n\n{caption or text}\n\n> **BERIKAN REACT DAN NILAI!**\n> **⭐ RATE 1–10**\n> **💬 COMMENT!**\n\n{hashtag}",
            parse_mode="Markdown"
        )
    elif jenis == "moan":
        if update.message.voice:
            fid = update.message.voice.file_id
            await context.bot.send_voice(
                chat_id=CHANNEL_MOAN_ID,
                voice=fid,
                caption=f"**{topik_display} 🎧**\n\n> **GENDER 🕵️ : {gender_raw.upper()} {gender}**\n\n{caption or text}\n\n> **BERIKAN REACT DAN NILAI!**\n> **⭐ RATE 1–10**\n> **💬 COMMENT!**\n\n{hashtag}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("⚠️ Kirim voice note ya!")
            return
    elif jenis == "pap":
        tipe = user_data[uid].get("pap_type", "foto")
        if tipe == "foto" and update.message.photo:
            fid = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=CHANNEL_PAP_ID,
                photo=fid,
                caption=f"**{topik_display} 📸**\n\n> **GENDER 🕵️ : {gender_raw.upper()} {gender}**\n\n{caption or text}\n\n> **BERIKAN REACT DAN NILAI!**\n> **⭐ RATE 1–10**\n> **💬 COMMENT!**\n\n{hashtag}",
                parse_mode="Markdown"
            )
        elif tipe == "video" and update.message.video:
            fid = update.message.video.file_id
            await context.bot.send_video(
                chat_id=CHANNEL_PAP_ID,
                video=fid,
                caption=f"**{topik_display} 🎥**\n\n> **GENDER 🕵️ : {gender_raw.upper()} {gender}**\n\n{caption or text}\n\n> **BERIKAN REACT DAN NILAI!**\n> **⭐ RATE 1–10**\n> **💬 COMMENT!**\n\n{hashtag}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"⚠️ Kirim {tipe} sesuai pilihanmu!")
            return
        user_data[uid].pop("pap_type", None)

    user_data[uid].pop("jenis", None)
    menu_awal = InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 Menfess 18+", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap Cabul",   callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan 18+",    callback_data="jenis_moan")]
    ])
    await update.message.reply_text(
        "✅ Postingan berhasil dikirim!\n\nMau kirim apa lagi?",
        reply_markup=menu_awal
    )

# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pilih_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(cek_join,    pattern="^cek_join$"))
    app.add_handler(CallbackQueryHandler(pilih_jenis, pattern="^jenis_"))
    app.add_handler(CallbackQueryHandler(pilih_pap_type, pattern="^pap_"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("🤖 Bot jalan...")
    app.run_polling(timeout=60)

if __name__ == "__main__":
    main()
