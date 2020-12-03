from ossapi import ossapi
from os import getenv
from discord.ext import commands
import discord
from src.lib.utils.basic_utils import ready_up_cog
from src.settings import DATABASE
from dateutil.parser import parse
from datetime import datetime

osu_api = ossapi(getenv("OSU_API"))


class OsuGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def get_user(user: tuple):
        return "".join(user).replace(" ", "_")

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command(aliases=["osu"])
    async def osuplayer(self, ctx: commands.Context, *user):
        # user_json = osu_api.get_user({"u": user})[0]
        try:
            user_json = osu_api.get_user({"u": DATABASE.child("OSU_USERS").child(ctx.author.id).get().val()["user"]})[0]
        except TypeError:
            await ctx.reply("Você não possui uma conta cadastrada, use `osu!set <user>`")
            return

        if user:
            user = self.get_user(user)
            if "" in user:
                if "<@!" in user:
                    user = user.replace("<@!", "").replace(">", "")
                elif "<@" in user:
                    user = user.replace("<@", "").replace(">", "")

                try:
                    user_json = osu_api.get_user({"u": DATABASE.child("OSU_USERS").get().val()[user]["user"]})

                except KeyError:
                    user_json = osu_api.get_user({"u": user})

                    if user_json == []:
                        return await ctx.reply("Não foi possivel encontrar o usuário!")

        try:
            user_json = user_json[0]
        except (IndexError, KeyError):
            user_json = user_json

        def is_not_none(item):
            if item is None:
                item = 0.00
            return float(item)

        profile_acc = is_not_none(user_json["accuracy"])
        profile_pp = is_not_none(user_json["pp_raw"])
        profile_level = is_not_none(user_json['level'])

        user_embed = discord.Embed(
            title=(
                f"<:osulogo:783846581371273246> Perfil do osu!standard"
                f" do(a) {(profile_username := user_json['username'])}"
            ),
            description=(
                f"**[Link do perfil do(a) {profile_username}](https://osu.ppy.sh/users/{user_json['user_id']})**\n"
            ), timestamp=datetime.utcnow()
        )

        user_embed.add_field(name="__Performance__", value=(
                "**"
                f"Accuracy: `{profile_acc :.2f}`\nPP: `{profile_pp:.2f}`\n"
                f"Rank PP: `#{user_json['pp_rank']}`\n"
                f"RANK {(country := user_json['country'])}(:flag_{country.lower()}:): `#{user_json['pp_country_rank']}`"
                "**"
            )
        )

        profile_best_play = osu_api.get_user_best({"u": user_json['user_id']})[0]
        played_beatmap_profile = osu_api.get_beatmaps({"b": profile_best_play["beatmap_id"]})[0]

        user_embed.add_field(name="__Melhor play__", value=(
            "**"
            f"PP: `{profile_best_play['pp']}`\n"
            f"[{played_beatmap_profile['title']}](https://osu.ppy.sh/beatmapsets/{profile_best_play['beatmap_id']})\n"
            f"Rank: `{profile_best_play['rank']}`"
            "**"
        ))

        print(profile_best_play)

        user_embed.set_footer(text=f"Level: {profile_level:.2f}")
        user_embed.set_thumbnail(url=f"https://a.ppy.sh/{user_json['user_id']}")

        await ctx.reply(content=f":flag_{user_json['country'].lower()}:")
        await ctx.reply(content=f"<@{ctx.author.id}>", embed=user_embed)

    @commands.command(aliases=["osuset"])
    async def osu_set(self, ctx, *user):
        if user:
            self.get_user(user)
        else:
            return await ctx.reply("Você esqueceu de por para qual usuário(a) você quer setar!")

        try:
            set_user_json = osu_api.get_user({"u": user})[0]
            DATABASE.child("OSU_USERS").child(ctx.author.id).set({"user": user})
        except (IndexError, ValueError):
            return await ctx.reply(f"Não foi possivel encontrar um(a) usuário(a) chamado(a): {user}")

        osuset_embed = discord.Embed(
            title=f"Você cadastrou seu usuário! {set_user_json['username']}"
        )

        osuset_embed.set_image(url=f"https://a.ppy.sh/{set_user_json['user_id']}")

        await ctx.reply(f"<@{ctx.author.id}>", embed=osuset_embed)

    @commands.command()
    async def recent(self, ctx, *user):
        if user:
            user = self.get_user(user)
            try:
                username = osu_api.get_user({'u': user})[0]['username']
            except IndexError:
                return await ctx.reply(f"Não foi possivel encontrar o usuário: {user}")
        else:
            return await ctx.reply(
                "Você não tem uma conta cadastrada, utilize `ms!osuset <user>`"
                "ou informe qual usuario você quer pegar a play recente `ms!rs <user>`"
            )

        try:
            recentplay = osu_api.get_user_recent({"u": user})[0]
        except IndexError:
            await ctx.reply(f"O {username} não possui nenhuma play recente :(")
        else:
            played_map = osu_api.get_beatmaps({"b": recentplay["beatmap_id"]})[0]
            played_map['difficultyrating'] = float(played_map['difficultyrating'])

            accuracy = "NÃO POR ENQUANTO"

            recentplay['date'] = recentplay['date'].replace("-", ".")
            recent_embed = discord.Embed(
                description=f"**[{played_map['title']}](https://osu.ppy.sh/beatmapsets/{played_map['beatmapset_id']})**"
                            f" ({(played_map['difficultyrating']):.2f}★)\n"
                            f"Dificuldade: {played_map['version']}\n"
                            f"Score: {recentplay['score']} •"
                            f" {recentplay['maxcombo']}/{played_map['max_combo']}",
                timestamp=parse(recentplay['date'])
            )

            rs_user_json = osu_api.get_user({"u": user})[0]
            recent_embed.set_thumbnail(
                url=f"https://b.ppy.sh/thumb/{played_map['beatmapset_id']}l.jpg"
            )
            recent_embed.set_footer(text=f"Acurácia: {accuracy}%")
            recent_embed.set_author(icon_url=f"https://a.ppy.sh/{rs_user_json['user_id']}",
                                    name=f"Play recente do(a) {username}")

            print(played_map)
            print(recentplay)

            await ctx.reply(embed=recent_embed)


def setup(bot):
    bot.add_cog(OsuGame(bot))
