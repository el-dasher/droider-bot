from typing import List, Any

from github import InputFileContent
from discord.ext.commands import Cog
import discord
from src.lib.utils.basic_utils import ready_up_cog, get_member_name
from datetime import datetime
from random import choice
import json
from discord.ext import commands
from src.paths import MONTHS_PATH
from src.settings import DASHERGIT
from urllib.request import urlopen


def load_wd_data():

    wd_data = json.load(urlopen("https://gist.githubusercontent.com/el-dasher/"
                                "ddc5ae305a3cb4093393a140b55c53b3/raw/welcomer_data.json"))

    return wd_data


load_wd_data()
welcomer_guist = DASHERGIT.get_gist("ddc5ae305a3cb4093393a140b55c53b3")


month_data = json.load(open(MONTHS_PATH.absolute(), encoding="utf-8"))

# welcomer_data = (
#     wd_data := json.load(open(wd_path := Path("src/lib/db/data/json/welcomer_data.json").absolute()),
#                         encoding="utf-8")
# )


class PyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)


class Welcomer(Cog):
    welcome_channels: List[Any]

    def __init__(self, bot):

        load_wd_data()

        self.gen_channel = None
        self.bot = bot
        self.guilds = []

        # self.welcome_channels = list(wd_data)

    @Cog.listener()
    async def on_ready(self):

        ready_up_cog(self.bot, __name__)

    @Cog.listener()
    async def on_member_join(self, member: discord.Member):

        wd_data = load_wd_data()

        welcome_msg = ("SEJA BEM VIADO", "SEJA BEM VINDO")

        join_embed = discord.Embed(
            title=f"{choice(welcome_msg)} {get_member_name(member).upper()}",
            description=f"Um(a) novo(a) <@{member.id}> entrou no server",
        )

        created_month = month_data["MONTHS"][member.created_at.month]
        join_embed.set_thumbnail(url=member.avatar_url)
        join_embed.add_field(name="Nome de usuário", value=f"<@{member.id}>"),
        join_embed.add_field(name=f"ID do(a) {get_member_name(member)}", value=member.id)

        join_embed.add_field(
            name="É o lywi ou não?",
            value=f"Entrou no discord em {member.created_at.year}, no dia {member.created_at.day} de {created_month}"
        )

        # server_joined = member.server.channels

        joined_guild = str(member.guild.id)

        welcome_channel = wd_data[joined_guild]["id"]
        welcome_channel = self.bot.get_channel(welcome_channel)

        await welcome_channel.send(f"<@{member.id}>", embed=join_embed)

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        wd_data = load_wd_data()

        created_month = month_data["MONTHS"][member.created_at.month]
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

        welcome_channel = wd_data[left_guild]["id"]
        welcome_channel = self.bot.get_channel(welcome_channel)

        await welcome_channel.send(embed=left_embed)

    @commands.command(aliases=("welcome", "convidados", "setwelcome", "welcomechannel"))
    @commands.has_permissions(manage_channels=True)
    async def set_welcome(self, ctx: discord.ext.commands.context, channel=None):

        wd_data = load_wd_data()
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

        self.guilds.append(ctx.message.guild)

        def gendata() -> dict:

            for guild_data in self.guilds:
                wd_data[str(guild_data.id)] = {
                    "id": channel.id,
                    "name": channel.name,
                    "position": channel.position,
                    "nsfw": str(channel.nsfw),
                    "category_id": channel.category_id
                }

            return wd_data

        generated_data = gendata()
        self.gen_channel = ctx.message.channel

        # with open(wd_path, "w") as outfile:
        #   json.dump(generated_data, outfile, indent=4)
        #   outfile.close()

        wd_data.update(generated_data)
        wd_data = json.dumps(wd_data, indent=4, ensure_ascii=False)

        welcomer_guist.edit(
            description="NEW WELCOME DATA POGGERS?",
            files={"welcomer_data.json": InputFileContent(str(wd_data).replace("'", '"'))}
        )

        await ctx.send(f"O novo canal de boas vindas é o <#{channel.id}>")


def setup(bot):
    bot.add_cog(Welcomer(bot))
