# filename: main_final.py
# Requirements (add to requirements.txt):
# python-telegram-bot==20.3
# Flask==2.3.3
# Pillow==9.5.0
# opencv-python==4.8.0
# (optional) sqlite3 is builtin

import os
import logging
import asyncio
import threading
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatJoinRequestHandler, ContextTypes, filters
)

# Image processing
from PIL import Image
import cv2
import numpy as np

# DB
import sqlite3

# ================== KONFIG TOKEN ==================
TOKEN_POSTING = os.environ.get("TOKEN_POSTING", "8069081808:AAEhlnUrZtwrqo5GUnHfuhdBXQN4o3LbDYc")
TOKEN_WELCOME = os.environ.get("TOKEN_WELCOME", "8490098646:AAGNF2yYwb0OSWm7dw7EK0DsXY5x7hDz-30")

# ================== KONFIG CHANNEL / GRUP ==================
CHANNEL_MENFESS_ID = int(os.environ.get("CHANNEL_MENFESS_ID", "-1002989043936"))
CHANNEL_PAP_ID     = int(os.environ.get("CHANNEL_PAP_ID",     "-1003189592682"))
CHANNEL_MOAN_ID    = int(os.environ.get("CHANNEL_MOAN_ID",    "-1003196180758"))
GROUP_NABRUTT_ID   = int(os.environ.get("GROUP_NABRUTT_ID",   "-1003098333444"))
GROUP_DISKUSI_ID   = int(os.environ.get("GROUP_DISKUSI_ID",   str(GROUP_NABRUTT_ID)))
URL_NABRUTT        = os.environ.get("URL_NABRUTT", "https://t.me/+a3Bd3FDl5HY2NjFl")

IMG_COWO = os.environ.get("IMG_COWO", "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cowo.png")
IMG_CEWE = os.environ.get("IMG_CEWE", "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/cewe.png")

# ================== WELCOME CONFIG ==================
LINKS = [
    ("🔥 GC 𝙉𝘼𝘽𝙍𝙐𝙏𝙏", "https://t.me/nabrutt11"),
    ("💌 CH 𝙈𝙀𝙉𝙁𝙀𝙎𝙎", "https://t.me/MenfessNabrutt"),
    ("📸 CH 𝙋𝘼𝙋𝘽𝙍𝙐𝙏𝙏", "https://t.me/papcabulnabrutt"),
    ("🔞 CH 𝙈𝙊𝘼𝙉", "https://t.me/Moan18Nabrutt"),
]
TIMEZONE = ZoneInfo("Asia/Jakarta")

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== DATA (in-memory caches) ==================
user_data = {}       # temporary per-user state while composing
emoji_counter = {}   # message_id -> counts
post_meta = {}       # channel_message_id -> {thread_id, owner, jenis}

