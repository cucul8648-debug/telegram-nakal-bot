import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ================== KONFIG ==================
TOKEN = "8466148433:AAEptPwAEC8a5CI_OezPxgQLaRb7MW41YbU"   # ⚠️ JANGAN simpan token asli di file publik!

# GROUP + THREAD
GROUP_NABRUTT = -1003098333444
THREAD_MENFESS = 1036
THREAD_PAP = 393
THREAD_MOAN = 1038

# CHANNEL
CHANNEL_MENFESS_ID = -1002989043936
CHANNEL_PAP_ID = -1003189592682
CHANNEL_MOAN_ID = -1003196180758

# GROUP DISKUSI
GROUP_DISKUSI = -1003033445498

# URL Join / Redirect
URL_NABRUTT = "https://t.me/+ptW3x7hLmhZkOTZl"
URL_MENFESS = "https://t.me/MenfessNABRUTT"
URL_PAP = "https://t.me/PAPCABULNABRUTT"
URL_MOAN = "https://t.me/MOAN18NABRUTT"
URL_DISKUSI = "https://t.me/+NHZRuZGIyehhNzk1"

# SIMPAN DATA USER
user_data = {}
emoji_counter = {}
vote_tracker = {}

# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- HELPER ----------
def format_gender(gender: str) -> str:
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def emoji_keyboard(key: str):
    counts = emoji_counter.get(key, {"👍": 0, "💖": 0, "💦": 0})
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"👍 {counts['👍']}", callback_data=f"vote|{key}|like"),
            InlineKeyboardButton(f"💖 {counts['💖']}", callback_data=f"vote|{key}|love"),
            InlineKeyboardButton(f"💦 {counts['💦']}", callback_data=f"vote|{key}|splash")
        ],
        [
            InlineKeyboardButton("1", callback_data=f"vote|{key}|1"),
            InlineKeyboardButton("2", callback_data=f"vote|{key}|2"),
            InlineKeyboardButton("3", callback_data=f"vote|{key}|3"),
            InlineKeyboardButton("4", callback_data=f"vote|{key}|4"),
            InlineKeyboardButton("5", callback_data=f"vote|{key}|5")
        ],
        [
            InlineKeyboardButton("6", callback_data=f"vote|{key}|6"),
            InlineKeyboardButton("7", callback_data=f"vote|{key}|7"),
            InlineKeyboardButton("8", callback_data=f"vote|{key}|8"),
            InlineKeyboardButton("9", callback_data=f"vote|{key}|9"),
            InlineKeyboardButton("10", callback_data=f"vote|{key}|10")
        ]
    ])

