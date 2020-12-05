from ossapi import ossapi
from os import getenv
from discord.ext import commands
import discord
from src.lib.utils.basic_utils import ready_up_cog
from src.settings import DATABASE
from dateutil.parser import parse
from datetime import datetime
from src.lib.utils.droid_data_getter import get_droid_data

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
            f"Beatmap: [{played_beatmap_profile['title']}](https://osu.ppy.sh/beatmapsets/{profile_best_play['beatmap_id']})\n"
            f"Rank: `{profile_best_play['rank']}`"
            "**"
        ))

        
        user_embed.set_thumbnail(url=f"https://a.ppy.sh/{user_json['user_id']}")
        user_embed.set_footer(text=f"Level: {profile_level:.2f}")
       
        await ctx.reply(content=f"<@{ctx.author.id}>", embed=user_embed)

    @commands.command(aliases=["osuset"])
    async def osu_set(self, ctx, *user):
        if user:
            user = self.get_user(user)
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
                description=f"**[{played_map['title']}](https://osu.ppy.sh/beatmapsets/{played_map['beatmapset_id']})"
                            f" ({(played_map['difficultyrating']):.2f}★)\n"
                            f"Dificuldade: {played_map['version']}\n"
                            f"Score: {recentplay['score']} •"
                            f" {recentplay['maxcombo']}/{played_map['max_combo']}**",
                timestamp=parse(recentplay['date'])
            )

            rs_user_json = osu_api.get_user({"u": user})[0]
            recent_embed.set_thumbnail(
                url=f"https://b.ppy.sh/thumb/{played_map['beatmapset_id']}l.jpg"
            )
            recent_embed.set_footer(text=f"Acurácia: {accuracy}%")
            recent_embed.set_author(icon_url=f"https://a.ppy.sh/{rs_user_json['user_id']}",
                                    name=f"Play recente do(a) {username}")

            await ctx.reply(embed=recent_embed)


class OsuDroid(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.missing_uid_msg = "Você esqueceu de por a `<uid>` do usuário!" \
                               " você também pode setar seu usuário com `ms!droidset <user>`"

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command(name="d/rs", aliases=["d/recentme"])
    async def droidrecent(self, ctx, uid=None):
        if uid is None:
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception as e:
                print(e)
                return await ctx.reply(self.missing_uid_msg)
        try:
            await ctx.reply(f"Sua play mais recente: {(await get_droid_data(uid))['beatmap_data']['rs_0']}")
        except KeyError:
            await ctx.reply(f"Não existe uma user id chamada: {uid}")

    @commands.command(name="d/ppcheck")
    async def pp_check(self, ctx, uid=None):
        if uid is None:
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception as e:
                print(e)
                return await ctx.reply(self.missing_uid_msg)
        top_plays = (await get_droid_data(uid))["pp_data"][:5]

        await ctx.reply(top_plays)

    @commands.command(aliases=["d/pfme"])
    async def droid_pfme(self, ctx, uid=None):
        
        if uid is None:
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception as e:
                print(e)
                return await ctx.reply(self.missing_uid_msg)
        try:
            profile_data = (await get_droid_data(uid))["user_data"]
            profile_embed = discord.Embed()

            profile_embed.set_thumbnail(url=profile_data['avatar_url'])
            profile_embed.set_author(url=f"http://ops.dgsrz.com/profile.php?uid={uid}",
                                     name=f"Perfil do(a) {profile_data['username']}")

            profile_embed.add_field(name="---Performance", value="**"
                                                                 f"Ele é do(a) {(user_country := profile_data['country'])}(:flag_{user_country.lower()}:)\n"
                                                                 f"Total score: `{profile_data['total_score']}`\n"
                                                                 f"Performance: `{int(profile_data['raw_pp']) if profile_data['raw_pp'] != 'OFFLINE' else profile_data['raw_pp']}dpp`\n"
                                                                 f"Overall acc: `{profile_data['overall_acc']}%`\n"
                                                                 f"Playcount: `{profile_data['playcount']}`"
                                                                 f"**")

            await ctx.reply(content=f"<@{ctx.author.id}>", embed=profile_embed)
        except KeyError as e:
            print(e)
            await ctx.reply(f"Não existe uma user id chamada: {uid}")

    @commands.command(name="droidset")
    async def droid_set(self, ctx, uid=None):

        if not uid:
            return await ctx.reply("Você esqueceu de por para qual usuário(a) você quer setar!")

        user_data = await (get_droid_data(uid))["user_data"]

        DATABASE.child("DROID_USERS").child(ctx.author.id).set({"user": user_data})

        droidset_embed = discord.Embed(
            title=f"Você cadastrou seu usuário! {user_data['username']}"
        )

        droidset_embed.set_image(url=user_data["avatar_url"])

        await ctx.reply(f"<@{ctx.author.id}>", embed=droidset_embed)

    @commands.command(hidden=True)
    async def is_pp_board_on(self, ctx: discord.ext.commands.Context, list_array: list):
        if list_array == []:
            await ctx.reply("O usuário que você citou talvez não tenha plays, ou a pp_board do rian3337 está offline!")
            return False
        else:
            return True


def setup(bot):
    bot.add_cog(OsuGame(bot))
    bot.add_cog(OsuDroid(bot))
