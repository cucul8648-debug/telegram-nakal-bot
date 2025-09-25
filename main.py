import sqlite3
import random
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from flask import Flask
import threading

# ---------- Flask App ----------
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot jalan di Render!"

# ---------- Konfigurasi ----------
TOKEN = "8466148433:AAH0yuuC3zetTYRysTkxmfCnc9JTqdwcXpI"
GC_NABRUTT = -1003098333444
DISCUSSION_GROUP = -1003033445498

CHANNEL_MAP = {
    "MENFESS": -1003033445498,
    "DONASI": -1003189592682,
    "MOAN": -1003196180758
}
THREAD_MAP = {"MENFESS": 1036, "DONASI": 393, "MOAN": 1038}

COVER_CEWE = "https://telegra.ph/file/7a2d41a6ddf9-cover-cewe.jpg"
COVER_COWO = "https://telegra.ph/file/9bb77a6d9d0b-cover-cowo.jpg"
counter = {"views": 10, "comments": 5}

# ---------- Database ----------
conn = sqlite3.connect("ratings.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS ratings (
    message_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    stage_name TEXT,
    score INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(message_id, user_id)
)
""")
conn.commit()

def save_rating(message_id: str, user_id: str, stage_name: str, score: int):
    c.execute("""
    INSERT INTO ratings (message_id, user_id, stage_name, score)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(message_id, user_id) DO UPDATE SET score=excluded.score
    """, (message_id, str(user_id), stage_name, score))
    conn.commit()

def get_average_rating(message_id: str):
    c.execute("SELECT score FROM ratings WHERE message_id=?", (message_id,))
    rows = c.fetchall()
    if not rows:
        return 0
    return round(sum(r[0] for r in rows) / len(rows), 1)

def get_top_alltime(limit=3):
    c.execute("""
        SELECT stage_name, AVG(score) as avg_score
        FROM ratings
        GROUP BY message_id
        ORDER BY avg_score DESC
        LIMIT ?
    """, (limit,))
    return c.fetchall()

def get_top_today(limit=3):
    c.execute("""
        SELECT stage_name, AVG(score) as avg_score
        FROM ratings
        WHERE DATE(timestamp) = DATE('now','localtime')
        GROUP BY message_id
        ORDER BY avg_score DESC
        LIMIT ?
    """, (limit,))
    return c.fetchall()

# ---------- Scheduler ----------
scheduler = AsyncIOScheduler()
def reset_top_daily():
    print("✅ Reset top harian (data rating tetap tersimpan)")
scheduler.add_job(reset_top_daily, 'cron', hour=0, minute=0)
scheduler.start()

# ---------- Bot Handlers ----------
def rating_keyboard(message_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(str(i), callback_data=f"{message_id}|{i}") for i in range(1, 6)],
        [InlineKeyboardButton(str(i), callback_data=f"{message_id}|{i}") for i in range(6, 11)]
    ])

async def handle_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global counter
    caption_user = update.message.caption or update.message.text or "Tanpa keterangan"
    stage_name = caption_user.split()[0] if caption_user else "Anon"

    is_media = bool(update.message.photo or update.message.video)
    is_audio = bool(update.message.voice or update.message.audio)
    is_text = bool(update.message.text and not update.message.caption)

    gender, emoji, cover = "CEWE", "👙", COVER_CEWE
    if "COWO" in caption_user.upper():
        if is_media:
            gender, emoji, cover = "COWO", "🩲", COVER_COWO
        elif is_audio or is_text:
            gender, emoji, cover = "COWO", "🧒", COVER_COWO
    else:
        if is_audio or is_text:
            gender, emoji, cover = "CEWE", "🧕", COVER_CEWE

    counter["views"] += random.randint(2, 8)
    counter["comments"] += random.randint(0, 3)

    category = next((k for k in CHANNEL_MAP if k in caption_user.upper()), None)
    if not category:
        await update.message.reply_text("❌ Tidak ada kategori cocok (MENFESS / DONASI / MOAN).")
        return

    target_ch, thread_id = CHANNEL_MAP[category], THREAD_MAP[category]
    caption_channel = (
        f"📌 GENDER: {gender}\n"
        f"{emoji} {caption_user}\n\n"
        f"✨ INSTRUKSI ✨\n"
        f"👉 Tekan tombol rating di bawah\n"
        f"👉 Komentar? Join diskusi (link di bawah)\n\n"
        f"#{gender}\n\n"
        f"👁️ {counter['views']}   💬 {counter['comments']}   🤖 Bot\n\n"
        f"🌟 RATING TERKINI: -\n"
        f"💬 Diskusi: https://t.me/c/1003033445498"
    )

    kb = rating_keyboard("tmp")
    msg = None
    if category == "MENFESS" and update.message.text:
        msg = await context.bot.send_message(chat_id=target_ch, text=caption_channel,
                                             parse_mode="HTML", reply_markup=kb)
    elif category == "DONASI":
        if update.message.photo:
            msg = await context.bot.send_photo(chat_id=target_ch, photo=update.message.photo[-1].file_id,
                                               caption=caption_channel, parse_mode="HTML", has_spoiler=True, reply_markup=kb)
        elif update.message.video:
            msg = await context.bot.send_video(chat_id=target_ch, video=update.message.video.file_id,
                                               caption=caption_channel, parse_mode="HTML", has_spoiler=True, reply_markup=kb)
    elif category == "MOAN":
        if update.message.voice:
            msg = await context.bot.send_voice(chat_id=target_ch, voice=update.message.voice.file_id,
                                               caption=caption_channel, parse_mode="HTML", reply_markup=kb)
        elif update.message.audio:
            msg = await context.bot.send_audio(chat_id=target_ch, audio=update.message.audio.file_id,
                                               caption=caption_channel, parse_mode="HTML", reply_markup=kb)
    else:
        await update.message.reply_text(f"❌ Format konten tidak sesuai untuk kategori {category}.")
        return

    if msg:
        await context.bot.edit_message_reply_markup(chat_id=target_ch, message_id=msg.message_id,
                                                    reply_markup=rating_keyboard(msg.message_id))
        link = f"https://t.me/c/{str(target_ch)[4:]}/{msg.message_id}"
        info_text = f"📢 {category} 18+\n👤 Gender: {gender}\n👉 Klik tombol untuk lihat full di channel"
        keyboard_info = InlineKeyboardMarkup([[InlineKeyboardButton("🔞 Lihat Full", url=link)]])
        await context.bot.send_message(chat_id=GC_NABRUTT, text=info_text, parse_mode="HTML",
                                       message_thread_id=thread_id, reply_markup=keyboard_info)

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    rating = int(query.data.split("|")[1])
    message_id = query.data.split("|")[0]

    save_rating(message_id, user_id, "Anon", rating)
    avg = get_average_rating(message_id)

    try:
        caption_lines = query.message.caption.split("\n")
        for i, line in enumerate(caption_lines):
            if line.startswith("🌟 RATING TERKINI:"):
                caption_lines[i] = f"🌟 RATING TERKINI: {avg}"
        await context.bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            caption="\n".join(caption_lines),
            parse_mode="HTML",
            reply_markup=query.message.reply_markup,
        )
        await query.answer(f"✅ Rating {rating} diterima (anonim)")
    except Exception:
        await query.answer("⚠️ Terjadi kesalahan")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MENFESS 18+", callback_data="START_MENFESS")],
        [InlineKeyboardButton("DONASI PAP CABUL", callback_data="START_DONASI")],
        [InlineKeyboardButton("MOAN 18+", callback_data="START_MOAN")],
        [InlineKeyboardButton("Top Terbaik", callback_data="TOP_ALL")],
        [InlineKeyboardButton("Top Hari Ini", callback_data="TOP_TODAY")]
    ])
    await update.message.reply_text("Selamat datang! Pilih topik:", reply_markup=keyboard)

async def inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("START_"):
        category = query.data.split("_")[1]
        await query.answer(f"Silakan kirim konten untuk kategori {category}")
    elif query.data == "TOP_ALL":
        top = get_top_alltime()
        text = "📊 Top Terbaik Sepanjang Masa\n" + "\n".join(
            f"{i+1}. {n} - 🌟 {s}" for i, (n, s) in enumerate(top)
        )
        await query.message.edit_text(text)
    elif query.data == "TOP_TODAY":
        top = get_top_today()
        text = "📊 Top Terlonte Hari Ini\n" + "\n".join(
            f"{i+1}. {n} - 🌟 {s}" for i, (n, s) in enumerate(top)
        )
        await query.message.edit_text(text)

def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_content))
    app.add_handler(CallbackQueryHandler(handle_rating, pattern=r"\d+\|\d+"))
    app.add_handler(CallbackQueryHandler(inline_callback))
    print("Bot jalan...")
    app.run_polling()

if __name__ == "__main__":
    # Jalankan bot di thread terpisah, Flask jadi proses utama
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
