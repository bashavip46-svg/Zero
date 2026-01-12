import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")  # 🔐 التوكن من Environment Variables
ADMIN_ID = 7991973291
DEVELOPER_URL = "https://t.me/V_L_7_D"
# ==========================================

# تخزين مؤقت (يشتغل ممتاز مع Render)
user_message_count = {}
blocked_users = set()
pending_replies = {}

# ───────── START ─────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = f"""
👋 أهلاً {user.first_name}

🤖 بوت تواصل احترافي مع الإدارة

📨 أرسل رسالتك الآن
وسيتم إيصالها مباشرة للإدارة

⏳ الرجاء الانتظار حتى يتم الرد
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 حساب المطوّر", url=DEVELOPER_URL)]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)

# ───────── USER MESSAGE ─────────
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id in blocked_users:
        await update.message.reply_text("⛔ تم حظرك من التواصل مع الإدارة.")
        return

    user_message_count[user.id] = user_message_count.get(user.id, 0) + 1

    admin_text = (
        "📩 رسالة جديدة\n\n"
        f"👤 الاسم: {user.full_name}\n"
        f"🔗 اليوزر: @{user.username if user.username else 'بدون'}\n"
        f"🆔 ID: {user.id}\n"
        f"📊 عدد الرسائل: {user_message_count[user.id]}\n\n"
        f"💬 الرسالة:\n{update.message.text}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ رد", callback_data=f"reply:{user.id}"),
            InlineKeyboardButton("⛔ حظر", callback_data=f"block:{user.id}")
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        reply_markup=keyboard
    )

    await update.message.reply_text(
        "✅ تم إرسال رسالتك للإدارة، الرجاء الانتظار."
    )

# ───────── BUTTON HANDLER ─────────
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("block:"):
        user_id = int(data.split(":")[1])
        blocked_users.add(user_id)
        await query.edit_message_text("⛔ تم حظر المستخدم بنجاح.")

    elif data.startswith("reply:"):
        user_id = int(data.split(":")[1])
        pending_replies[ADMIN_ID] = user_id
        await query.edit_message_text(
            "✉️ أرسل الآن رسالة الرد، وسيتم إرسالها للمستخدم مباشرة."
        )

# ───────── ADMIN REPLY ─────────
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if ADMIN_ID not in pending_replies:
        return

    user_id = pending_replies.pop(ADMIN_ID)

    await context.bot.send_message(
        chat_id=user_id,
        text=f"📬 رد الإدارة:\n\n{update.message.text}"
    )

    await update.message.reply_text("✅ تم إرسال الرد بنجاح.")

# ───────── RUN ─────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), admin_reply))

    print("🤖 PRO Support Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
