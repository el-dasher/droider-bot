# SE VOCÊ FOR RODAR O PROJETO LOCALMENTE ATRIBUA O VALOR DE "local" PARA "True"

from pathlib import Path

local = False  # local = True SE VOCÊ FOR RODAR O PROJETO LOCALMENTE!!!

if local:
    COGS_PATH = Path('./lib/cogs').absolute()

    DB_PATH = Path("./lib/db/data/db/database.db").absolute()
    BUILD_PATH = Path("./lib/db/data/db/build.sql").absolute()

    LUCKY_PATH = Path("./lib/db/data/json/lucky_responses.json").absolute()
    MONTHS_PATH = Path("./lib/db/data/json/months.json").absolute()
else:
    COGS_PATH = Path('./src/lib/cogs').absolute()

    DB_PATH = Path("./src/lib/db/data/db/database.db").absolute()
    BUILD_PATH = Path("./src/lib/db/data/db/build.sql").absolute()

    LUCKY_PATH = Path("./src/lib/db/data/json/lucky_responses.json").absolute()
    MONTHS_PATH = Path("./src/lib/db/data/json/months.json").absolute()
