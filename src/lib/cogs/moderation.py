from typing import Union

import discord
import discord.errors
from discord.ext import commands

from src.lib.utils.basic_utils import get_member_name
from src.lib.utils.basic_utils import ready_up_cog


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx: commands.Context, user: discord.Member, reason: str = "UNDEFINED"):
        await ctx.trigger_typing()
        if user is None:
            return await ctx.reply("Você esqueceu de por o usúario que você quer kickar!")
        try:
            await ctx.guild.kick(ctx.guild.get_member(user.id), reason=reason)
        except discord.errors.Forbidden:
            return await ctx.reply(f"O(a) {get_member_name(user)} tem um cargo mais alto do que o meu :(")
        else:
            return await ctx.reply(f"O(a) {get_member_name(user)} foi kickado(a) com sucesso!")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx: commands.Context, user: discord.Member = None, reason: str = "UNDEFINED"):
        await ctx.trigger_typing()
        if user is None:
            return await ctx.reply("Você esqueceu de por o usuário que você quer banir!")
        try:
            await ctx.guild.kick(ctx.guild.get_member(user.id), reason=reason)
        except discord.errors.Forbidden:
            return await ctx.reply(f"O(a) {get_member_name(user)} tem um cargo mais alto do que o meu :(")
        else:
            return await ctx.reply(f"O(a) {get_member_name(user)} foi banido com sucesso!")

    @commands.command()
    async def clear(self, ctx: commands.Context, limit: Union[str, int] = 10):
        await ctx.trigger_typing()
        try:
            limit = int(float(limit)) + 2
        except ValueError:
            return await ctx.reply("O limite de mensagens precisa ser um número!")
        else:
            if int(limit) > 0:
                clear_str: str = f"Eu limpei {limit} mensagem, aqui no {ctx.channel.mention}"
                if limit != 1:
                    clear_str = f"Eu limpei {limit - 2} mensagens, aqui no {ctx.channel.mention}"

                res = await ctx.reply(clear_str, delete_after=10)
                await ctx.channel.purge(limit=limit, check=lambda m: m != res)
            else:
                return await ctx.reply("O limite de mensagens tem que ser maior que 0", delete_after=10)


"""
class DiscordLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def setlog(self, ctx: commands.Context, log_channel: discord.TextChannel = None):
        if log_channel is None:
            log_channel = ctx.channel

        DATABASE.child("LOG_CHANNELS").child(log_channel.id).set({
            "id": log_channel.id,
            "name": log_channel.name,
            "position": log_channel.position,
            "nsfw": str(log_channel.nsfw),
            "category_id": log_channel.category_id
        })

        return await ctx.reply(f"O novo canal de logs é o {log_channel.mention}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        log_channel = message.guild.get_channel(
            DATABASE.child("LOG_CHANNELS").child(message.channel.id).child("id").get().val()
        )

        deleted = discord.Embed(
            description=f"Mensagem deletada em {message.channel.mention}", color=0x4040EC
        ).set_author(name=message.author, url=discord.Embed.Empty, icon_url=message.author.avatar_url)

        if message.content != "":
            deleted.add_field(name="Conteúdo", value=message.content)

        deleted.timestamp = message.created_at
        await log_channel.send(embed=deleted)
"""


def setup(bot):
    bot.add_cog(Moderation(bot))
    # bot.add_cog(DiscordLog(bot))