async def is_member(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def check_all_membership(bot, uid):
    join_nabrutt = await is_member(bot, GROUP_NABRUTT, uid)
    join_diskusi = await is_member(bot, GROUP_DISKUSI, uid)
    join_menfess = await is_member(bot, CHANNEL_MENFESS_ID, uid)
    join_pap     = await is_member(bot, CHANNEL_PAP_ID, uid)
    join_moan    = await is_member(bot, CHANNEL_MOAN_ID, uid)
    # pastikan group utama juga ikut dicek
    return join_nabrutt and join_diskusi and join_menfess and join_pap and join_moan

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelamin mu dulu ya:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- PILIH GENDER ----------
async def pilih_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data.replace("gender_", "")
    user_data[query.from_user.id] = {"gender": gender}
    uid = query.from_user.id
    sudah_join = await check_all_membership(context.bot, uid)
    if not sudah_join:
        keyboard = [
            [InlineKeyboardButton("👉 Join Group Nabrutt", url=URL_NABRUTT)],
            [InlineKeyboardButton("👉 Join Group Diskusi", url=URL_DISKUSI)],
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
        await tampilkan_menu(update, context)

# ---------- CEK JOIN ----------
async def cek_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    sudah_join = await check_all_membership(context.bot, uid)
    if sudah_join:
        await tampilkan_menu(update, context)
    else:
        await query.edit_message_text("❌ Kamu belum join semua group/channel.\n\nSilakan join dulu baru lanjut.")

# ---------- MENU ----------
async def tampilkan_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("💌 Menfess 18+", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap Cabul", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan 18+", callback_data="jenis_moan")]
    ]
    await query.edit_message_text(
        "✅ Semua step sudah selesai!\n\nPilih jenis postingan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- PILIH JENIS (BARU) ----------
async def pilih_jenis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    jenis = query.data.replace("jenis_", "")
    user_data.setdefault(uid, {})["jenis"] = jenis

    if jenis == "pap":
        keyboard = [
            [InlineKeyboardButton("📷 Foto", callback_data="pap_foto")],
            [InlineKeyboardButton("🎥 Video", callback_data="pap_video")]
        ]
        await query.edit_message_text("Kirim PAP dalam bentuk apa?",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(f"Silakan kirim konten untuk {jenis.upper()} sekarang.")

# ---------- PILIH PAP TYPE (BARU) ----------
async def pilih_pap_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    tipe = "foto" if query.data == "pap_foto" else "video"
    user_data.setdefault(uid, {})["pap_type"] = tipe
    await query.edit_message_text("Silakan kirim foto/video sekarang.")

# ---------- HANDLE VOTE ----------
async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    _, key, action = query.data.split("|")

    if key not in vote_tracker:
        vote_tracker[key] = {"emoji": {}, "nilai": {}}

    if action in ["like", "love", "splash"]:
        if uid in vote_tracker[key]["emoji"]:
            await query.answer("⚠️ Kamu sudah pilih emoji!", show_alert=True)
            return
        vote_tracker[key]["emoji"][uid] = action
        if key not in emoji_counter:
            emoji_counter[key] = {"👍":0, "💖":0, "💦":0}
        if action == "like": emoji_counter[key]["👍"] += 1
        elif action == "love": emoji_counter[key]["💖"] += 1
        elif action == "splash": emoji_counter[key]["💦"] += 1

    elif action.isdigit():
        if uid in vote_tracker[key]["nilai"]:
            await query.answer("⚠️ Kamu sudah kasih nilai!", show_alert=True)
            return
        vote_tracker[key]["nilai"][uid] = int(action)

    counts = emoji_counter.get(key, {"👍":0, "💖":0, "💦":0})
    await query.message.edit_reply_markup(reply_markup=emoji_keyboard(key))
    await query.answer("✅ Pilihan kamu tersimpan!")

    # ---------- HANDLE MESSAGE ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data or "jenis" not in user_data[uid]:
        return
    jenis = user_data[uid]["jenis"]
    gender_text = format_gender(user_data[uid].get("gender",""))

    caption = update.message.caption or ""
    text = update.message.text or ""

    # ----- MENFESS -----
    if jenis == "menfess":
        # thread GC hanya text + link
        await context.bot.send_message(
            chat_id=GROUP_NABRUTT,
            message_thread_id=THREAD_MENFESS,
            text=f"MENFESS 💌18+\n\n🕵️ Gender: {gender_text}\n\n{text}\n\n👉 Klik tombol untuk lihat full di channel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_MENFESS)]])
        )
        # channel full text + emoji interaktif
        if text:
            await context.bot.send_message(
                chat_id=CHANNEL_MENFESS_ID,
                text=f"MENFESS 💌18+\n\n🕵️ Gender: {gender_text}\n\n{text}",
                reply_markup=emoji_keyboard()
            )

    # ----- PAP -----
    elif jenis == "pap":
        if "pap_type" not in user_data[uid]:
            await update.message.reply_text("⚠️ Pilih tipe PAP dulu (Foto/Video).")
            return
        tipe = user_data[uid]["pap_type"]
        file_id = None
        title = "PAPBRUTT 📸" if tipe == "foto" else "VIDEOBRUTT 🎥"

        if tipe == "foto" and update.message.photo:
            file_id = update.message.photo[-1].file_id
            # thread GC
            await context.bot.send_photo(
                chat_id=GROUP_NABRUTT,
                message_thread_id=THREAD_PAP,
                photo=file_id,
                caption=f"{title}\n\n🕵️ Gender: {gender_text}\n\n{caption}\n\n👉 Klik tombol untuk lihat full di channel",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_PAP)]])
            )
            # channel full
            await context.bot.send_photo(
                chat_id=CHANNEL_PAP_ID,
                photo=file_id,
                caption=f"{title}\n👤 Gender: {gender_text}\n\n{caption}",
                has_spoiler=True,
                reply_markup=emoji_keyboard()
            )
        elif tipe == "video" and update.message.video:
            file_id = update.message.video.file_id
            await context.bot.send_video(
                chat_id=GROUP_NABRUTT,
                message_thread_id=THREAD_PAP,
                video=file_id,
                caption=f"{title}\n\n🕵️ Gender: {gender_text}\n\n{caption}\n\n👉 Klik tombol untuk lihat full di channel",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_PAP)]])
            )
            await context.bot.send_video(
                chat_id=CHANNEL_PAP_ID,
                video=file_id,
                caption=f"{title}\n👤 Gender: {gender_text}\n\n{caption}",
                has_spoiler=True,
                reply_markup=emoji_keyboard()
            )
        else:
            await update.message.reply_text(f"⚠️ Kirim {tipe} sesuai pilihanmu!")
            return
        user_data[uid].pop("pap_type", None)

    # ----- MOAN -----
    elif jenis == "moan":
        if update.message.voice:
            file_id = update.message.voice.file_id
            # thread GC hanya text + link
            await context.bot.send_message(
                chat_id=GROUP_NABRUTT,
                message_thread_id=THREAD_MOAN,
                text=f"MOANBRUTT 🎧\n\n🕵️ Gender: {gender_text}\n\n{caption}\n\n👉 Klik tombol untuk lihat full di channel",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_MOAN)]])
            )
            # channel full audio + emoji interaktif
            await context.bot.send_voice(
                chat_id=CHANNEL_MOAN_ID,
                voice=file_id,
                caption=f"MOANBRUTT 🎧\n👤 Gender: {gender_text}\n\n{caption}",
                has_spoiler=True,
                reply_markup=emoji_keyboard()
            )
        else:
            await update.message.reply_text("⚠️ Kirim voice note ya!")

    # Reset & tampil menu lagi
    keyboard = [
        [InlineKeyboardButton("💌 Menfess 18+", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap Cabul", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan 18+", callback_data="jenis_moan")]
    ]
    await update.message.reply_text(
        "✅ Postingan berhasil dikirim!\n\nMau kirim apa lagi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    user_data[uid].pop("jenis", None)
# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pilih_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(cek_join, pattern="^cek_join$"))
    app.add_handler(CallbackQueryHandler(tampilkan_menu, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(pilih_jenis, pattern="^jenis_"))
    app.add_handler(CallbackQueryHandler(pilih_pap_type, pattern="^pap_"))
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="^vote"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("🤖 Bot jalan...")
    app.run_polling(timeout=60)

if __name__ == "__main__":
    main()
