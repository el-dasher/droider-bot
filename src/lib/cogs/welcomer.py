from discord.ext.commands import Cog
import discord
from src.lib.utils.basic_utils import ready_up_cog, get_member_name
from datetime import datetime
from random import choice
import json
from os.path import abspath
from discord.ext import commands

json_path = abspath("../src/lib/db/data/json/months.json")
month_data = json.load(open(json_path, encoding="utf-8"))


class Welcomer(Cog):
    welcome_channel: discord.TextChannel

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_msg = ("SEJA BEM VIADO", "SEJA BEM VINDO")
        join_embed = discord.Embed(
            title=f"{choice(welcome_msg)} {get_member_name(member).upper()}",
            description=f"Um novo <@{member.id}> entrou no server",
        )

        created_month = month_data["MONTHS"][member.created_at.month]
        join_embed.set_thumbnail(url=member.avatar_url)
        join_embed.add_field(name="Nome de usuário", value=get_member_name(member))
        join_embed.add_field(name="ID do discord", value=member.id)

        join_embed.add_field(name="É o lywi ou não?", value=f"Entrou no discord em {member.created_at.year}"
                                                            f" No dia {member.created_at.day} de {created_month}")

        join_embed.set_footer(
            text=f"{get_member_name(member)} Entrou no servidor às {datetime.utcnow().hour} horas"
                 f" e {datetime.utcnow().minute} minutos hoje", icon_url=member.avatar_url
        )

        # server_joined = member.server.channels

        await self.bot.stdout.send(embed=join_embed)

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot.stdout.send(f"Que pena, o {get_member_name(member)} saiu do servidor, compreensivel apenas...")

    @commands.command(aliases=("welcome_channel", "convidados"))
    @commands.has_permissions(manage_channels=True)
    async def set_welcome(self, ctx: discord.ext.commands.context, channel: discord.TextChannel = None):
        channels = []

        for channel_ in ctx.message.guild.channels:
            channels.append(channel_)

        if channel is None:
            channel = ctx.message.channel
            print(channel)

        # elif channel != ctx.message.guild:
        #    await ctx.send(f"Não foi possivel encontrar o canal: <#{channel.id}>")

            return None

        self.welcome_channel = ctx.message.guild.name
        await ctx.send(f"O novo canal de boas vindas é o <#{channel.id}>")


def setup(bot):
    bot.add_cog(Welcomer(bot))
