import json
from datetime import datetime
from random import choice
from typing import List, Any

import discord
from discord.ext import commands
from discord.ext.commands import Cog
from src.paths import debug

from src.lib.utils.basic_utils import ready_up_cog, get_member_name
from src.paths import MONTHS_PATH
from src.setup import DATABASE

month_data = json.load(open(MONTHS_PATH, encoding="utf-8"))


# welcomer_data = (
#     wd_data := json.load(open(wd_path := Path("src/lib/db/data/json/welcomer_data.json").absolute()),
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
        if debug:
            return None
        created_month = month_data["MONTHS"][member.created_at.month - 1]

        left_embed = discord.Embed(title=f"O(A) {get_member_name(member)} saiu do servidor",
                                   description=f"Estou muito triste com uma notícia dessas..."
                                               f" <a:emojidanssa:780835162916651018>",
                                   timestamp=datetime.utcnow())
        left_embed.set_thumbnail(url=member.avatar_url)

        left_embed.add_field(name="Tag do usuário", value=get_member_name(member))
        left_embed.add_field(name=f"ID do(a) {get_member_name(member)}", value=member.id)
        left_embed.add_field(
            name="Será que era o lywi?",
            value=f"Entrou no discord em {member.created_at.year}, no dia {member.created_at.day} de {created_month}")

        left_guild = str(member.guild.id)
        welcome_channel = self.bot.get_channel(self.welcomer_data()[left_guild]["id"])

        await welcome_channel.send(embed=left_embed)

    @commands.command(aliases=("welcome", "convidados", "setwelcome", "welcomechannel"))
    @commands.has_permissions(manage_channels=True)
    async def set_welcome(self, ctx: discord.ext.commands.context, channel=None):

        channels = []

        for channel_ in ctx.message.guild.text_channels:
            channels.append(channel_.id)

        if channel is None:
            channel = ctx.message.channel

        if channel not in channels and channel != ctx.message.channel:
            count = 0
            while True:
                if channel not in channels:
                    if count < 1:
                        # noinspection PyBroadException
                        try:
                            channel = channel.split("<#")[1].split(">")[0]
                            break
                        except Exception:
                            await ctx.send(f"Não foi possível encontrar o canal: {channel}")

                            return None
                    count += 1
                else:
                    break

        if channel != ctx.message.channel:
            channel = self.bot.get_channel(int(channel))

        new_data = {
            "id": channel.id,
            "name": channel.name,
            "position": channel.position,
            "nsfw": str(channel.nsfw),
            "category_id": channel.category_id

        }

        DATABASE.child("WELCOMER_DATA").child(str(ctx.guild.id)).set(new_data)

        await ctx.reply(f"O novo canal de boas vindas é o <#{channel.id}> <a:blobhype:780576199558299649>")


def setup(bot):
    bot.add_cog(Welcomer(bot))
