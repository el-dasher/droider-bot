from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging
from github import Github
from src.paths import COGS_PATH
from src.lib.db.data.db.firebase_db import database as firebase
from pyrebase.pyrebase import Database
from pygelbooru import Gelbooru

env_path: any = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

COGS: list = []

for path in COGS_PATH.glob('*.py'):
    COGS.append(path.name[:-3])

DATABASE: Database = firebase

GELBOORU_API: Gelbooru = Gelbooru(getenv("GELBOORU_API"), "693051")
DASHERGIT: Github = Github(getenv("ACCESS_TOKEN"))
BOT_TOKEN: str = getenv("BOT_TOKEN")
PREFIX: str = getenv("PREFIX")
DPPBOARD_API = getenv("DPP_BOARD_API")

GOOGLE_USEFULS: dict = {
    "id": getenv("SEARCH_ENGINE_ID"),
    "api_key": getenv("SEARCH_ENGINE_API_KEY")
}

logging.basicConfig(level=logging.INFO)
