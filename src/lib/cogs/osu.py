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

        try:
            user_json = api.get_user({"u": DATABASE.child("OSU_USERS").child(ctx.author.id).get().val()["user"]})[0]
        except TypeError:
            await ctx.reply("Você não possui uma conta cadastrada, use `osu!set <user>`")
            return

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
                        return

        try:
            user_json = user_json[0]
        except (IndexError, KeyError):
            user_json = user_json

        print(user_json)

        user_embed = discord.Embed(
            title=f"<:osulogo:783846581371273246> Perfil do osu!standard do(a) {user_json['username']}",
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

        if type(user_json["level"]) is None:
            user_json["level"] = 0.00
            print(user_json["level"])
        print(user_json["level"])
        user_embed.add_field(name="Level", value=f"{float(user_json['level']):.2f}")
        await ctx.reply(content=f"<@{ctx.author.id}>", embed=user_embed)

    @commands.command(aliases=["osuset"])
    async def osu_set(self, ctx, user=None):
        try:
            set_user_json = api.get_user({"u": user})[0]
            DATABASE.child("OSU_USERS").child(ctx.author.id).set({"user": user})
        except (IndexError, ValueError):
            if user is None:
                await ctx.reply("Você esqueceu de por para qual usuário(a) você quer setar!")
            else:
                print(user)
                await ctx.reply(f"Não foi possivel encontrar um(a) usuário(a) chamado(a): {user}")

            return

        osuset_embed = discord.Embed(
            title=f"Você cadastrou seu usuário! {set_user_json['username']}"
        )

        osuset_embed.set_image(url=f"https://a.ppy.sh/{set_user_json['user_id']}")

        await ctx.reply(f"<@{ctx.author.id}>", embed=osuset_embed)


def setup(bot):
    bot.add_cog(OsuGame(bot))
