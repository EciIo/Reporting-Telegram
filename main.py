import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

CHANNEL, CATEGORY, REASON = range(3)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 BOT REPORT SALURAN PALSU\n\n"
        "Kirim username atau link saluran yang ingin dilaporkan."
    )
    return CHANNEL


# ================= STEP 1 =================
async def get_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["channel"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("👤 Menyamar Tokoh Terkenal", callback_data="tokoh")],
        [InlineKeyboardButton("🏢 Menyamar Organisasi Resmi", callback_data="organisasi")],
        [InlineKeyboardButton("🏷 Menyamar Brand Bermerek", callback_data="brand")],
        [InlineKeyboardButton("💰 Penipuan / Scam", callback_data="scam")],
    ]

    await update.message.reply_text(
        "Pilih kategori laporan:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return CATEGORY


# ================= STEP 2 =================
async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["category"] = query.data

    await query.edit_message_text(
        "Masukkan detail tambahan (opsional)\n"
        "Contoh: Menggunakan logo resmi tanpa izin"
    )

    return REASON


# ================= STEP 3 =================
async def get_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = context.user_data["channel"]
    category = context.user_data["category"]
    reason = update.message.text

    if category == "tokoh":
        template = f"""
🚨 OFFICIAL REPORT – IMPERSONATION

Channel: {channel}

This channel is falsely impersonating a well-known public figure.
They are using identity elements to mislead users.

Additional Info:
{reason}

This violates Telegram policies regarding impersonation.
Immediate investigation is requested.
"""

    elif category == "organisasi":
        template = f"""
🚨 OFFICIAL REPORT – ORGANIZATION IMPERSONATION

Channel: {channel}

This channel is illegally impersonating an official organization.
They are misleading users by copying identity elements.

Additional Info:
{reason}

This is a violation of Telegram anti-impersonation policy.
Please review and take action immediately.
"""

    elif category == "brand":
        template = f"""
🚨 OFFICIAL REPORT – BRAND IMPERSONATION

Channel: {channel}

This channel is falsely representing a registered brand.
Unauthorized use of brand identity may cause fraud and public harm.

Additional Info:
{reason}

This violates Telegram rules regarding fraud and impersonation.
Immediate suspension is requested.
"""

    else:  # scam
        template = f"""
🚨 OFFICIAL REPORT – SCAM / FRAUD

Channel: {channel}

This channel is involved in fraudulent activities and deception.

Additional Info:
{reason}

This violates Telegram policies regarding scam and financial fraud.
Please investigate urgently.
"""

    keyboard = [
        [InlineKeyboardButton("📩 Lapor ke @notoscam", url="https://t.me/notoscam")]
    ]

    await update.message.reply_text(
        f"✅ Format laporan siap dikirim:\n\n{template}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.END


# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_channel)],
            CATEGORY: [CallbackQueryHandler(get_category)],
            REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_reason)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)

    print("Bot berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
