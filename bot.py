import os
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

# Estados de la conversación
PHOTO, AMOUNT, NUMBER = range(3)

# Expresión regular para CUIT u otra validación
REGEX = r"^\d{2}-\d{8}-\d{1}$"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Buen día! Enviame una foto del ticket")
    return PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    context.user_data["photo_file_id"] = file.file_id
    await update.message.reply_text("💰 Ingresá su importe (ej: 1234.56)")
    return AMOUNT

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(",", "."))
        context.user_data["amount"] = amount
        await update.message.reply_text("🔢 Ingresá el cuil del negocio (XX-XXXXXXXX-X)")
        return NUMBER
    except ValueError:
        await update.message.reply_text("❌ Ese importe no es válido. Probá de nuevo.")
        return AMOUNT

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text
    if re.match(REGEX, number):
        context.user_data["number"] = number
        await update.message.reply_photo(
            photo=context.user_data["photo_file_id"],
            caption=f"✅ Datos:\n💰 Importe: {context.user_data['amount']}\n🔢 Número: {number}"
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ El número no cumple el formato. Probá de nuevo.")
        return NUMBER

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelado.")
    return ConversationHandler.END

def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise Exception("No se encontró la variable BOT_TOKEN")

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

if __name__ == "__main__":
    main()
