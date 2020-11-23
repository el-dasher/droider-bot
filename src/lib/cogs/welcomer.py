from discord.ext.commands import Cog
import discord
from src.lib.utils.basic_utils import ready_up_cog, get_member_name


class Welcomer(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        join_embed = discord.Embed(
            title="MEMBRO NOVO POG",
            description=f"Um novo <@{member.id}> entrou no server"
        )
        join_embed.set_image(url=member.avatar_url)

        await self.bot.stdout.send(embed=join_embed)

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot.stdout.send(f"Que pena, o {get_member_name(member)} saiu do servidor, compreensivel apenas...")


def setup(bot):
    bot.add_cog(Welcomer(bot))
