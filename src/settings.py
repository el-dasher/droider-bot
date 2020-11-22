from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging


env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = getenv("BOT_TOKEN")
PREFIX = getenv("PREFIX")
OWNERS_ID = [750129701129027594]

logging.basicConfig(level=logging.INFO)
