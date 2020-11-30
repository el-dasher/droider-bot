from src.lib.utils.basic_utils import ready_up_cog
from discord.ext import commands
import discord
from random import choice
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.lib.db.data.json.pydict.pydata import bot_presences


class Funny(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    @commands.Cog.listener()
    async def on_ready(self):
        self.scheduler.add_job(self.presences, CronTrigger(second=0))
        self.scheduler.start()

        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def owo(self, ctx):
        await ctx.reply("UwU")

    async def presences(self):
        await self.bot.change_presence(activity=(choice(bot_presences)))

    @commands.command()
    async def ping(self, ctx):
        await ctx.reply(f"Pingo, tô levando {self.bot.latency:.3f} milissegundos pra responder!")


def setup(bot):
    bot.add_cog(Funny(bot))
