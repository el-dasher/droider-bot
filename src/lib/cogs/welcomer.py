import json
from datetime import datetime
from random import choice
from typing import List, Any

import discord
from discord.ext import commands
from discord.ext.commands import Cog

from src.lib.utils.basic_utils import ready_up_cog, get_member_name
from src.paths import MONTHS_PATH
from src.paths import debug
from src.setup import DATABASE

month_data = json.load(open(MONTHS_PATH, encoding="utf-8"))


# welcomer_data = (
#     wd_data := json.load(open(wd_path := Path("src/lib/firebase/firebase/json/welcomer_data.json").absolute()),
#                         encoding="utf-8")
# )


class Welcomer(Cog):
    welcome_channels: List[Any]

    def __init__(self, bot):

        self.bot = bot

        # self.welcome_channels = list(wd_data)

    @staticmethod
    def welcomer_data():
        return DATABASE.child("WELCOMER_DATA").get().val()

    @Cog.listener()
    async def on_ready(self):

        ready_up_cog(self.bot, __name__)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if debug:
            return None

        welcome_msg = ("SEJA BEM VIADO", "SEJA BEM VINDO")

        join_embed = discord.Embed(
            title=f"{choice(welcome_msg)}, {get_member_name(member).upper()}",
            description=f"Um(a) novo(a) <@{member.id}> entrou no server",
        )

        created_month = month_data["MONTHS"][member.created_at.month - 1]

        join_embed.set_thumbnail(url=member.avatar_url)
        join_embed.add_field(name="Nome de usuário", value=f"<@{member.id}>"),
        join_embed.add_field(name=f"ID do(a) {get_member_name(member)}", value=member.id)

        join_embed.add_field(
            name="É o lywi ou não?",
            value=f"Entrou no discord em {member.created_at.year}, no dia {member.created_at.day} de {created_month}"
        )

        # server_joined = member.server.channels

        joined_guild = str(member.guild.id)

        welcome_channel = self.bot.get_channel(self.welcomer_data()[joined_guild]["id"])

        await welcome_channel.send(f"<@{member.id}>", embed=join_embed)

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        if not debug:
            return None

        remove_str: str = f"O(A) {get_member_name(member)} saiu do servidor"
        if member.guild.fetch_ban(member):
            remove_str = f"O(A) {get_member_name(member)} foi banido(a) do servidor"
        elif member.guild.get_member(member.id) is None:
            remove_str = f"O(A) {get_member_name(member)} foi kickado(a) do servidor"

        created_month = month_data["MONTHS"][member.created_at.month - 1]

        remove_embed = discord.Embed(title=remove_str,
                                     description=f"Estou muito triste com uma notícia dessas..."
                                                 f" <a:emojidanssa:780835162916651018>",
                                     timestamp=datetime.utcnow())
        remove_embed.set_thumbnail(url=member.avatar_url)

        remove_embed.add_field(name="Tag do usuário", value=get_member_name(member))
        remove_embed.add_field(name=f"ID do(a) {get_member_name(member)}", value=member.id)
        remove_embed.add_field(
            name="Será que era o lywi?",
            value=f"Entrou no discord em {member.created_at.year}, no dia {member.created_at.day} de {created_month}")

        left_guild = str(member.guild.id)
        welcome_channel = self.bot.get_channel(self.welcomer_data()[left_guild]["id"])

        await welcome_channel.send(embed=remove_embed)

    @commands.command(aliases=("welcome", "convidados", "setwelcome", "welcomechannel"))
    @commands.has_permissions(manage_channels=True)
    async def set_welcome(self, ctx: discord.ext.commands.context, welcome_channel: discord.TextChannel = None):
        if welcome_channel is None:
            welcome_channel = ctx.channel

        DATABASE.child("WELCOMER_DATA").child(str(ctx.guild.id)).set({
            "id": welcome_channel.id,
            "name": welcome_channel.name,
            "position": welcome_channel.position,
            "nsfw": str(welcome_channel.nsfw),
            "category_id": welcome_channel.category_id

        })

        await ctx.reply(f"O novo canal de boas vindas é o {welcome_channel.mention} <a:blobhype:780576199558299649>")


def setup(bot):
    bot.add_cog(Welcomer(bot))
