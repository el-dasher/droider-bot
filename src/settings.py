from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging
from discord.ext.commands import Bot


env_path = Path('') / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = getenv("BOT_TOKEN")
PREFIX = getenv("PREFIX")
bot = Bot(command_prefix=PREFIX)

logging.basicConfig(level=logging.INFO)
