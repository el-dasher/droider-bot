from discord.ext.commands import Bot as BotBase
import src.settings as setup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from datetime import datetime
import json
import os


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

    @staticmethod
    def guild_dict(guild_name: str, guild_id: str) -> dict:
        return {"guild_name": str(guild_name), "guild_id": str(guild_id)}

    async def on_ready(self):

        _main_guild = self.get_guild(769012183790256170)
        _br_guild = self.get_guild(702064150750429194)
        _bot_user = self.user
        _channel = self.get_channel(702218625079181342)
        _mscoy = _main_guild.get_member(750129701129027594)

        def export_data() -> None:

            data = {
                "guilds": {
                    "main_guild": self.guild_dict(guild_name=_main_guild, guild_id=_main_guild.id),
                    "br_guild": self.guild_dict(guild_name=_br_guild, guild_id=_main_guild.id)
                },
                "users": {
                    "bot_user": {
                        "name": str(_bot_user),
                        "user_id": str(_bot_user.id)
                    },
                    "mscoy": {
                        "name": str(_mscoy),
                        "user_id": str(_mscoy.id)
                    }
                }
            }

            with open(os.path.abspath("./lib/db/data/json/useful_data.json"), "w+") as outfile:
                json.dump(data, outfile)

            return None

        if not self.ready:
            self.ready = True
            print("O bot já ta pronto pra ação!")

            export_data()  # Exports useful data in a json file
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
