from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging
from github import Github
from src.paths import COGS_PATH

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)


COGS = []

for path in COGS_PATH.glob('*.py'):
    COGS.append(path.name[:-3])

DASHERGIT = Github(getenv("ACCESS_TOKEN"))
BOT_TOKEN = getenv("BOT_TOKEN")
PREFIX = getenv("PREFIX")


logging.basicConfig(level=logging.INFO)
