from datetime import datetime
from random import choice
from typing import Union

import discord
from discord.ext import commands

from src.lib.utils.basic_utils import ready_up_cog, get_member_name


class Avatar(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def avatar(self, ctx: discord.ext.commands.Context, member: discord.Member = None):

        if member is not None:
            ava_desc: str = choice(("Aproveita e me paga um café", f"Avatar bonito o do <@{member.id}> né mano?"))
        else:
            ava_desc: str = choice(("Toma aqui o seu avatar", "O teu avatar é muito lindo véi"))
            member: Union[discord.Member, discord.User] = ctx.message.author

        member_name: str = get_member_name(member)

        avatar_embed: discord.Embed = discord.Embed(
            title=f"Avatar do(a) {member_name}",
            description=f"{ava_desc} [Link]({member.avatar_url})",
            timestamp=datetime.utcnow()
        )

        avatar_embed.set_image(url=member.avatar_url)
        avatar_embed.set_footer(text=get_member_name(self.bot.user), icon_url=self.bot.user.avatar_url)

        await ctx.reply(f"<@{ctx.author.id}>", embed=avatar_embed)


def setup(bot):
    bot.add_cog(Avatar(bot))
