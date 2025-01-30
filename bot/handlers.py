from datetime import time
from telegram.ext import ContextTypes
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    filters,
    MessageHandler,
    CommandHandler,
    ApplicationBuilder,
    ConversationHandler
)

from bot.logger import logger


GET_NAME, GET_EMAIL, GET_CODICE, GET_HOUR, GET_TIME_SLOT = range(5)

def generate_time_slots(hours: int):
    """
    Generate time slots starting from 9:00 AM,
    shifting by 30 minutes until the end time reaches 23:00.

    Args:
        hours (int): The number of hours to reserve.

    Returns:
        list: A list of dictionaries containing start and end times.
    """
    time_slots = []
    start_time = time(hour=9, minute=0)
    end_time = time(hour=start_time.hour + hours, minute=start_time.minute)

    while end_time <= time(hour=23, minute=0):
        time_slots.append({
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M")
        })

        if start_time.minute == 30:
            start_time = time(start_time.hour + 1, start_time.minute - 30)
        else:
            start_time = time(start_time.hour, start_time.minute + 30)
        end_time = time(start_time.hour + hours, start_time.minute)

    return time_slots

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start the bot and send a welcome message to the user.
    """
    await update.message.reply_text(
        "Hello there!\nI can help you to book appointments for the next "
        "working day in the BICF library.\n"
        "Use /help to see the list of commands."
    )

async def create_reserve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiate the reservation process.
    If user data isn't already stored, request the user's details.
    """
    if context.user_data:
        await update.message.reply_text(
            "Enter the number of hours you want to reserve.\n"
            "(Only numeric values are allowed, minimum=1, maximum=14)."
        )
        return GET_HOUR
    else:
        await update.message.reply_text(
            "To book an appointment, the website requires your first name, "
            "last name, email, and codice fiscale.\n\n"
            "This data will be stored so you don't have to enter it again "
            "in the future. You can update this information at any time using "
            "the /change_data command.\n\n"
            "Please enter your first name and last name:"
        )
        return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store the user's name.
    """
    context.user_data["name"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Now enter the email address where you want to receive the "
        "appointment code:"
    )
    return GET_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store the user's email.
    """
    context.user_data["email"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Now enter your codice fiscale:"
    )
    return GET_CODICE

async def get_codice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store the user's codice fiscale and chat_id.
    """
    context.user_data["codice"] = update.message.text.strip()
    context.user_data["chat_id"] = update.message.chat_id
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Thank you.\nNow enter the number of hours you want to reserve.\n"
        "(Only numeric values are allowed, minimum=1, maximum=14)."
    )
    return GET_HOUR

async def get_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store the number of hours requested by the user.
    """
    try:
        hours = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a numeric value.")
        return GET_HOUR

    if 1 <= hours <= 14:
        context.user_data["request"] = {"hour": hours}

        time_slots = generate_time_slots(hours)
        context.user_data["request"]["time_slots"] = time_slots

        keyboard = [[f"{slot['start']} - {slot['end']}"] for slot in time_slots]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "Please select a time slot:",
            reply_markup=reply_markup
        )
        return GET_TIME_SLOT
    else:
        await update.message.reply_text("Please enter a number between 1 and 14.")
        return GET_HOUR

async def get_time_slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store the selected time slot and confirm the reservation.
    """
    selected_slot = update.message.text.strip()
    time_slots = context.user_data["request"]["time_slots"]

    for slot in time_slots:
        if f"{slot['start']} - {slot['end']}" == selected_slot:
            context.user_data["request"]["time_slot"] = slot
            await update.message.reply_text(
                f"Your reservation is confirmed for {slot['start']} - {slot['end']}."
            )
            return ConversationHandler.END

    await update.message.reply_text("Invalid selection. Please try again.")
    return GET_TIME_SLOT

def setup_handlers(bot_token: str):
    """
    Set up the bot's handlers and starts pulling.

    Args:
        bot_token (str): The bot's API token.

    Returns:
        None
    """
    logger.info("Starting the bot...")
    
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('create_reserve', create_reserve)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            GET_CODICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_codice)],
            GET_HOUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hour)],
            GET_TIME_SLOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time_slot)],
        },
        fallbacks=[]
    ))

    logger.info("Bot is polling for updates...")
    app.run_polling()
    logger.info("Bot has stopped.")
