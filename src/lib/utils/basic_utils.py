from typing import Union

import discord


def ready_up_cog(bot, __name___: __name__):
    if not bot.ready:
        bot.cogs_ready.ready_up(get_pyfn(__name___))


def get_pyfn(filename: __name__) -> str:
    f = filename.split(".")[-1]
    return f


def get_member_name(member: Union[discord.Member, discord.User]) -> str:
    return str(member).split("#")[-2]
