import re
import logging
from telegram import Update, ForceReply
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Estados del flujo
PHOTO, AMOUNT, NUMBER = range(3)

# Logging
logging.basicConfig(level=logging.INFO)

# Expresión regular para validar número (e.g., CUIT)
REGEX = r"^\d{2}-\d{8}-\d{1}$"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enviame una foto 📸")
    return PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    context.user_data["photo_file_id"] = file.file_id
    await update.message.reply_text("Ahora ingresá un importe (ej: 1234.56) 💰")
    return AMOUNT

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(",", "."))
        context.user_data["amount"] = amount
        await update.message.reply_text("Ahora ingresá un número con formato XX-XXXXXXXX-X 🔢")
        return NUMBER
    except ValueError:
        await update.message.reply_text("Eso no parece un número válido. Intentá de nuevo.")
        return AMOUNT

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text
    if re.match(REGEX, number):
        context.user_data["number"] = number
        await update.message.reply_text("✅ ¡Datos recibidos!")
        # Mostrar todo junto
        await update.message.reply_photo(
            photo=context.user_data["photo_file_id"],
            caption=f"💰 Importe: {context.user_data['amount']}\n🔢 Número: {context.user_data['number']}"
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ El número no coincide con el formato requerido.")
        return NUMBER

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada ❌")
    return ConversationHandler.END

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("BOT_TOKEN")  # guardá tu token como variable de entorno

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount)],
            NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
