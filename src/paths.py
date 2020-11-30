# SE VOCÊ FOR RODAR O PROJETO LOCALMENTE ATRIBUA O VALOR DE "local" PARA "True"

from pathlib import Path

local = True  # local = True SE VOCÊ FOR RODAR O PROJETO LOCALMENTE!!!

if local:
    COGS_PATH = Path('./lib/cogs')

    LUCKY_PATH = Path("./lib/db/data/json/lucky_responses.json")
    MONTHS_PATH = Path("./lib/db/data/json/months.json")
else:
    COGS_PATH = Path('./src/lib/cogs')

    LUCKY_PATH = Path("./src/lib/db/data/json/lucky_responses.json")
    MONTHS_PATH = Path("./src/lib/db/data/json/months.json")
