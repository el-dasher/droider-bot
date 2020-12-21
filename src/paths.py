# SE VOCÊ FOR RODAR O PROJETO LOCALMENTE ATRIBUA O VALOR DE "debug" PARA "True"

from pathlib import Path

debug = False  # debug = True SE VOCÊ FOR RODAR O PROJETO LOCALMENTE!!!

if debug:
    print("O BOT ESTÁ RODANDO LOCALMENTE")

    COGS_PATH = Path('./lib/cogs')

    FIREBASE_CONFIG_PATH = Path("./lib/db/json/firebase_config.json")
    RECENT_OSU_FILE_PATH = Path("./lib/db/osu_files/recent.osu")
    WEIRD_TAGS_RESPONSE_PATH = Path("./lib/db/json/weird_tags_response.json")
    LUCKY_PATH = Path("./lib/db/json/lucky_responses.json")
    MONTHS_PATH = Path("./lib/db/json/months.json")
else:
    print('O BOT ESTÁ RODANDO EM "PRODUÇÃO')

    COGS_PATH = Path('./src/lib/cogs')

    FIREBASE_CONFIG_PATH = None
    RECENT_OSU_FILE_PATH = Path("./src/lib/db/osu_files/recent.osu")
    WEIRD_TAGS_RESPONSE_PATH = Path("./src/lib/db/json/weird_tags_response.json")
    LUCKY_PATH = Path("./src/lib/db/json/lucky_responses.json")
    MONTHS_PATH = Path("./src/lib/db/json/months.json")
