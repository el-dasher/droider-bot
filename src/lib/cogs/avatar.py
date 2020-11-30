from discord.ext import commands
import discord
from src.lib.utils.basic_utils import ready_up_cog, get_member_name
from random import choice
from datetime import datetime


class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def avatar(self, ctx: discord.ext.commands.Context, member: discord.Member = None):

        if member is not None:
            ava_desc = choice(("Aproveita e me paga um café", f"Avatar bonito o do <@{member.id}> né mano?"))
        else:
            ava_desc = choice(("Toma aqui o seu avatar", "O teu avatar é muito lindo véi"))
            member = ctx.message.author

        member_name = get_member_name(member)

        avatar_embed = discord.Embed(
            title=f"Avatar do {member_name}",
            description=f"{ava_desc} [Link]({member.avatar_url})",
            timestamp=datetime.utcnow()
        )

        avatar_embed.set_image(url=member.avatar_url)
        avatar_embed.set_footer(text=get_member_name(self.bot.bot_user), icon_url=self.bot.bot_user.avatar_url)

        await ctx.reply(embed=avatar_embed)


def setup(bot):
    bot.add_cog(Avatar(bot))
