from src.lib.bot import bot
import src.settings as settings

for cog in settings.COGS:
    bot.load_extension("lib.cogs.{cog}")

bot.run()
