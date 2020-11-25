from discord.ext import commands
import src.settings as settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from datetime import datetime
from src.lib.db.data.json.datagen import gendata
from pathlib import Path
import asyncio
from src.lib.utils.basic_utils import get_member_name

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
    main_guild: discord.guild.Guild
    br_guild: discord.guild.Guild
    mscoy: discord.user.User
    zalur: discord.user.User
    stdout: any
    bot_user: discord.client.User

    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()

        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=settings.PREFIX,
            # owner_ids=setup.PRIVILEGED["bot_owners"]["mscoy"],
            owner_ids="",
            intents=discord.Intents.all()
        )

    def setup(self):
        for cog in settings.COGS:
            self.load_extension(f"src.lib.cogs.{cog}")
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
        self.stdout = self.get_channel(769012183790256175)

        self.mscoy = self.get_user(750129701129027594)
        self.zalur = self.get_user(323516956642902016)

        def update_users():
            self.mscoy = self.get_user(750129701129027594)
            self.zalur = self.get_user(323516956642902016)

        if not self.ready:
            # Updates our useful_data.json
            self.scheduler.add_job(
                lambda: gendata(self, Path("src/lib/db/data/json/useful_data.json").absolute()),
                CronTrigger(second="0, 30")
            )
            self.scheduler.add_job(update_users, CronTrigger(second=0))

            # self.scheduler.add_job(lambda: print("a"), CronTrigger(second="0, 15, 30, 45"))
            self.scheduler.start()

            db.autosave(self.scheduler)

            while not self.cogs_ready.all_ready:
                await asyncio.sleep(0.5)

            self.ready = True
            print("O BOT ESTÁ PRONTO")
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
            ready_embed.set_footer(text=f"{get_member_name(self.mscoy)}...", icon_url=self.mscoy.avatar_url)
            ready_embed.set_author(name="osu!droid Brasil", icon_url=self.br_guild.icon_url)
            ready_embed.set_thumbnail(url=self.bot_user.avatar_url)

            await self.stdout.send(embed=ready_embed)

        else:
            print("O bot se reconectou")
            await self.stdout.send("Eu tô online denovo!")

    async def on_message(self, msg):
        await self.process_commands(msg)


bot = DroiderBR()
