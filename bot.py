# ============ HIDE TOKENS FROM LOGS (MUST BE FIRST) ============
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

# ============ IMPORTS ============
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

# ============ LOGGING ============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ CONFIG FROM ENV VARS ============
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Rebrand these in Railway Variables:
BOT_NAME       = os.getenv('BOT_NAME', 'My Bot')
CHANNEL_URL    = os.getenv('CHANNEL_URL', 'https://t.me/telegram')
CONTACT_URL    = os.getenv('CONTACT_URL', 'https://t.me/telegram')
WEBSITE_URL    = os.getenv('WEBSITE_URL', '')
OWNER_ID       = os.getenv('OWNER_ID', '')  # numeric Telegram ID

if not TELEGRAM_TOKEN:
    raise ValueError("❌ No TELEGRAM_BOT_TOKEN set in Railway Variables!")

# In-memory subscriber store
SUBSCRIBERS = set()


# ============ KEYBOARDS ============
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Latest Update", callback_data="latest")],
        [InlineKeyboardButton("🔔 Notifications", callback_data="notify")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")],
    ])


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")]
    ])


# ============ COMMANDS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome + main menu."""
    user = update.effective_user
    text = (
        f"👋 <b>Welcome to {BOT_NAME}</b>\n\n"
        f"Hi {user.first_name}! I keep you updated with the latest.\n\n"
        "Choose an option below 👇"
    )
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>📖 How to use this bot</b>\n\n"
        "/start – Show main menu\n"
        "/latest – Get the latest update\n"
        "/notify – Toggle notifications\n"
        "/about – About this bot\n"
        "/contact – Contact us\n"
        "/help – This message\n\n"
        "Every button on the menu works — just tap it!"
    )
    await update.message.reply_text(text, reply_markup=back_button(), parse_mode='HTML')


async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_latest(update, context)


async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_notify(update, context)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_about(update, context)


async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_contact(update, context)


# ============ SCREEN BUILDERS ============

async def send_latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>📢 Latest Update</b>\n\n"
        "Tap the button below to open the latest content:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Open Latest", url=CHANNEL_URL)],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")],
    ])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=kb, parse_mode='HTML')


async def send_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribed = user_id in SUBSCRIBERS

    status = "🔔 <b>Subscribed</b>" if subscribed else "🔕 <b>Not subscribed</b>"
    action_text = "🔕 Turn OFF notifications" if subscribed else "🔔 Turn ON notifications"
    action_data = "unsub" if subscribed else "sub"

    text = (
        f"<b>🔔 Notifications</b>\n\n"
        f"Status: {status}\n\n"
        "When enabled, you'll be notified whenever there's something new.\n"
        "You can unsubscribe at any time."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(action_text, callback_data=action_data)],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")],
    ])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=kb, parse_mode='HTML')


async def send_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"<b>ℹ️ About {BOT_NAME}</b>\n\n"
        "This bot keeps you updated with the latest content and news.\n\n"
        "<b>Features:</b>\n"
        "• 📢 Latest updates — one tap to open\n"
        "• 🔔 Optional notifications\n"
        "• 📞 Direct contact\n"
        "• 100% free, no spam\n\n"
        "Made with ❤️ for our community."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Open Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")],
    ])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=kb, parse_mode='HTML')


async def send_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>📞 Contact Us</b>\n\n"
        "We'd love to hear from you!\n\n"
        "Tap below to reach out directly:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Message Us", url=CONTACT_URL)],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")],
    ])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=kb, parse_mode='HTML')


# ============ BUTTON ROUTER ============

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        user = update.effective_user
        text = (
            f"👋 <b>Welcome to {BOT_NAME}</b>\n\n"
            f"Hi {user.first_name}! Choose an option below 👇"
        )
        await query.edit_message_text(text, reply_markup=main_menu(), parse_mode='HTML')
    elif data == "latest":
        await send_latest(update, context)
    elif data == "notify":
        await send_notify(update, context)
    elif data == "about":
        await send_about(update, context)
    elif data == "contact":
        await send_contact(update, context)
    elif data == "sub":
        SUBSCRIBERS.add(update.effective_user.id)
        await send_notify(update, context)
    elif data == "unsub":
        SUBSCRIBERS.discard(update.effective_user.id)
        await send_notify(update, context)


# ============ FALLBACK FOR PLAIN TEXT ============

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 I don't understand that message.\n\n"
        "Please use the menu below 👇"
    )
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode='HTML')


# ============ OWNER BROADCAST ============

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner-only: /broadcast your message"""
    if OWNER_ID and str(update.effective_user.id) != str(OWNER_ID):
        await update.message.reply_text("⛔ Not authorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast your message here")
        return

    msg = " ".join(context.args)
    sent, failed = 0, 0

    for uid in list(SUBSCRIBERS):
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 <b>New Update!</b>\n\n{msg}",
                parse_mode='HTML'
            )
            sent += 1
        except Exception:
            failed += 1
            SUBSCRIBERS.discard(uid)

    await update.message.reply_text(
        f"✅ Sent: {sent}\n❌ Failed: {failed}\n👥 Total subscribers: {len(SUBSCRIBERS)}"
    )


# ============ STATS (OWNER) ============

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID and str(update.effective_user.id) != str(OWNER_ID):
        await update.message.reply_text("⛔ Not authorized.")
        return
    await update.message.reply_text(
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👥 Subscribers: <b>{len(SUBSCRIBERS)}</b>\n"
        f"🤖 Status: Running\n"
        f"⚡ Platform: Railway",
        parse_mode='HTML'
    )


# ============ ERROR HANDLER ============

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try /start again."
            )
    except Exception:
        pass


# ============ MAIN ============

def main():
    print(f"🚀 Starting {BOT_NAME}...")
    print(f"📢 Channel: {CHANNEL_URL}")
    print(f"📞 Contact: {CONTACT_URL}")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("latest", latest_command))
    application.add_handler(CommandHandler("notify", notify_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats))

    # Buttons
    application.add_handler(CallbackQueryHandler(on_button))

    # Fallback for any plain text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Errors
    application.add_error_handler(error_handler)

    print(f"🤖 {BOT_NAME} is running!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()
