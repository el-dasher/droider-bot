from ossapi import ossapi
from os import getenv
from discord.ext import commands
import discord
from src.lib.utils.basic_utils import ready_up_cog
from src.settings import DATABASE

api = ossapi(getenv("OSU_API"))


class OsuGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command(aliases=["osu"])
    async def osuplayer(self, ctx: commands.Context, user=None):
        # user_json = api.get_user({"u": user})[0]

        user_json = api.get_user({"u": DATABASE.child("OSU_USERS").child(ctx.author.id).get().val()["user"]})[0]

        if user:
            if "" in user:
                if "<@!" in user:
                    user = user.replace("<@!", "").replace(">", "")
                elif "<@" in user:
                    user = user.replace("<@", "").replace(">", "")

                try:
                    user_json = api.get_user({"u": DATABASE.child("OSU_USERS").get().val()[user]["user"]})

                except KeyError:
                    user_json = api.get_user({"u": user})

                    if user_json == []:
                        await ctx.reply("Não foi possivel encontrar o usuário!")

        try:
            user_json = user_json[0]
        except (IndexError, KeyError):
            user_json = user_json

        print(user_json)

        user_embed = discord.Embed(
            title=f"Perfil do {user_json['username']}",
            description=f"[Link do perfil](https://osu.ppy.sh/users/{user_json['user_id']})",
        )

        try:
            user_json["accuracy"] = f"{float(user_json['accuracy']):.2f}"
        except TypeError:
            user_json["accuracy"] = "0.00"

        user_embed.set_thumbnail(url=f"https://a.ppy.sh/{user_json['user_id']}")
        user_json["pp_raw"] = 0.00 if user_json["pp_raw"] is None else user_json["pp_raw"]

        user_embed.add_field(name="Performance", value=f"{float(user_json['pp_raw']):.2f}pp")

        if user_json["pp_rank"] is not None or user_json["pp_country_rank"] is not None:
            user_embed.add_field(name="Rank global", value=f'#{user_json["pp_rank"]}')
            user_embed.add_field(name="Rank local", value=f"#{user_json['pp_country_rank']}")
        user_embed.add_field(name="Precisão", value=f'{user_json["accuracy"]}%')

        user_embed.add_field(name="Level", value=f"{float(user_json['level']):.2f}") if type(user_json["level"]) \
            is float \
            else user_embed.add_field(name="Level", value=f"0.00")

        await ctx.reply(content=f"<@{ctx.author.id}>", embed=user_embed)

    @commands.command(aliases=["osuset"])
    async def osu_set(self, ctx, user=None):
        try:
            user_json_ = api.get_user({"u": user})[0]
            DATABASE.child("OSU_USERS").child(ctx.author.id).set({"user": user})
        except (IndexError, ValueError):
            if user is None:
                await ctx.reply("Você esqueceu de por para qual usuário você quer setar!")
            else:
                print(user)
                await ctx.reply(f"Não foi possivel encontrar um usuário chamado: {user}")

            return

        await ctx.reply(f"O seu usuário foi setado para: {user}")
        return user_json_


def setup(bot):
    bot.add_cog(OsuGame(bot))
