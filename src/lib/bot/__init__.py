from discord.ext import commands
import src.settings as settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
import asyncio
from typing import Union

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
    mscoy: Union[discord.User, discord.Member]
    zalur: Union[discord.User, discord.Member]
    stdout: discord.TextChannel

    def __init__(self):

        self.sent_time = 0
        self.ready = False
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler()
        self.sent_channels = []

        super().__init__(
            command_prefix=settings.PREFIX,
            owner_ids=[750129701129027594],
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
        # self.scheduler = AsyncIOScheduler()

        self.br_guild = self.get_guild(702064150750429194)
        self.stdout = self.get_channel(769012183790256175)

        self.mscoy = self.get_user(750129701129027594)
        self.zalur = self.get_user(323516956642902016)

        if not self.ready:
            # self.scheduler.add_job(lambda: print("a"), CronTrigger(second="0, 15, 30, 45"))
            # self.scheduler.start()

            while not self.cogs_ready.all_ready:
                await asyncio.sleep(0.5)

            self.ready = True
            print("O BOT ESTÁ PRONTO")

            await self.stdout.send("O droider está online!")

        else:
            print("O bot se reconectou")
            await self.stdout.send("Eu tô online denovo!")

    async def on_message(self, msg: discord.Message, already_timed=False, counter=0):

        if msg.author.id == self.user.id:
            return

        if isinstance(msg.channel, discord.DMChannel):
            if msg.channel.id not in self.sent_channels:
                self.sent_channels.append(msg.channel.id)
                await msg.channel.send("Não respondo a mensagens diretas, kthx ;)")
                await asyncio.sleep(86400)
                self.sent_channels.remove(msg.channel.id)

                return

        print(f"{msg.author}: {msg}")
        await self.process_commands(msg)


bot = DroiderBR()
