import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ================== KONFIG ==================
TOKEN = "8466148433:AAF9iG2B3Fcs2b_nq9r6Po-_AUz7MRojqjw"

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
    return join_diskusi and join_menfess and join_pap and join_moan

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
        await tampilkan_menu(query)

# ---------- CEK JOIN ----------
async def cek_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    sudah_join = await check_all_membership(context.bot, uid)
    if sudah_join:
        await tampilkan_menu(query)
    else:
        await query.edit_message_text("❌ Kamu belum join semua group/channel.\n\nSilakan join dulu baru lanjut.")

# ---------- MENU ----------
async def tampilkan_menu(query):
    keyboard = [
        [InlineKeyboardButton("💌 Menfess 18+", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap Cabul", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan 18+", callback_data="jenis_moan")]
    ]
    await query.edit_message_text(
        "✅ Semua step sudah selesai!\n\nPilih jenis postingan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- HANDLE VOTE ----------
async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    _, key, action = query.data.split("|")

    if key not in vote_tracker:
        vote_tracker[key] = {"emoji": {}, "nilai": {}}

    # Emoji
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

    # Nilai
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

    caption = update.message.caption or update.message.text or ""

    # --- MENFESS ---
    if jenis == "menfess":
        # Thread
        await context.bot.send_message(
            chat_id=GROUP_NABRUTT,
            message_thread_id=THREAD_MENFESS,
            text=f"MENFESS 💌 18+\n\n🕵️ Gender: {gender_text}\n\n{caption}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_MENFESS)]])
        )
        # Channel
        msg = await context.bot.send_message(
            chat_id=CHANNEL_MENFESS_ID,
            text=f"MENFESS 💌 18+\n\n👤 Gender: {gender_text}\n\n{caption}\n\n💬 Komentar: {URL_DISKUSI}"
        )
        key = f"{msg.chat_id}-{msg.message_id}"
        emoji_counter[key] = {"👍":0,"💖":0,"💦":0}
        await msg.edit_reply_markup(reply_markup=emoji_keyboard(key))
        # Diskusi
        await context.bot.send_message(
            chat_id=GROUP_DISKUSI,
            text=f"MENFESS 💌 18+\n\n👤 Gender: {gender_text}\n\n{caption}",
            reply_markup=emoji_keyboard(key)
        )

    # --- PAP ---
    elif jenis == "pap":
        tipe = user_data[uid].get("pap_type","foto")
        file_id = None
        title = "PAPBRUTT 📸" if tipe=="foto" else "VIDEOBRUTT 🎥"

        if tipe=="foto" and update.message.photo:
            file_id = update.message.photo[-1].file_id
            # Thread
            await context.bot.send_message(
                chat_id=GROUP_NABRUTT,
                message_thread_id=THREAD_PAP,
                text=f"{title}\n\n🕵️ Gender: {gender_text}\n\n{caption}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_PAP)]])
            )
            # Channel
            msg = await context.bot.send_photo(
                chat_id=CHANNEL_PAP_ID,
                photo=file_id,
                caption=f"{title}\n👤 Gender: {gender_text}\n\n{caption}\n\n💬 Komentar: {URL_DISKUSI}",
                has_spoiler=True
            )
            key = f"{msg.chat_id}-{msg.message_id}"
            emoji_counter[key] = {"👍":0,"💖":0,"💦":0}
            await msg.edit_reply_markup(reply_markup=emoji_keyboard(key))
            # Diskusi
            await context.bot.send_photo(
                chat_id=GROUP_DISKUSI,
                photo=file_id,
                caption=f"{title}\n👤 Gender: {gender_text}\n\n{caption}",
                has_spoiler=True,
                reply_markup=emoji_keyboard(key)
            )

        elif tipe=="video" and update.message.video:
            file_id = update.message.video.file_id
            # Thread
            await context.bot.send_message(
                chat_id=GROUP_NABRUTT,
                message_thread_id=THREAD_PAP,
                text=f"{title}\n\n🕵️ Gender: {gender_text}\n\n{caption}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_PAP)]])
            )
            # Channel
            msg = await context.bot.send_video(
                chat_id=CHANNEL_PAP_ID,
                video=file_id,
                caption=f"{title}\n👤 Gender: {gender_text}\n\n{caption}\n\n💬 Komentar: {URL_DISKUSI}",
                has_spoiler=True
            )
            key = f"{msg.chat_id}-{msg.message_id}"
            emoji_counter[key] = {"👍":0,"💖":0,"💦":0}
            await msg.edit_reply_markup(reply_markup=emoji_keyboard(key))
            # Diskusi
            await context.bot.send_video(
                chat_id=GROUP_DISKUSI,
                video=file_id,
                caption=f"{title}\n👤 Gender: {gender_text}\n\n{caption}",
                has_spoiler=True,
                reply_markup=emoji_keyboard(key)
            )

    # --- MOAN ---
    elif jenis == "moan" and update.message.voice:
        file_id = update.message.voice.file_id
        # Thread
        await context.bot.send_message(
            chat_id=GROUP_NABRUTT,
            message_thread_id=THREAD_MOAN,
            text=f"MOANBRUTT 🎧\n\n🕵️ Gender: {gender_text}\n\n{caption}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=URL_MOAN)]])
        )
        # Channel
        msg = await context.bot.send_voice(
            chat_id=CHANNEL_MOAN_ID,
            voice=file_id,
            caption=f"MOANBRUTT 🎧\n👤 Gender: {gender_text}\n\n{caption}\n\n💬 Komentar: {URL_DISKUSI}",
            has_spoiler=True
        )
        key = f"{msg.chat_id}-{msg.message_id}"
        emoji_counter[key] = {"👍":0,"💖":0,"💦":0}
        await msg.edit_reply_markup(reply_markup=emoji_keyboard(key))
        # Diskusi
        await context.bot.send_voice(
            chat_id=GROUP_DISKUSI,
            voice=file_id,
            caption=f"MOANBRUTT 🎧\n👤 Gender: {gender_text}\n\n{caption}",
            has_spoiler=True,
            reply_markup=emoji_keyboard(key)
        )

    # Balas user
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
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="^vote"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("🤖 Bot jalan...")
    app.run_polling(timeout=60)

if __name__ == "__main__":
    main()
