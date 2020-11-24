# This thing isn't working i will fix it later
from discord.ext import commands
import src.settings as settings
from src.lib.utils.basic_utils import ready_up_cog


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.Cog.listener()
    async def on_error(self):
        # if error == "on_command_error":
        #   pass
        await self.bot.stdout.send(
            f"Algo de errado, não está certo, talvez você tente falar com o"
            f" <@{settings.MSCOY['user_id']}>, e ver o que ele pode fazer"
        )
        print("Algo de errado não esta certo")
        raise

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
