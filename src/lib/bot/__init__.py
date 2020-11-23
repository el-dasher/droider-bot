from discord.ext import commands
import src.settings as settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from datetime import datetime
from src.lib.db.data.json.datagen import gendata
from os.path import abspath

from ..db import db
# from apscheduler.triggers.cron import CronTrigger


class Ready(object):
    def __init__(self):
        for cog in settings.COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"A cog {cog} está pronta")

    @property
    def all_ready(self):
        return all([getattr(self, cog) for cog in settings.COGS])


class DroiderBR(commands.Bot):
    def __init__(self):
        self.stdout, self.main_guild, self.br_guild, self.bot_user = None, None, None, None
        self.mscoy, self.zalur = None, None
        self.ready = False
        self.cogs_ready = False

        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=settings.PREFIX,
            # owner_ids=setup.PRIVILEGED["bot_owners"]["mscoy"],
            owner_ids="",
            intents=discord.Intents.all()
        )

    def setup(self):
        for cog in settings.COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"A cog {cog} foi carregada!")

        print("Todas as cogs foram carregadas")

    def run(self):
        print(f'Iniciando o bot')
        print("Configurando as cogs")
        self.setup()

        super().run(settings.BOT_TOKEN, reconnect=True)

    async def on_connect(self):
        print(f'O "{self.user}" se conectou...')

    async def on_disconnect(self):
        print(f'O "{self.user}" se desconectou...')

    # async def auto_msg(self):
    #   _channel = self.get_channel(702077490423922748)
    #   await _channel.send("Eu sou uma mensagem automatizada")

    async def on_ready(self):
        self.scheduler = AsyncIOScheduler()

        self.main_guild = self.get_guild(769012183790256170)
        self.br_guild = self.get_guild(702064150750429194)
        self.bot_user = self.user
        self.stdout = self.get_channel(702077490423922748)
        self.mscoy = self.get_user(750129701129027594)
        self.zalur = self.get_user(323516956642902016)

        gendata(self, abspath("./lib/db/data/json/useful_data.json"))

        if not self.ready:
            gendata(self, abspath("./lib/db/data/json/useful_data.json"))
            # self.scheduler.add_job(self.auto_msg, CronTrigger(second="0, 15, 30, 45"))
            self.scheduler.start()

            db.autosave(self.scheduler)
            self.ready = True
            ready_embed = discord.Embed(
                title="Droider online!",
                description="O Droider tá online, se eu fosse você eu teria cuidado, mero membro comum.",
                colour=0xf769ff, timestamp=datetime.utcnow()
            )
            embed_fields = [
                (
                    f"{settings.PREFIX}help",
                    "> Peça uma ajudinha com os comandos do bot, aproveita e me faz um café.", True
                ),
                ("Criador", f"> Não foi o <@{self.mscoy.id}>", True)
            ]
            for name, value, inline in embed_fields:
                ready_embed.add_field(name=name, value=value, inline=inline)

            # ready_embed.set_author(name="Droider")
            ready_embed.set_footer(text="O MsCoy...", icon_url=self.mscoy.avatar_url)
            ready_embed.set_author(name="osu!droid Brasil", icon_url=self.br_guild.icon_url)
            ready_embed.set_thumbnail(url=self.bot_user.avatar_url)

        else:
            print("O bot se reconectou")
            await self.stdout.send("Eu tô online denovo!")

    async def on_message(self, msg):
        pass


bot = DroiderBR()
