import os, sqlite3, random
from datetime import datetime
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

# ---------------- Flask ----------------
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Bot jalan di Render!"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "ok"

# ---------------- Konfigurasi ----------------
TOKEN = os.environ.get("BOT_TOKEN", "ISI_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://YOUR-RENDER-URL/telegram")

CHANNEL_MAP = {
    "MENFESS": -1003033445498,
    "DONASI": -1003189592682,
    "MOAN":   -1003196180758
}
THREAD_MAP = {"MENFESS": 1036, "DONASI": 393, "MOAN": 1038}

# ---------------- Database ----------------
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

def save_rating(mid, uid, stage, score):
    c.execute("""
    INSERT INTO ratings (message_id,user_id,stage_name,score)
    VALUES (?,?,?,?)
    ON CONFLICT(message_id,user_id)
    DO UPDATE SET score=excluded.score
    """,(mid,str(uid),stage,score))
    conn.commit()

def get_average(mid):
    c.execute("SELECT score FROM ratings WHERE message_id=?", (mid,))
    rows = c.fetchall()
    return round(sum(r[0] for r in rows)/len(rows),1) if rows else 0

# ---------------- Bot Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("MENFESS 18+", callback_data="START_MENFESS")],
        [InlineKeyboardButton("DONASI PAP CABUL", callback_data="START_DONASI")],
        [InlineKeyboardButton("MOAN 18+", callback_data="START_MOAN")],
    ])
    await update.message.reply_text("Selamat datang! Pilih topik:", reply_markup=kb)

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mid, rating = query.data.split("|")
    save_rating(mid, query.from_user.id, "Anon", int(rating))
    avg = get_average(mid)
    try:
        lines = query.message.caption.split("\n")
        for i,l in enumerate(lines):
            if l.startswith("🌟 RATING TERKINI:"):
                lines[i] = f"🌟 RATING TERKINI: {avg}"
        await context.bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            caption="\n".join(lines),
            parse_mode="HTML",
            reply_markup=query.message.reply_markup
        )
        await query.answer(f"Rating {rating} diterima")
    except:
        await query.answer("Gagal update rating")

# Tambahkan handler konten Anda di sini…

# ---------------- Scheduler ----------------
scheduler = AsyncIOScheduler()
scheduler.add_job(lambda: print("Reset harian..."), 'cron', hour=0, minute=0)
scheduler.start()

# ---------------- Build Application ----------------
bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(handle_rating, pattern=r"\d+\|\d+"))
# + handler lain sesuai kebutuhan

async def set_webhook():
    await bot_app.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    asyncio.get_event_loop().create_task(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
