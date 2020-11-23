from src.lib.utils.basic_utils import ready_up_cog
from discord.ext import commands


class Funny(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def owo(self, ctx):
        await ctx.send("UwU")


def setup(bot):
    bot.add_cog(Funny(bot))
