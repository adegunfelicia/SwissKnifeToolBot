import os
import sys
import logging
import random
import string
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.critical("ERROR: TELEGRAM_BOT_TOKEN environment variable is missing!")
    sys.exit(1)

# Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🤖 **SwissKnifeToolBot is Online!**\n\n"
        "/upper <text>\n/lower <text>\n/reverse <text>\n/password <len>\n/calc <expr>"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def upper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    await update.message.reply_text(text.upper() if text else "❌ Provide text.")

async def lower_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    await update.message.reply_text(text.lower() if text else "❌ Provide text.")

async def reverse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    await update.message.reply_text(text[::-1] if text else "❌ Provide text.")

async def password_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        length = int(context.args[0]) if context.args else 12
    except ValueError:
        await update.message.reply_text("❌ Length must be an integer.")
        return
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    res = "".join(random.choice(chars) for _ in range(max(6, min(length, 64))))
    await update.message.reply_text(f"🔑 Password: `{res}`", parse_mode="Markdown")

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expression = "".join(context.args)
    if not expression or not set(expression).issubset(set("0123456789+-*/(). ")):
        await update.message.reply_text("❌ Missing or invalid expression.")
        return
    try:
        await update.message.reply_text(f"🧮 Result: `{eval(expression, {'__builtins__': None}, {})}`", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Syntax error.")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔄 **Echo:** {update.message.text}", parse_mode="Markdown")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Error occurred:", exc_info=context.error)

async def main():
    logger.info("Building application...")
    # Built-in pooling applications require precise handling on Python 3.14+
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("upper", upper_command))
    app.add_handler(CommandHandler("lower", lower_command))
    app.add_handler(CommandHandler("reverse", reverse_command))
    app.add_handler(CommandHandler("password", password_command))
    app.add_handler(CommandHandler("calc", calc_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    app.add_error_handler(error_handler)

    # Use python-telegram-bot's standard context manager to safely structure the runner loop
    async with app:
        logger.info("Starting polling...")
        await app.updater.start_polling(drop_pending_updates=True)
        await app.start()
        logger.info("Bot is fully operational.")
        
        # Keep the main process alive peacefully
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    # Clean loop initialization for modern container environments
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot execution terminated.")
