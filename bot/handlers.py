from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import ApplicationBuilder, CommandHandler

from bot.logger import logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot."""
    await update.message.reply_text(
        '''Hello there!\n'''
        '''I can help you to get appointments for the next working day in the BICF library.'''
        '''use /help to see the list of commands.'''
    )

def setup_handlers(bot_token: str):
    logger.info("Starting the bot...")
    
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))

    logger.info("Bot is polling for updates...")
    app.run_polling()
    logger.info("Bot has stopped.")
