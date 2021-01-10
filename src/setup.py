import logging
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from github import Github
from ossapi import ossapi
from pygelbooru import Gelbooru
from pyrebase.pyrebase import Database

from src.lib.db.firebase.firebase_db import database as firebase
from src.paths import COGS_PATH
from src.paths import debug

env_path: any = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

COGS: list = []

for path in COGS_PATH.glob('*.py'):
    COGS.append(path.name[:-3])

DATABASE: Database = firebase

OSU_API = ossapi((OSU_API_KEY := getenv("OSU_API")))
GELBOORU_API: Gelbooru = Gelbooru(getenv("GELBOORU_API"), "693051")
if not debug:
    DASHERGIT: Github = Github(getenv("ACCESS_TOKEN"))
    # PREFIX: str = getenv("PREFIX")
    PREFIX: list = ["a!", "&", "ms!"]
else:
    PREFIX: list = ["d!", "m!"]
DPPBOARD_API = getenv("DPP_BOARD_API")
BOT_TOKEN: str = getenv("BOT_TOKEN")

GOOGLE_USEFULS: dict = {
    "id": getenv("SEARCH_ENGINE_ID"),
    "api_key": getenv("SEARCH_ENGINE_API_KEY")
}

logging.basicConfig(level=logging.INFO)
