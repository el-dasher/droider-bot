from discord.ext.commands import Bot as BotBase
import src.settings as setup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from datetime import datetime


class DroiderBR(BotBase):
    def __init__(self):
        self.TOKEN = setup.BOT_TOKEN
        self.PREFIX = setup.PREFIX
        self.ready = False
        self.scheduler = AsyncIOScheduler

        super().__init__(command_prefix=setup.PREFIX, owner_ids=setup.OWNERS_ID, intents=discord.Intents.all())

    def run(self):
        print(f'Iniciando o bot')
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print(f'O "{self.user}" se conectou...')

    async def on_disconnect(self):
        print(f'O "{self.user}" se desconectou...')

    async def on_ready(self):

        _guild = bot.get_guild(769012183790256170)
        _br_guild = bot.get_guild(702064150750429194)
        _bot_user = _guild.get_member(769693989023514634)
        _channel = self.get_channel(702218625079181342)
        _mscoy = _guild.get_member(750129701129027594)

        if not self.ready:
            self.ready = True
            print("O bot já ta pronto pra ação!")
            # await channel.send("Eu tô online!")
            ready_embed = discord.Embed(
                title="Droider online!",
                description="O Droider tá online, se eu fosse você eu teria cuidado, mero membro comum.",
                colour=0xf769ff, timestamp=datetime.utcnow()
            )
            embed_fields = [
                (
                    f"{setup.PREFIX}help",
                    "> Peça uma ajudinha com os comandos do bot, aproveita e me faz um café.", True
                ),
                ("Criador", "> Não foi O MsCoy", True)
            ]
            for name, value, inline in embed_fields:
                ready_embed.add_field(name=name, value=value, inline=inline)

            # ready_embed.set_author(name="Droider")
            ready_embed.set_footer(text="O MsCoy...", icon_url=_mscoy.avatar_url)
            ready_embed.set_author(name="osu!droid Brasil", icon_url=_br_guild.icon_url)
            ready_embed.set_thumbnail(url=_bot_user.avatar_url)

            await _channel.send(embed=ready_embed)
        else:
            print("O bot se reconectou")
            await _channel.send("Eu tô online denovo!")

    async def on_message(self, msg):
        pass


bot = DroiderBR()
