import asyncio, nest_asyncio, random, string, time
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from .config import *
from .db import init_db, connect, get_setting, set_setting

nest_asyncio.apply()
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def gen_key(days):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)), days

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT redeemed_count, premium_until, is_banned FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if row and row[2] == 1:
        await update.message.reply_text("🚫 You are banned!")
        con.close()
        return

    if not row:
        cur.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
        con.commit()
        redeemed_count, premium_until = 0, 0
    else:
        redeemed_count, premium_until = row[0], row[1]

    now = int(time.time())
    free_unlimited = get_setting("free_unlimited") == "1"

    if premium_until > now or free_unlimited or redeemed_count == 0:
        await update.message.reply_text("✅ Processing your redeem request...")
        cur.execute("UPDATE users SET redeemed_count = redeemed_count + 1 WHERE user_id=?", (user_id,))
        con.commit()
    else:
        await update.message.reply_text(PURCHASE_TEXT)
    con.close()

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /premium <key>")
        return
    key_input = context.args[0]

    con = connect()
    cur = con.cursor()
    cur.execute("SELECT days, used_by FROM keys WHERE key=?", (key_input,))
    row = cur.fetchone()
    if not row:
        await update.message.reply_text("❌ Invalid key!")
    elif row[1] is not None:
        await update.message.reply_text("❌ Key already used!")
    else:
        days = row[0]
        premium_until = int(time.time()) + days*86400
        cur.execute("UPDATE users SET premium_until=? WHERE user_id=?", (premium_until, user_id))
        cur.execute("UPDATE keys SET used_by=? WHERE key=?", (user_id, key_input))
        con.commit()
        await update.message.reply_text("✅ Premium Activated ⚡️")
        await context.bot.send_message(ADMIN_ID, f"User {user_id} activated premium for {days} days.")
    con.close()

async def genk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /genk <days>")
        return
    days = int(context.args[0])
    key, _ = gen_key(days)
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO keys(key, days) VALUES(?, ?)", (key, days))
    con.commit()
    con.close()
    await update.message.reply_text(f"Generated Key: {key} ({days} days)")

async def toggle_service(update: Update, context: ContextTypes.DEFAULT_TYPE, on=True):
    if update.effective_user.id != ADMIN_ID:
        return
    set_setting("free_unlimited", "1" if on else "0")
    msg = SERVICE_ON_TEXT if on else SERVICE_OFF_TEXT
    await update.message.reply_text(msg)

def main():
    init_db()
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("premium", premium))
    application.add_handler(CommandHandler("genk", genk))
    application.add_handler(CommandHandler("on", lambda u, c: toggle_service(u, c, True)))
    application.add_handler(CommandHandler("off", lambda u, c: toggle_service(u, c, False)))

    loop = asyncio.get_event_loop()
    loop.create_task(application.run_polling())
    app.run(host=HOST, port=PORT)

if __name__ == "__main__":
    main()
