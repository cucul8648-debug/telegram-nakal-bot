# filename: main.py
# requirements:
# python-telegram-bot==20.3
# Flask==2.3.3

import os
import logging
import asyncio
import threading
import sqlite3
from pathlib import Path
from flask import Flask, request
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ---------------- CONFIG ----------------
TOKEN_POSTING     = "8466148433:AAHG4-yrXyHvV2yJb0C9WcGOcSvWevCz9M8"  # ganti token bot posting-mu
# Channel / Group IDs (ganti sesuai kebutuhan)
CHANNEL_MENFESS_ID = -1002989043936
CHANNEL_PAP_ID     = -1003189592682
CHANNEL_MOAN_ID    = -1003196180758
CHANNEL_VIDEO_ID   = -1003201234567  # ganti dengan ID channel video jika pakai
GROUP_NABRUTT_ID   = -1003098333444
URL_NABRUTT        = "https://t.me/+a3Bd3FDl5HY2NjFl"

# Header images (raw github URLs)
IMG_PapBrutt_COWO   = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cowo.png"
IMG_VideoBrutt_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cowo.png"
IMG_MoanBrutt_COWO  = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cowo.png"
IMG_MenfessBrutt_COWO = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cowo.png"

IMG_PapBrutt_CEWE   = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/PapBrutt_Cewe.png"
IMG_VideoBrutt_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/VideoBrutt_Cewe.png"
IMG_MoanBrutt_CEWE  = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MoanBrutt_Cewe.png"
IMG_MenfessBrutt_CEWE = "https://raw.githubusercontent.com/cucul8648-debug/telegram-nakal-bot/main/MenfessBrutt_Cewe.png"

# ---------------- logging ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- in-memory user flow ----------------
user_data = {}  # {user_id: {"gender": "cowo"/"cewe", "jenis": "pap"/"video"/"moan"/"menfess"}}

# ---------------- database ----------------
DB_DIR = Path(".")
DB_RATING = DB_DIR / "rating.db"
DB_REACT  = DB_DIR / "reactions.db"

def init_db():
    conn = sqlite3.connect(DB_RATING)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER,
            user_id INTEGER,
            nilai INTEGER,
            UNIQUE(message_id, user_id)
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_REACT)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER,
            user_id INTEGER,
            reaction TEXT,
            UNIQUE(message_id, user_id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- helper ----------------
def format_gender_text(g: str) -> str:
    return "COWO 🤵‍♂" if g.lower() == "cowo" else "CEWE 👩‍🦰"

def tag_gender(g: str) -> str:
    return "#COWO" if g.lower() == "cowo" else "#CEWE"

def build_react_rating_keyboard(message_id: int):
    """
    Build keyboard by reading counts from DB for a given message_id.
    If DB empty for message, shows zeros.
    """
    # read reaction counts
    conn = sqlite3.connect(DB_REACT)
    c = conn.cursor()
    c.execute("SELECT reaction, COUNT(*) FROM reactions WHERE message_id = ? GROUP BY reaction", (message_id,))
    react_counts = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    like = react_counts.get("like", 0)
    love = react_counts.get("love", 0)
    splash = react_counts.get("splash", 0)

    # ratings distribution
    conn = sqlite3.connect(DB_RATING)
    c = conn.cursor()
    c.execute("SELECT nilai, COUNT(*) FROM ratings WHERE message_id = ? GROUP BY nilai ORDER BY nilai", (message_id,))
    distrib = {row[0]: row[1] for row in c.fetchall()}
    conn.close()

    # react row
    react_row = [
        InlineKeyboardButton(f"👍 {like}", callback_data=f"like|{message_id}"),
        InlineKeyboardButton(f"❤️ {love}", callback_data=f"love|{message_id}"),
        InlineKeyboardButton(f"💦 {splash}", callback_data=f"splash|{message_id}")
    ]

    # rating buttons 1..10 with counts
    rating_buttons = [
        InlineKeyboardButton(f"{i} ({distrib.get(i,0)})", callback_data=f"rate|{message_id}|{i}") for i in range(1, 11)
    ]

    kb = InlineKeyboardMarkup([
        react_row,
        rating_buttons[:5],
        rating_buttons[5:],
        [InlineKeyboardButton("👥 Gabung GC Nabrutt", url=URL_NABRUTT)]
    ])
    return kb

def insert_rating_db(message_id: int, user_id: int, nilai: int) -> bool:
    conn = sqlite3.connect(DB_RATING)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO ratings (message_id, user_id, nilai) VALUES (?, ?, ?)", (message_id, user_id, nilai))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def insert_reaction_db(message_id: int, user_id: int, reaction: str) -> bool:
    conn = sqlite3.connect(DB_REACT)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO reactions (message_id, user_id, reaction) VALUES (?, ?, ?)", (message_id, user_id, reaction))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def rating_stats_from_db(message_id: int):
    conn = sqlite3.connect(DB_RATING)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), AVG(nilai) FROM ratings WHERE message_id = ?", (message_id,))
    total, avg = c.fetchone()
    conn.close()
    return int(total or 0), float(avg or 0.0)

