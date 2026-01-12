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
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7991973291
DEVELOPER_URL = "https://t.me/V_L_7_D"
# =========================================

blocked_users = set()
user_stats = {}
reply_mode = {}

# ───────── START ─────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id == ADMIN_ID:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")]
        ])
        await update.message.reply_text(
            "👑 مرحبًا أيها الأدمن\n\nلوحة التحكم جاهزة.",
            reply_markup=keyboard
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 حساب المطوّر", url=DEVELOPER_URL)]
    ])

    await update.message.reply_text(
        "🤖 بوت تواصل مع الإدارة\n\n📨 أرسل رسالتك الآن.",
        reply_markup=keyboard
    )

# ───────── USER MESSAGE ─────────
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id in blocked_users:
        await update.message.reply_text("⛔ أنت محظور من التواصل.")
        return

    user_stats[user.id] = user_stats.get(user.id, 0) + 1

    text = (
        "📩 رسالة جديدة\n\n"
        f"👤 الاسم: {user.full_name}\n"
        f"🔗 اليوزر: @{user.username}\n"
        f"🆔 ID: {user.id}\n"
        f"📊 عدد الرسائل: {user_stats[user.id]}\n\n"
        f"💬 {update.message.text}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ رد", callback_data=f"reply:{user.id}"),
            InlineKeyboardButton("⛔ حظر", callback_data=f"block:{user.id}")
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ تم إرسال رسالتك للإدارة.")

# ───────── BUTTONS ─────────
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "stats":
        await query.edit_message_text(
            f"📊 الإحصائيات\n\n"
            f"👥 المستخدمين: {len(user_stats)}\n"
            f"🚫 المحظورين: {len(blocked_users)}"
        )

    elif data.startswith("block:"):
        uid = int(data.split(":")[1])
        blocked_users.add(uid)
        await query.edit_message_text("⛔ تم حظر المستخدم.")

    elif data.startswith("reply:"):
        uid = int(data.split(":")[1])
        reply_mode[ADMIN_ID] = uid
        await query.edit_message_text("✉️ أرسل الرد الآن.")

# ───────── ADMIN REPLY ─────────
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if ADMIN_ID not in reply_mode:
        return

    uid = reply_mode.pop(ADMIN_ID)

    await context.bot.send_message(
        chat_id=uid,
        text=f"📬 رد الإدارة:\n\n{update.message.text}"
    )

    await update.message.reply_text("✅ تم إرسال الرد.")

# ───────── RUN ─────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), admin_reply))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
