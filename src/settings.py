from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging
import json
import traceback

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = getenv("BOT_TOKEN")
PREFIX = getenv("PREFIX")

# noinspection PyBroadException
try:
    f = open("./lib/db/data/json/useful_data.json")
    data = json.load(f)
    f.close()

    # Useful data
    MAIN_GUILD = data["guilds"]["main_guild"]
    BR_GUILD = data["guilds"]["br_guild"]

    USERS = data["users"]
    PRIVILEGED = USERS["privileged"]

    BOT_USER = USERS["bot_user"]
    MSCOY = PRIVILEGED["bot_owners"]["mscoy"]
    ZALUR = PRIVILEGED["guild_owners"]["zalur"]

except Exception:
    print(traceback.print_exc())


logging.basicConfig(level=logging.INFO)