# ---------------- keyboards ----------------
def jenis_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 Menfess", callback_data="jenis_menfess")],
        [InlineKeyboardButton("📸 Pap", callback_data="jenis_pap")],
        [InlineKeyboardButton("🎥 Video", callback_data="jenis_video")],
        [InlineKeyboardButton("🎧 Moan", callback_data="jenis_moan")]
    ])

# ---------------- bot flows ----------------
async def start_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # require group membership check (optional). If want to skip, comment out next lines.
    try:
        member = await context.bot.get_chat_member(GROUP_NABRUTT_ID, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("Gabung dulu ke GC 🔥", url=URL_NABRUTT)]])
            await update.message.reply_text("⚠️ Kamu harus join GC Nabrutt dulu sebelum posting.", reply_markup=kb)
            return
    except Exception:
        # fallback: allow
        pass

    kb = [
        [InlineKeyboardButton("🤵‍♂ Cowok", callback_data="gender_cowo")],
        [InlineKeyboardButton("👩‍🦰 Cewek", callback_data="gender_cewe")]
    ]
    await update.message.reply_text("Selamat datang di EksibNih 🤖\n\nPilih jenis kelaminmu dulu:", reply_markup=InlineKeyboardMarkup(kb))

async def pilih_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    gender = q.data.replace("gender_", "")
    user_data[q.from_user.id] = {"gender": gender}
    await q.edit_message_text(f"Gender kamu: {format_gender_text(gender)} ✅\n\nPilih jenis posting:", reply_markup=jenis_keyboard())

async def pilih_jenis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    jenis = q.data.replace("jenis_", "")
    user_data[q.from_user.id]["jenis"] = jenis
    await q.edit_message_text(f"Kirim konten untuk {jenis.upper()} sekarang!")

