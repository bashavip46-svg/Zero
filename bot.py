from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================
TOKEN = "TOKEN"  # 🔴 غيره فورًا من BotFather
ADMIN_ID = 7991973291
DEVELOPER_URL = "https://t.me/V_L_7_D"

user_message_count = {}
blocked_users = set()
# ============================================


# ───────── /start ─────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = f"""
👋 أهلاً {user.first_name}

🤖 هذا بوت تواصل مع الإدارة

📨 أرسل رسالتك الآن
وسيتم تحويلها إلى الأدمن مباشرة

⏳ الرجاء الانتظار حتى يتم الرد
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 حساب المطوّر", url=DEVELOPER_URL)]
    ])

    await update.message.reply_text(
        text=text,
        reply_markup=keyboard
    )


# ───────── USER MESSAGE ─────────
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id in blocked_users:
        await update.message.reply_text("⛔ تم حظرك من التواصل مع الإدارة.")
        return

    user_message_count[user.id] = user_message_count.get(user.id, 0) + 1

    admin_text = f"""
📩 رسالة جديدة

👤 الاسم: {user.first_name}
🔗 اليوزر: @{user.username}
🆔 ID: {user.id}
📊 عدد الرسائل: {user_message_count[user.id]}

💬 الرسالة:
{update.message.text}
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ رد", callback_data=f"reply_{user.id}"),
            InlineKeyboardButton("⛔ حظر", callback_data=f"block_{user.id}")
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        reply_markup=keyboard
    )

    await update.message.reply_text(
        "✅ تم إرسال رسالتك إلى الإدارة، الرجاء الانتظار."
    )


# ───────── ADMIN REPLY ─────────
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        text = update.message.reply_to_message.text
        if "ID:" in text:
            try:
                user_id = int(text.split("ID:")[1].split("\n")[0])
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📬 رد الإدارة:\n\n{update.message.text}"
                )
            except:
                pass


# ───────── BUTTONS ─────────
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("block_"):
        user_id = int(data.split("_")[1])
        blocked_users.add(user_id)
        await query.edit_message_text("⛔ تم حظر المستخدم بنجاح.")

    elif data.startswith("reply_"):
        await query.edit_message_text("✉️ قم بالرد على هذه الرسالة مباشرة.")


# ───────── RUN BOT ─────────
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, admin_reply))
    app.add_handler(CallbackQueryHandler(buttons))

    print("🤖 Support Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
