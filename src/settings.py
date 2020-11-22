from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging
import json

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = getenv("BOT_TOKEN")
PREFIX = getenv("PREFIX")
OWNERS_ID = [750129701129027594]

f = open("./lib/db/data/json/useful_data.json")
data = json.load(f)
f.close()

# Useful data
MAIN_GUILD = data["guilds"]["main_guild"]
BR_GUILD = data["guilds"]["br_guild"]
BOT_USER = data["users"]["bot_user"]
MSCOY = data["users"]["mscoy"]

logging.basicConfig(level=logging.INFO)