# ---------------- handle incoming content and send to channel ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_data:
        await update.message.reply_text("Silakan /start dulu untuk memilih gender & jenis posting.")
        return

    info = user_data[uid]
    gender = info["gender"]
    jenis = info["jenis"]
    caption_user = update.message.caption or update.message.text or ""
    gender_txt = format_gender_text(gender)
    hashtag = tag_gender(gender)

    # choose header image
    img_header = {
        "cowo": {
            "pap": IMG_PapBrutt_COWO,
            "video": IMG_VideoBrutt_COWO,
            "moan": IMG_MoanBrutt_COWO,
            "menfess": IMG_MenfessBrutt_COWO
        },
        "cewe": {
            "pap": IMG_PapBrutt_CEWE,
            "video": IMG_VideoBrutt_CEWE,
            "moan": IMG_MoanBrutt_CEWE,
            "menfess": IMG_MenfessBrutt_CEWE
        }
    }[gender]

    # base caption with quote block for gender & rating placeholder (0)
    if jenis == "menfess":
        caption = (
            f"MENFESSBRUTT 💌\n\n"
            f"> Gender 🕵️ : {gender_txt}\n"
            f"> ⭐ Rating saat ini: 0.0 / 10 (0 penilai)\n\n"
            f"Hallo {caption_user}\n\n"
            f"{hashtag}"
        )
    else:
        title = "PAPBRUTT 📸" if jenis == "pap" else ("VIDEOBRUTT 🎥" if jenis == "video" else "MOANBRUTT 🎧")
        caption = (
            f"{title}\n\n"
            f"> GENDER 🕵️ : {gender_txt}\n"
            f"> ⭐ Rating saat ini: 0.0 / 10 (0 penilai)\n"
            f"> 💬 Berikan react dan nilai!\n\n"
            f"{caption_user}\n\n"
            f"{hashtag}"
        )

    # target channel by jenis
    target = CHANNEL_PAP_ID
    if jenis == "menfess":
        target = CHANNEL_MENFESS_ID
    elif jenis == "moan":
        target = CHANNEL_MOAN_ID
    elif jenis == "video":
        target = CHANNEL_VIDEO_ID

    sent_message = None
    try:
        # send by content type: photo preferred for pap & menfess (use header image if no photo)
        if jenis == "pap":
            if update.message.photo:
                sent_message = await context.bot.send_photo(
                    chat_id=target,
                    photo=update.message.photo[-1].file_id,
                    caption=caption,
                    reply_markup=build_react_rating_keyboard(0),  # temp keyboard, will replace with correct message_id below
                    has_spoiler=True
                )
            else:
                # if user didn't attach photo, send header image
                sent_message = await context.bot.send_photo(
                    chat_id=target,
                    photo=img_header,
                    caption=caption,
                    reply_markup=build_react_rating_keyboard(0),
                    has_spoiler=True
                )
        elif jenis == "video":
            if update.message.video:
                sent_message = await context.bot.send_video(
                    chat_id=target,
                    video=update.message.video.file_id,
                    caption=caption,
                    reply_markup=build_react_rating_keyboard(0),
                    has_spoiler=True
                )
            else:
                # fallback: send header image with caption, user didn't provide video
                sent_message = await context.bot.send_photo(
                    chat_id=target,
                    photo=img_header,
                    caption=caption,
                    reply_markup=build_react_rating_keyboard(0),
                    has_spoiler=True
                )
        elif jenis == "moan":
            if update.message.voice:
                sent_message = await context.bot.send_voice(
                    chat_id=target,
                    voice=update.message.voice.file_id,
                    caption=caption,
                    reply_markup=build_react_rating_keyboard(0)
                )
            else:
                # fallback to header photo
                sent_message = await context.bot.send_photo(
                    chat_id=target,
                    photo=img_header,
                    caption=caption,
                    reply_markup=build_react_rating_keyboard(0)
                )
        elif jenis == "menfess":
            # menfess always send header image + caption
            sent_message = await context.bot.send_photo(
                chat_id=target,
                photo=img_header,
                caption=caption,
                reply_markup=build_react_rating_keyboard(0),
                has_spoiler=True
            )
    except Exception as e:
        logger.exception("Gagal mengirim ke channel: %s", e)
        await update.message.reply_text("Gagal mengirim posting. Pastikan bot admin di channel.")
        return

    # now we have message_id of sent posting; rebuild keyboard with real message_id
    if sent_message:
        mid = sent_message.message_id
        kb = build_react_rating_keyboard(mid)
        # Update caption to include rating placeholder with message_id counts (0)
        # but keep quote block: replace > ⭐ Rating saat ini: ... to keep 0.0
        # Build new caption with updated rating (0)
        total_votes, avg = rating_stats_from_db(mid)
        avg = round(avg, 1) if total_votes else 0.0

        # Insert rating under gender line in caption
        parts = (sent_message.caption or caption).split("\n")
        # replace any existing > ⭐ Rating line if present
        parts = [l for l in parts if not l.strip().startswith("> ⭐ Rating")]
        # find index of gender quote block and insert after it
        for idx, line in enumerate(parts):
            if line.strip().startswith("> Gender") or line.strip().startswith("> GENDER"):
                parts.insert(idx + 1, f"> ⭐ Rating saat ini: {avg:.1f} / 10 ({total_votes} penilai)")
                break
        else:
            # fallback append near top
            parts.insert(1, f"> ⭐ Rating saat ini: {avg:.1f} / 10 ({total_votes} penilai)")

        new_caption = "\n".join(parts)
        try:
            await context.bot.edit_message_caption(chat_id=target, message_id=mid, caption=new_caption, reply_markup=kb)
        except Exception as e:
            logger.warning("Gagal edit caption awal: %s", e)