# ================== DATABASE ==================
DB_PATH = os.environ.get("DB_PATH", "nabrutt.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        channel_msg_id INTEGER PRIMARY KEY,
        thread_id INTEGER,
        owner_id INTEGER,
        jenis TEXT,
        caption TEXT,
        created_at TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_msg_id INTEGER,
        user_id INTEGER,
        score INTEGER,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_post_db(channel_msg_id, thread_id, owner_id, jenis, caption):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO posts(channel_msg_id, thread_id, owner_id, jenis, caption, created_at) VALUES(?,?,?,?,?,?)",
              (channel_msg_id, thread_id, owner_id, jenis, caption, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def add_score_db(channel_msg_id, user_id, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO scores(channel_msg_id, user_id, score, created_at) VALUES(?,?,?,?)",
              (channel_msg_id, user_id, score, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_score_stats(channel_msg_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), AVG(score) FROM scores WHERE channel_msg_id=?", (channel_msg_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return 0, 0.0
    return int(row[0] or 0), float(row[1] or 0.0)

# ==========================================================
# ================== BOT 1: POSTING =========================
# ==========================================================

def format_gender(gender: str) -> str:
    return "COWO 🤵‍♂️" if gender.lower() == "cowo" else "CEWE 👩‍🦰"

def emoji_keyboard_initial(jenis, avg_text=""):
    # second row is rating button which opens score options
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍 0", callback_data=f"like|{jenis}"),
            InlineKeyboardButton("❤️ 0", callback_data=f"love|{jenis}"),
            InlineKeyboardButton("💦 0", callback_data=f"splash|{jenis}")
        ],
        [InlineKeyboardButton(f"🌟 Nilai {avg_text}", callback_data=f"nilai|{jenis}")]
    ])

# ========= CEK WAJIB JOIN =========
async def is_member(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(GROUP_NABRUTT_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning(f"Gagal cek member: {e}")
        return False

# ========= START POST =========
async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_member(context, user_id):
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("Gabung dulu ke GC 🔥", url=URL_NABRUTT)]])
        await update.message.reply_text("⚠️ Kamu harus join GC Nabrutt dulu sebelum posting.", reply_markup=btn)
        return

    kb = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text(
        "Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ========= PILIH GENDER =========
async def pilih_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    gender = q.data.replace("gender_", "")
    user_data[q.from_user.id] = {"gender": gender}
    kb = [
        [InlineKeyboardButton("💌 Menfess", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎙 Moan", callback_data="jenis_moan")]
    ]
    await q.edit_message_text(
        f"Gender kamu: {format_gender(gender)} ✅\n\nPilih jenis posting:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ========= PILIH JENIS =========
async def pilih_jenis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    jenis = q.data.replace("jenis_", "")
    user_data[q.from_user.id]["jenis"] = jenis

    if jenis == "pap":
        kb = [
            [InlineKeyboardButton("😶 Blur Mata", callback_data="blur_mata")],
            [InlineKeyboardButton("😐 Blur Mulut", callback_data="blur_mulut")],
            [InlineKeyboardButton("🫥 Blur Seluruh", callback_data="blur_full")],
            [InlineKeyboardButton("🔲 Tanpa Blur", callback_data="blur_none")]
        ]
        await q.edit_message_text("Pilih efek blur untuk foto kamu:", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await q.edit_message_text(f"Kirim konten untuk {jenis.upper()} sekarang!")

# ========= PILIH BLUR =========
async def pilih_blur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    blur = q.data.replace("blur_", "")
    user_data[q.from_user.id]["blur"] = blur
    await q.edit_message_text(f"Efek blur: {blur.upper()} ✅\n\nSekarang kirim fotonya!")

# ========= IMAGE BLUR APPLY =========
async def apply_blur(photo_bytes: bytes, mode: str = "none") -> BytesIO:
    if mode == "none":
        return BytesIO(photo_bytes)

    # decode image
    arr = np.frombuffer(photo_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return BytesIO(photo_bytes)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        if mode == "mata":
            y_end = y + int(h * 0.35)
            blur_area = img[y:y_end, x:x+w]
            img[y:y_end, x:x+w] = cv2.GaussianBlur(blur_area, (51, 51), 30)
        elif mode == "mulut":
            y_start = y + int(h * 0.6)
            blur_area = img[y_start:y+h, x:x+w]
            img[y_start:y+h, x:x+w] = cv2.GaussianBlur(blur_area, (51, 51), 30)
        else:  # full
            blur_area = img[y:y+h, x:x+w]
            img[y:y+h, x:x+w] = cv2.GaussianBlur(blur_area, (51, 51), 30)

    _, buffer = cv2.imencode('.jpg', img)
    return BytesIO(buffer.tobytes())

# ========= EMOJI REACT =========
async def handle_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = q.from_user.id
    msg = q.message
    action, jenis = q.data.split("|", 1)

    key = (msg.message_id)
    emoji_counter.setdefault(key, {"👍":0, "❤️":0, "💦":0})

    # prevent duplicate votes per user per message (simple in-memory check)
    voted_key = (msg.message_id, uid)
    if voted_key in post_meta:
        await q.answer("Kamu sudah vote.", show_alert=True)
        return

    post_meta[voted_key] = action

    if action == "like":
        emoji_counter[key]["👍"] += 1
    elif action == "love":
        emoji_counter[key]["❤️"] += 1
    elif action == "splash":
        emoji_counter[key]["💦"] += 1

    c = emoji_counter[key]
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"👍 {c['👍']}", callback_data=f"like|{jenis}"),
            InlineKeyboardButton(f"❤️ {c['❤️']}", callback_data=f"love|{jenis}"),
            InlineKeyboardButton(f"💦 {c['💦']}", callback_data=f"splash|{jenis}")
        ],
        [InlineKeyboardButton("🌟 Nilai", callback_data=f"nilai|{jenis}")]
    ])
    try:
        await msg.edit_reply_markup(kb)
    except Exception as e:
        logger.warning(f"Gagal update markup: {e}")

# ========= NILAI (rating) UI =========
async def nilai_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, jenis = q.data.split("|", 1)
    kb = [
        [
            InlineKeyboardButton("⭐ 1", callback_data=f"score|1"),
            InlineKeyboardButton("⭐⭐ 2", callback_data=f"score|2"),
            InlineKeyboardButton("⭐⭐⭐ 3", callback_data=f"score|3"),
            InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data=f"score|4"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data=f"score|5")
        ]
    ]
    await q.message.reply_text("Pilih nilai (1–5):", reply_markup=InlineKeyboardMarkup(kb))

async def pilih_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    score = int(q.data.split("|", 1)[1])
    # we expect this keyboard to be a reply to the group/thread message that references the channel post
    reply = q.message.reply_to_message
    if not reply:
        await q.edit_message_text("Gagal: tidak ada referensi postingan.")
        return

    # try to find channel_msg_id stored in post_meta by thread mapping
    target_channel_msg = None
    for ch_msg_id, info in post_meta.items():
        if isinstance(ch_msg_id, int) and info.get("thread_id") == reply.message_id:
            target_channel_msg = ch_msg_id
            break

    if target_channel_msg is None:
        # fallback: if reply contains link to channel, try parse
        text = reply.text_markdown or ""
        # naive parse not robust, but try to find last number
        import re
        m = re.search(r"/(\d+)", text)
        if m:
            target_channel_msg = int(m.group(1))

    if not target_channel_msg:
        await q.edit_message_text("Gagal: tidak dapat menemukan posting terkait untuk dinilai.")
        return

    add_score_db(target_channel_msg, q.from_user.id, score)
    count, avg = get_score_stats(target_channel_msg)
    avg_str = f"{avg:.1f}" if count else "-"

    # update caption in channel post to show new average
    try:
        await context.bot.edit_message_caption(
            chat_id=CHANNEL_PAP_ID,
            message_id=target_channel_msg,
            caption=(await get_channel_caption(context, CHANNEL_PAP_ID, target_channel_msg)) + f"\n\n⭐ Rata-rata: {avg_str} ({count} penilai)"
        )
    except Exception as e:
        logger.warning(f"Gagal update caption rata-rata: {e}")

    await q.edit_message_text("Terima kasih atas penilaianmu ⭐")

async def get_channel_caption(context, chat_id, message_id):
    try:
        msg = await context.bot.get_chat(chat_id)
        # get_message isn't available; instead we store caption when posting
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT caption FROM posts WHERE channel_msg_id=?", (message_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row and row[0] else ""
    except Exception:
        return ""

# ========= HANDLE PESAN (posting dan comment thread) =========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Posting flow when user is composing
    if update.message.photo and update.effective_user.id in user_data:
        uid = update.effective_user.id
        state = user_data.get(uid, {})
        jenis = state.get("jenis")
        gender_raw = state.get("gender")
        caption = update.message.caption or update.message.text or ""
        gender = format_gender(gender_raw or "cowo")
        header_img = IMG_COWO if gender_raw == "cowo" else IMG_CEWE

        if jenis == "menfess":
            sent = await context.bot.send_photo(
                CHANNEL_MENFESS_ID, photo=header_img,
                caption=f"💌 MENFESS 18+\n🕵️ Gender: {gender}\n\n{caption}",
                reply_markup=emoji_keyboard_initial("menfess"), has_spoiler=True
            )
            # no thread for menfess

        elif jenis == "pap":
            fid = update.message.photo[-1].file_id
            f = await context.bot.get_file(fid)
            photo_bytes = await f.download_as_bytearray()
            blur_mode = state.get("blur", "none")
            blurred_io = await apply_blur(photo_bytes, blur_mode)
            blurred_io.seek(0)

            # send to channel
            sent = await context.bot.send_photo(
                CHANNEL_PAP_ID,
                photo=InputFile(blurred_io, filename="pap.jpg"),
                caption=f"📸 PAPBRUTT\n🕵️ Gender: {gender}\nEfek blur: {blur_mode.upper()}\n\n{caption}",
                reply_markup=emoji_keyboard_initial("pap"),
                has_spoiler=True
            )

            channel_msg_id = sent.message_id

            # Try to create a forum topic (thread) in the discussion group if supported
            thread_id = None
            try:
                # create topic with a short title
                topic_title = f"Diskusi PAP {channel_msg_id}"
                res = await context.bot.create_forum_topic(GROUP_DISKUSI_ID, topic_title)
                thread_id = res.message_thread_id
                # Post link message into topic
                link_text = f"💬 Diskusi untuk postingan ini: https://t.me/c/{str(CHANNEL_PAP_ID)[4:]}/{channel_msg_id}"
                await context.bot.send_message(GROUP_DISKUSI_ID, link_text, message_thread_id=thread_id)
            except Exception as e:
                logger.info(f"create_forum_topic tidak tersedia atau gagal: {e}")
                # fallback: send a normal message in group and use its message_id as thread marker
                msg = await context.bot.send_message(GROUP_DISKUSI_ID, f"💬 Diskusi untuk postingan https://t.me/c/{str(CHANNEL_PAP_ID)[4:]}/{channel_msg_id}")
                thread_id = msg.message_id

            # save metadata in memory and DB
            post_meta[channel_msg_id] = {"thread_id": thread_id, "owner": uid, "jenis": "pap"}
            save_post_db(channel_msg_id, thread_id, uid, "pap", caption)

        elif jenis == "moan" and update.message.voice:
            fid = update.message.voice.file_id
            await context.bot.send_voice(
                CHANNEL_MOAN_ID, voice=fid,
                caption=f"🎙 MOANBRUTT\n🕵️ Gender: {gender}\n\n{caption}",
                reply_markup=emoji_keyboard_initial("moan")
            )

        # clear state for user
        user_data.pop(uid, None)
        return

    # COMMENT HANDLER: route comments into the correct per-post thread
    # We expect discussion happens in GROUP_DISKUSI_ID. If a user replies to the system thread message, we repost into that thread only.
    if update.message.chat_id == GROUP_DISKUSI_ID and update.message.reply_to_message:
        replied = update.message.reply_to_message
        # find matching post by thread_id or by link in replied message
        target_channel_msg = None
        for ch_id, info in post_meta.items():
            if info.get("thread_id") == replied.message_id:
                target_channel_msg = ch_id
                thread_id = info.get("thread_id")
                break
        # if found, forward comment into the same thread as a formatted message
        if target_channel_msg:
            user = update.effective_user
            txt = update.message.text or "[media comment]"
            await context.bot.send_message(
                GROUP_DISKUSI_ID,
                text=f"💬 Komentar oleh {user.mention_html()}:\n\n{txt}",
                parse_mode="HTML",
                message_thread_id=thread_id
            )
            # Optionally, notify the owner via DM (only if not the commenter)
            owner = post_meta[target_channel_msg]["owner"]
            if owner != user.id:
                try:
                    await context.bot.send_message(owner, f"Komentar baru di postinganmu (id {target_channel_msg}):\n{txt}")
                except Exception:
                    pass
            return

# ========= BUILD BOT POSTING =========
def create_app_posting():
    app = Application.builder().token(TOKEN_POSTING).build()
    app.add_handler(CommandHandler("start", start_post))
    app.add_handler(CallbackQueryHandler(pilih_gender, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(pilih_jenis, pattern="^jenis_"))
    app.add_handler(CallbackQueryHandler(pilih_blur, pattern="^blur_"))
    app.add_handler(CallbackQueryHandler(handle_emoji, pattern=r"^(like|love|splash)\|"))
    app.add_handler(CallbackQueryHandler(nilai_post, pattern=r"^nilai\|"))
    app.add_handler(CallbackQueryHandler(pilih_score, pattern=r"^score\|"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    return app

# ==========================================================
# ================== BOT 2: WELCOME =========================
# ==========================================================

def build_links_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(t, url=u)] for t, u in LINKS])

async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    await req.approve()
    user = req.from_user
    await context.bot.send_message(
        req.chat.id,
        text=f"🌟 Selamat datang {user.mention_html()}!\nKlik tombol di bawah untuk akses semua area!",
        parse_mode="HTML",
        reply_markup=build_links_keyboard()
    )

def create_app_welcome():
    app = Application.builder().token(TOKEN_WELCOME).build()
    app.add_handler(ChatJoinRequestHandler(join_request_handler))
    return app

# ==========================================================
# ================== FLASK SERVER ==========================
# ==========================================================
flask_app = Flask(__name__)
posting_app = create_app_posting()
welcome_app = create_app_welcome()

# Buat event loop global untuk Render
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

@flask_app.route("/")
def home():
    return "🚀 NABRUTT BOT Webhook aktif!"

@flask_app.route("/posting", methods=["POST"])
def webhook_posting():
    update = Update.de_json(request.get_json(force=True), posting_app.bot)
    asyncio.run_coroutine_threadsafe(posting_app.process_update(update), loop)
    return "ok", 200

@flask_app.route("/welcome", methods=["POST"])
def webhook_welcome():
    update = Update.de_json(request.get_json(force=True), welcome_app.bot)
    asyncio.run_coroutine_threadsafe(welcome_app.process_update(update), loop)
    return "ok", 200

# ==========================================================
# ================== SETUP WEBHOOK ==========================
# ==========================================================
async def setup_webhooks():
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "https://telegram-nakal-bot.onrender.com").rstrip("/")
    await posting_app.bot.set_webhook(f"{base_url}/posting")
    await welcome_app.bot.set_webhook(f"{base_url}/welcome")
    logger.info(f"✅ Webhook diset ke {base_url}")

# ==========================================================
# ================== MAIN ==================================
# ==========================================================
if __name__ == "__main__":
    init_db()

    async def main():
        await posting_app.initialize()
        await welcome_app.initialize()
        await setup_webhooks()
        # run flask app in current thread (blocking)
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    asyncio.run(main())
