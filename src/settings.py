from dotenv import load_dotenv
from pathlib import Path
from os import getenv
import logging
import json
from glob import glob
import sys

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

sys.exit(str(Path("src/lib/db/data/json/useful_data.json").absolute()).split(".")[:-1])
COGS = [path.split("\\")[-1][:-3] for path in glob("src/lib/cogs/*.py")]
BOT_TOKEN = getenv("BOT_TOKEN")
PREFIX = getenv("PREFIX")

# noinspection PyBroadException
f_path = Path("./src/lib/db/data/json/useful_data.json").absolute()
print(f_path)
try:
    f = open(f_path)
except FileNotFoundError as exc:
    f = None
    raise Exception(f"Não foi possivel encontrar o diretório {f_path}",
                    f"\n{exc}")

if f is None:

    sys.exit("Como o arquivo não pôde ser encontrado o processo foi encerrado")
# noinspection PyBroadException
try:
    data = json.load(f)
except Exception:
    print("O arquivo foi corrompido e eu se dei ao máximo pra que o arquivo seja recuperado")
finally:
    f.close()

# Useful data
# noinspection PyBroadException
try:
    # noinspection PyUnboundLocalVariable
    if data:
        # noinspection PyUnboundLocalVariable
        MAIN_GUILD = data["guilds"]["main_guild"]
        BR_GUILD = data["guilds"]["br_guild"]

        USERS = data["users"]
        PRIVILEGED = USERS["privileged"]

        MSCOY = PRIVILEGED["bot_owners"]["mscoy"]
        ZALUR = PRIVILEGED["guild_owners"]["zalur"]
    else:
        print('O BOT NÃO CONSEGUIU RECUPERAR O "useful_data.json"')
except Exception:
    print("Ocorreu um erro mas o bot fez de tudo pra recuperar o JSON novamente, então deve estar tudo ok!")

logging.basicConfig(level=logging.INFO)
