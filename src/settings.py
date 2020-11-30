from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging
from github import Github
from src.paths import COGS_PATH

env_path: any = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)


COGS: list = []

for path in COGS_PATH.glob('*.py'):
    COGS.append(path.name[:-3])

DASHERGIT: Github = Github(getenv("ACCESS_TOKEN"))
BOT_TOKEN: str = getenv("BOT_TOKEN")
PREFIX: str = getenv("PREFIX")


logging.basicConfig(level=logging.INFO)
