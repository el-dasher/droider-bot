# This thing isn't working i will fix it later
from discord.ext import commands
from src.lib.utils.basic_utils import ready_up_cog


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.CommandNotFound):
            await ctx.send("Esse comando não existe..., cê ta bem mano?")
        elif hasattr(exc, "original"):
            raise exc.original
        else:
            raise exc


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
