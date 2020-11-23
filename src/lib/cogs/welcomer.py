from discord.ext.commands import Cog
import discord


class Welcomer(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.stdout.send(f"Seja bem vindo ao inferno, <@{member.id}>")


def setup(bot):
    bot.add_cog(Welcomer(bot))
