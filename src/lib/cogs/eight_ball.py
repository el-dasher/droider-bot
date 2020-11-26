from src.lib.utils.basic_utils import ready_up_cog
from discord.ext import commands
import json
from random import choice
from paths import LUCKY_PATH

json_path = LUCKY_PATH


class EightBall(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.f = json.load(open(json_path, encoding="utf-8"))

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command(aliases=("8ball", "sorte"))
    async def lucky(self, ctx, question=None):
        if question is None:
            await ctx.send("Aprende a usar o bot, BURRO, cadê a pergunta?")
        else:
            lucky_response = choice(list(choice(list(choice((list(self.f.values()))).values()))))
            await ctx.send(lucky_response)


def setup(bot):
    bot.add_cog(EightBall(bot))
