import discord
from typing import Union
import time
import asyncio


def ready_up_cog(bot, __name___: __name__):
    if not bot.ready:
        bot.cogs_ready.ready_up(get_pyfn(__name___))


def get_pyfn(filename: __name__) -> str:
    f = filename.split(".")[-1]
    return f


def get_member_name(member: Union[discord.Member, discord.User]) -> str:
    return str(member).split("#")[-2]


async def timed_out(seconds=60):
    start_time = time.time()
    while time.time() - start_time < seconds:
        await asyncio.sleep(1)
    return True

