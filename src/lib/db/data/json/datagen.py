from discord.ext import commands
from os import path
from json import dump


def guild_dict(guild_name: str, guild_id: str) -> dict:
    return {"guild_name": str(guild_name), "guild_id": str(guild_id)}


def gendata(bot: commands.bot, abspath: path.abspath) -> dict:
    data = {
        "guilds": {
            "main_guild": guild_dict(guild_name=bot.main_guild, guild_id=bot.main_guild.id),
            "br_guild": guild_dict(guild_name=bot.br_guild, guild_id=bot.main_guild.id)
        },
        "users": {
            "bot_user": {
                "name": str(bot.bot_user),
                "user_id": str(bot.bot_user.id)
            },
            "privileged": {
                "bot_owners": {
                    "mscoy": {
                        "name": str(bot.mscoy),
                        "user_id": str(bot.mscoy.id)
                    }
                },
                "guild_owners": {
                    "zalur": {
                        "name": str(bot.zalur),
                        "user_id": str(bot.zalur.id)
                    }
                }
            }
        }
    }

    with open(abspath, "w+") as outfile:
        dump(data, outfile, indent=4)

        outfile.close()

    return data
