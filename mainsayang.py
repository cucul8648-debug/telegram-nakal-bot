# main_final.py
import logging, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
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
        "Selamat datang di Nabrutt 🤖\n\nPilih jenis kelaminmu dulu ya:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== CEK JOIN GROUP ==================
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
        except:
            not_joined.append(url)
    return not_joined

# ================== PILIH GENDER ==================
async def gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data.split("_")[1].upper()
    context.user_data["gender"] = gender

    # Cek join
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

# ================== MENU POSTINGAN ==================
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

# ================== POST CALLBACK ==================
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

# ================== PAP FOTO/VIDEO ==================
async def pap_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pap_type = query.data
    context.user_data["pap_type"] = pap_type
    await query.edit_message_text(f"Kamu memilih {pap_type.replace('pap_', '').upper()} untuk PAP. Kirim file sekarang.")

# ================== TERIMA TEKS/FILE ==================
async def receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    gender = context.user_data.get("gender", "COWO")
    topik = context.user_data.get("topik")
    pap_type = context.user_data.get("pap_type", "")
    text = update.message.text if update.message.text else ""
    media = None

    # Jika voice/photo/video
    if update.message.voice:
        media = update.message.voice
    elif update.message.photo:
        media = update.message.photo[-1]
    elif update.message.video:
        media = update.message.video

    # Thread header image
    header_img = ""
    if topik == "post_menfess":
        header_img = IMG_MENFESS_COWO if gender == "COWO" else IMG_MENFESS_CEWE
    elif topik == "post_pap":
        if pap_type == "pap_foto":
            header_img = IMG_PAP_COWO if gender == "COWO" else IMG_PAP_CEWE
        elif pap_type == "pap_video":
            header_img = IMG_VIDEO_COWO if gender == "COWO" else IMG_VIDEO_CEWE
    elif topik == "post_moan":
        header_img = IMG_MOAN_COWO if gender == "COWO" else IMG_MOAN_CEWE

    # ================== KIRIM KE THREAD ==================
    thread_text = ""
    if topik == "post_menfess":
        thread_text = f"""MENFESSBRUTT 💌

> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**

{header_img}

{text}

👉 Klik tombol untuk lihat full di channel
"""
    elif topik == "post_pap":
        thread_text = f"""{'PAPBRUTT 📸' if pap_type=='pap_foto' else 'VIDEOBRUTT 🎥'}

> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**

{header_img}

{text}

👉 Klik tombol untuk lihat full di channel
"""
    elif topik == "post_moan":
        thread_text = f"""MOANBRUTT 🎧

> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**

{header_img}

{text}

👉 Klik tombol untuk lihat full di channel
"""

    await update.message.reply_text(thread_text)

    # ================== KIRIM KE CHANNEL ==================
    channel_caption = f"""**{thread_text.splitlines()[0]}**

> **GENDER 🕵️ : {gender} {'🤵‍♂️' if gender=='COWO' else '👩‍🦰'}**

{text}

> **BERIKAN REACT DAN NILAI!**
> **⭐ RATE 1–10**
> **💬 COMMENT!**
"""
    # hashtag
    if topik == "post_menfess":
        channel_caption += f"\n#{gender} #MENFESSBRUTT"
    elif topik == "post_pap":
        channel_caption += f"\n#{gender} #{'PAPBRUTT' if pap_type=='pap_foto' else 'VIDEOBRUTT'}"
    elif topik == "post_moan":
        channel_caption += f"\n#{gender} #MOANBRUTT"

    channel_id = 0
    if topik == "post_menfess":
        channel_id = CHANNEL_MENFESS_ID
    elif topik == "post_pap":
        channel_id = CHANNEL_PAP_ID
    elif topik == "post_moan":
        channel_id = CHANNEL_MOAN_ID

    if media:
        await context.bot.send_message(channel_id, text=channel_caption)  # Bisa ganti send_photo/send_video/send_voice sesuai media
    else:
        await context.bot.send_message(channel_id, text=channel_caption)

    # ================== MENU ULANG ==================
    keyboard = [
        [InlineKeyboardButton("💌 MenfessBRUTT", callback_data="post_menfess")],
        [InlineKeyboardButton("📸 PapBRUTT", callback_data="post_pap")],
        [InlineKeyboardButton("🎙 MoanBRUTT", callback_data="post_moan")]
    ]
    await update.message.reply_text(
        "✅ Postingan kamu berhasil dikirim!\n\nMau kirim apa lagi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== MAIN ==================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(gender_callback, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(post_callback, pattern="^post_"))
    app.add_handler(CallbackQueryHandler(pap_type_callback, pattern="^pap_"))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO | filters.VIDEO, receive_content))

    print("Bot running...")

    # Jalankan webhook untuk Render
    WEBHOOK_PATH = f"/{TOKEN}"
    WEBHOOK_URL = f"https://github.com/cucul8648-debug/telegram-nakal-bot{WEBHOOK_PATH}"
    PORT = int(os.environ.get("PORT", 10000))
    app.run_webhook(listen="0.0.0.0", port=PORT, url_path=WEBHOOK_PATH, webhook_url=WEBHOOK_URL)

if __name__ == "__main__":
    main()
