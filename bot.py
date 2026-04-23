from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

TOKEN = "8680039869:AAHIewnkNkH-7fRsp8TCzk0TqIEX_S2hXe0"

# DATABASE
conn = sqlite3.connect("gmute.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS muted (user_id INTEGER, chat_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY, chat_name TEXT)")
conn.commit()

# CHECK ADMIN
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    return member.status in ["administrator", "creator"]

# AUTO SAVE GROUP
async def save_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type in ["group", "supergroup"]:
        cursor.execute(
            "INSERT OR IGNORE INTO groups VALUES (?, ?)",
            (chat.id, chat.title)
        )
        conn.commit()

# GMUTE
async def gmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can use this")
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        chat_id = update.effective_chat.id

        cursor.execute(
            "INSERT INTO muted VALUES (?, ?)",
            (user_id, chat_id)
        )
        conn.commit()

        await update.message.reply_text("✅ User muted")
    else:
        await update.message.reply_text("Reply to user")

# UNGMUTE
async def ungmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only admins can use this")
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        chat_id = update.effective_chat.id

        cursor.execute(
            "DELETE FROM muted WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        )
        conn.commit()

        await update.message.reply_text("✅ User unmuted")
    else:
        await update.message.reply_text("Reply to user")

# DELETE MUTED MSG
async def delete_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id

    cursor.execute(
        "SELECT * FROM muted WHERE user_id=? AND chat_id=?",
        (user_id, chat_id)
    )
    result = cursor.fetchone()

    if result:
        try:
            await update.message.delete()
        except:
            pass

# SHOW GROUPS
async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT * FROM groups")
    data = cursor.fetchall()

    if not data:
        await update.message.reply_text("No groups found")
        return

    text = "📢 Bot Groups:\n\n"
    for chat_id, name in data:
        text += f"{name} → {chat_id}\n"

    await update.message.reply_text(text)

# MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("gmute", gmute))
app.add_handler(CommandHandler("ungmute", ungmute))
app.add_handler(CommandHandler("groups", groups))

app.add_handler(MessageHandler(filters.ALL, save_group))
app.add_handler(MessageHandler(filters.ALL, delete_msg))

print("Bot running...")
app.run_polling()
