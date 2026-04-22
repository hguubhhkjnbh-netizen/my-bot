from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

TOKEN = "8680039869:AAHwqVOJ7lIXKHV5tUfDnwrHkJTGeFv2R00"

# Database setup
conn = sqlite3.connect("gmute.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS muted (user_id INTEGER, chat_id INTEGER)")
conn.commit()

# Check admin
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
member = await context.bot.get_chat_member(
update.effective_chat.id,
update.effective_user.id
)
return member.status in ["administrator", "creator"]

# gmute command
async def gmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not await is_admin(update, context):
await update.message.reply_text("❌ Only admins can use this")
    return

if update.message.reply_to_message:
user_id = update.message.reply_to_message.from_user.id
chat_id = update.effective_chat.id

cursor.execute("INSERT INTO muted VALUES (?, ?)", (user_id, chat_id))
conn.commit()

await update.message.reply_text("✅ User muted")
else:
await update.message.reply_text("Reply to user")

# ungmute command
async def ungmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not await is_admin(update, context):
    await update.message.reply_text("❌ Only admins can use this")
    return

if update.message.reply_to_message:
user_id = update.message.reply_to_message.from_user.id
chat_id = update.effective_chat.id

cursor.execute("DELETE FROM muted WHERE user_id=? AND chat_id=?", (user_id, chat_id))
conn.commit()

await update.message.reply_text("✅ User unmuted")
else:
await update.message.reply_text("Reply to user")

# Delete muted messages
async def delete_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.message.from_user.id
chat_id = update.effective_chat.id

cursor.execute("SELECT * FROM muted WHERE user_id=? AND chat_id=?", (user_id, chat_id))
result = cursor.fetchone()

if result:
try:
await update.message.delete()
except:
pass

# Start bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("gmute", gmute))
app.add_handler(CommandHandler("ungmute", ungmute))
app.add_handler(MessageHandler(filters.ALL, delete_msg))

print("Bot running...")
app.run_polling()
