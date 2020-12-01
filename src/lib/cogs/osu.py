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
    async def osuplayer(self, ctx: commands.Context, user: discord.Member = None):
        
        while True:
            try:
                user_json = api.get_user({"u": user})[0]

                if not user_json:
                    user_json = api.get_user(
                            {"u": (user := DATABASE.child("OSU_USERS").child(user.id).get().val()["user"])}
                        )[0]
                else:
                    break

                print(user_json)

            except (IndexError, ValueError):
                if user is None:

                    user_json = api.get_user(
                        {"u": (user := DATABASE.child("OSU_USERS").child(ctx.author.id).get().val()["user"])}
                    )[0]
                    if user_json:
                        break
                    elif not user:
                        await ctx.reply("Você precisa informar um usuário,"
                                        " talvez você queira setar seu usuário utilizado `ms!osuset`")
                        return
                else:
                    await ctx.reply("Usuário não encontrado")
                    return

        if user_json is None:
            return

        user_embed = discord.Embed(
            title=f"Perfil do {user_json['username']}",
            description=f"[Link do perfil](https://osu.ppy.sh/users/{user_json['user_id']})",
        )

        user_json["accuracy"] = f"{float(user_json['accuracy']):.2f}"

        user_embed.set_thumbnail(url=f"https://a.ppy.sh/{user_json['user_id']}")
        user_embed.add_field(name="Performance", value=f"{user_json['pp_raw']}pp")
        user_embed.add_field(name="Rank global", value=f'#{user_json["pp_rank"]}')
        user_embed.add_field(name="Precisão", value=f'{user_json["accuracy"]}%')
        user_embed.add_field(name="Level", value=user_json["level"])
        user_embed.add_field(name="Rank local", value=user_json["pp_country_rank"])

        await ctx.reply(content=f"<@{ctx.author.id}>", embed=user_embed)

    @commands.command(aliases=["osuset"])
    async def osu_set(self, ctx, user=None):
        try:
            user_json = api.get_user({"u": user})[0]
            DATABASE.child("OSU_USERS").child(ctx.author.id).set({"user": user})
        except (IndexError, ValueError):
            if user is None:
                await ctx.reply("Você esqueceu de por para qual usuário você quer setar!")
            else:
                print(user)
                await ctx.reply(f"Não foi possivel encontrar um usuário chamado: {user}")

            return

        await ctx.reply(f"O seu usuário foi setado para: {user}")
        return user_json


def setup(bot):
    bot.add_cog(OsuGame(bot))
