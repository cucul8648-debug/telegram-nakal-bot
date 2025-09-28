import logging
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
THREAD_MOAN    = 1038

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

# SIMPAN DATA USER
user_data     = {}
emoji_counter = {}
user_vote     = {}

# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- HELPER ----------
def format_gender(gender: str) -> str:
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def emoji_keyboard(jenis: str):
    """Inline keyboard untuk emoji & link komentar."""
    if jenis == "menfess":
        komentar_url = URL_GC_MENFESS
    elif jenis == "pap":
        komentar_url = URL_GC_PAP
    elif jenis == "moan":
        komentar_url = URL_GC_MOAN
    else:
        komentar_url = URL_NABRUTT  # fallback

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍", callback_data="like"),
            InlineKeyboardButton("❤️", callback_data="love"),
            InlineKeyboardButton("💦", callback_data="splash")
        ],
        [
            InlineKeyboardButton("💬 Komentar", url=komentar_url),
            InlineKeyboardButton("👥 GC Nabrutt", url=URL_NABRUTT)
        ]
    ])

async def is_member(bot, chat_id, user_id):
    """Cek apakah user sudah join chat tertentu."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def check_all_membership(bot, uid):
    """Cek join semua channel & group yang diwajibkan."""
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

# ---------- CEK JOIN ----------
async def cek_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await check_all_membership(context.bot, query.from_user.id):
        await tampilkan_menu(query)
    else:
        await query.edit_message_text(
            "❌ Kamu belum join semua group/channel.\n\nSilakan join dulu baru lanjut."
        )

# ---------- MENU ----------
async def tampilkan_menu(query):
    keyboard = [
        [InlineKeyboardButton("💌 Menfess 18+", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap Cabul",   callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan 18+",    callback_data="jenis_moan")]
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
            [InlineKeyboardButton("📸 Foto",  callback_data="pap_foto")],
            [InlineKeyboardButton("🎥 Video", callback_data="pap_video")]
        ]
        await query.edit_message_text("📸 Kamu memilih *PAP*.\n\nPilih tipe:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text("🎙 Kamu memilih *MOAN*.\n\nKirim voice note + caption (opsional).", parse_mode="Markdown")

# ---------- PILIH PAP TIPE ----------
async def pilih_pap_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipe = query.data.replace("pap_", "")
    user_data[query.from_user.id]["pap_type"] = tipe
    await query.edit_message_text(f"✅ Kamu memilih PAP tipe *{tipe.upper()}*.\n\nKirim {tipe} sekarang!", parse_mode="Markdown")

# ---------- HANDLE EMOJI ----------
async def handle_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid   = query.from_user.id
    mid   = query.message.message_id
    await query.answer()

    # Cegah double vote
    if (mid, uid) in user_vote:
        await query.answer("❌ Kamu sudah memilih emoji.", show_alert=True)
        return

    choice = query.data
    user_vote[(mid, uid)] = choice

    # Inisialisasi counter
    if mid not in emoji_counter:
        emoji_counter[mid] = {"👍": 0, "❤️": 0, "💦": 0}

    if choice == "like":
        emoji_counter[mid]["👍"] += 1
    elif choice == "love":
        emoji_counter[mid]["❤️"] += 1
    elif choice == "splash":
        emoji_counter[mid]["💦"] += 1

    c = emoji_counter[mid]

    # Update tombol dengan jumlah terbaru
    await query.message.edit_reply_markup(
        InlineKeyboardMarkup([[
            InlineKeyboardButton(f"👍 {c['👍']}", callback_data="like"),
            InlineKeyboardButton(f"❤️ {c['❤️']}", callback_data="love"),
            InlineKeyboardButton(f"💦 {c['💦']}", callback_data="splash")
        ],
        [
            InlineKeyboardButton("💬 Komentar", url=URL_NABRUTT),
            InlineKeyboardButton("👥 GC Nabrutt", url=URL_NABRUTT)
        ]])
    )

# ---------- HANDLE MESSAGE ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data or "jenis" not in user_data[uid]:
        return

    jenis   = user_data[uid]["jenis"]
    gender  = format_gender(user_data[uid].get("gender", ""))
    caption = update.message.caption or ""
    text    = update.message.text or ""

    async def send_thread(text_thread, url):
        await context.bot.send_message(
            chat_id=GROUP_NABRUTT,
            message_thread_id={
                "menfess": THREAD_MENFESS,
                "pap":     THREAD_PAP,
                "moan":    THREAD_MOAN
            }[jenis],
            text=f"{text_thread}\n\n🕵️ Gender: {gender}\n\n{caption or text}\n\n👉 Klik tombol untuk lihat full di channel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=url)]])
        )

    if jenis == "menfess":
        await send_thread("MENFESS 💌18+", URL_MENFESS)
        if text:
            await context.bot.send_message(
                chat_id=CHANNEL_MENFESS_ID,
                text=f"MENFESS 💌18+\n\n🕵️ Gender: {gender}\n\n{caption or text}",
                reply_markup=emoji_keyboard("menfess")
            )

    elif jenis == "pap":
        if "pap_type" not in user_data[uid]:
            await update.message.reply_text("⚠️ Pilih tipe PAP dulu (Foto/Video).")
            return
        tipe = user_data[uid]["pap_type"]
        title = "PAPBRUTT 📸" if tipe == "foto" else "VIDEOBRUTT 🎥"
        await send_thread(title, URL_PAP)

        if tipe == "foto" and update.message.photo:
            fid = update.message.photo[-1].file_id
            await context.bot.send_photo(
                CHANNEL_PAP_ID, photo=fid,
                caption=f"{title}\n\n🕵️ Gender: {gender}\n\n{caption or text}",
                has_spoiler=True,
                reply_markup=emoji_keyboard("pap")
            )
        elif tipe == "video" and update.message.video:
            fid = update.message.video.file_id
            await context.bot.send_video(
                CHANNEL_PAP_ID, video=fid,
                caption=f"{title}\n\n🕵️ Gender: {gender}\n\n{caption or text}",
                has_spoiler=True,
                reply_markup=emoji_keyboard("pap")
            )
        else:
            await update.message.reply_text(f"⚠️ Kirim {tipe} sesuai pilihanmu!")
            return
        user_data[uid].pop("pap_type", None)

    elif jenis == "moan":
        if update.message.voice:
            await send_thread("MOANBRUTT 🎧", URL_MOAN)
            fid = update.message.voice.file_id
            await context.bot.send_voice(
                CHANNEL_MOAN_ID,
                voice=fid,
                caption=f"MOANBRUTT 🎧\n\n🕵️ Gender: {gender}\n\n{caption or text}",
                has_spoiler=True,
                reply_markup=emoji_keyboard("moan")
            )
        else:
            await update.message.reply_text("⚠️ Kirim voice note ya!")

    # Reset jenis & kirim menu awal
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
    app.add_handler(CallbackQueryHandler(handle_emoji,   pattern="^(like|love|splash)$"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("🤖 Bot jalan...")
    app.run_polling(timeout=60)

if __name__ == "__main__":
    main()