# ---------------- callback: reactions ----------------
async def handle_react_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data  # e.g. "like|<message_id>"
    try:
        action, mid_str = data.split("|", 1)
        mid = int(mid_str)
    except Exception:
        await q.answer("Data invalid.", show_alert=True)
        return

    uid = q.from_user.id
    # try insert reaction
    ok = insert_reaction_db(mid, uid, action)
    if not ok:
        await q.answer("Kamu sudah memberi react di posting ini.", show_alert=True)
        return

    # rebuild keyboard and update counts on message
    kb = build_react_rating_keyboard(mid)
    # update message reply_markup in channel
    try:
        # We don't know channel id easily, but we can attempt to edit by using the chat id of the callback origin if it's same. 
        # Callback usually originates from channel message; q.message points to the channel message.
        await q.message.edit_reply_markup(reply_markup=kb)
    except Exception as e:
        logger.warning("Gagal update reply_markup react: %s", e)

    await q.answer("✅ React tersimpan!")

# ---------------- callback: rating ----------------
async def handle_rate_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data  # e.g. "rate|<message_id>|<nilai>"
    try:
        _, mid_str, nilai_str = data.split("|")
        mid = int(mid_str); nilai = int(nilai_str)
    except Exception:
        await q.answer("Data invalid.", show_alert=True)
        return

    uid = q.from_user.id
    ok = insert_rating_db(mid, uid, nilai)
    if not ok:
        await q.answer("Kamu sudah memberi rating sebelumnya.", show_alert=True)
        return

    # compute stats from DB
    total_votes, avg = rating_stats_from_db(mid)
    avg = round(avg, 1) if total_votes else 0.0

    # rebuild keyboard and edit both reply_markup and caption (quote block)
    kb = build_react_rating_keyboard(mid)

    try:
        # edit reply_markup
        await q.message.edit_reply_markup(reply_markup=kb)
    except Exception as e:
        logger.warning("Gagal update reply_markup rating: %s", e)

    # edit caption: maintain quote block and insert/update rating line right under gender
    caption = q.message.caption or ""
    lines = caption.split("\n")
    # remove any existing rating quote line
    lines = [l for l in lines if not l.strip().startswith("> ⭐ Rating")]
    # find gender line index
    inserted = False
    for idx, l in enumerate(lines):
        if l.strip().lower().startswith("> gender") or l.strip().lower().startswith("> gender") or l.strip().startswith("> GENDER"):
            lines.insert(idx + 1, f"> ⭐ Rating saat ini: {avg:.1f} / 10 ({total_votes} penilai)")
            inserted = True
            break
    if not inserted:
        # fallback: insert after first non-empty line
        for idx, l in enumerate(lines):
            if l.strip():
                lines.insert(idx + 1, f"> ⭐ Rating saat ini: {avg:.1f} / 10 ({total_votes} penilai)")
                inserted = True
                break
    new_caption = "\n".join(lines)
    try:
        await q.message.edit_caption(caption=new_caption, reply_markup=kb)
    except Exception as e:
        logger.warning("Gagal edit caption rating: %s", e)

    await q.answer(f"✅ Rating {nilai}/10 tersimpan!")

# ---------------- build app ----------------
def create_app_posting():
    app = Application.builder().token(TOKEN_POSTING).build()
    app.add_handler(CommandHandler("start", start_post))
    app.add_handler(CallbackQueryHandler(pilih_gender, "^gender_"))
    app.add_handler(CallbackQueryHandler(pilih_jenis, "^jenis_"))
    app.add_handler(CallbackQueryHandler(handle_react_cb, r"^(like|love|splash)\|"))
    app.add_handler(CallbackQueryHandler(handle_rate_cb, r"^rate\|"))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    return app

# ---------------- Flask webhook ----------------
flask_app = Flask(__name__)
posting_app = create_app_posting()

# Create and run event loop on background thread
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

@flask_app.route("/", methods=["GET"])
def home():
    return "Nabrutt Posting Bot Active"

@flask_app.route("/posting", methods=["POST"])
def webhook_posting():
    update = Update.de_json(request.get_json(force=True), posting_app.bot)
    asyncio.run_coroutine_threadsafe(posting_app.process_update(update), loop)
    return "ok", 200

async def setup_webhook():
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "https://telegram-nakal-bot.onrender.com").rstrip("/")
    await posting_app.bot.set_webhook(f"{base_url}/posting")
    logger.info("Webhook set to %s/posting", base_url)

if __name__ == "__main__":
    async def main():
        await posting_app.initialize()
        await setup_webhook()
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    asyncio.run(main())
