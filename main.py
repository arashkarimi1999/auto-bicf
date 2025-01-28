from os import getenv
from dotenv import load_dotenv

load_dotenv()

from bot.handlers import setup_handlers


if __name__ == "__main__":
    setup_handlers(bot_token=getenv("BOT_TOKEN"))

