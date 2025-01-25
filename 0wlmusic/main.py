import discord
from discord.ext import commands
import asyncio
import os
import logging
from discord import Activity, ActivityType
from dotenv import load_dotenv
import signal

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

ACTIVITY_NAME = "!help"
activity = Activity(name=ACTIVITY_NAME, type=ActivityType.listening)
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True  # message_content is enabled by default
COMMAND_PREFIX = '!'
bot = commands.Bot(command_prefix=COMMAND_PREFIX, activity=activity, intents=intents)
token = os.getenv("BOT_TOKEN")
if not token:
    logger.error("No token provided. Please set the BOT_TOKEN environment variable.")
    raise ValueError("No token provided. Please set the BOT_TOKEN environment variable.")

@bot.event
async def on_ready():
    """
    Event handler for when the bot has successfully connected to Discord.
    """
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("------")

    # Load all extensions from the 'owlmusic' directory.
    bot.remove_command('help')
    for entry in os.scandir("./owlmusic"):
        if entry.name.endswith(".py") and entry.is_file():
            try:
                await bot.load_extension(f"owlmusic.{entry.name[:-3]}")
                logger.info(f"Loaded extension: {entry.name}")
            except Exception as e:
                logger.error(f"Failed to load extension {entry.name}: {e}")

async def start_bot():
    """
    Starts the bot.
    """
    try:
        await bot.start(token)
    except Exception as e:
        logger.critical(f"An error occurred while starting the bot: {e}")
        await shutdown_handler()

async def shutdown_handler():
    """
    Handles the shutdown of the bot.
    """
    logger.info("Shutting down the bot...")
    await bot.close()

def main():
    loop = asyncio.get_event_loop()

    try:
        if os.name != 'nt':
            loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown_handler()))
            loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown_handler()))
        loop.run_until_complete(start_bot())
    except Exception as e:
        logger.critical(f"An error occurred while running the bot: {e}")
    finally:
        loop.run_until_complete(shutdown_handler())
        loop.close()

if __name__ == "__main__":
    main()
