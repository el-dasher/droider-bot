import asyncio
import time
from datetime import datetime
from os import getenv

import discord
import requests
from dateutil.parser import parse
from discord.ext import commands, tasks
from ossapi import ossapi
from pytz import timezone
from src.paths import debug

from src.lib.utils.basic_utils import ready_up_cog
from src.lib.utils.droid_data_getter import get_droid_data
from src.setup import DATABASE

osu_api = ossapi((OSU_API := getenv("OSU_API")))


def mention_to_uid(msg):
    if "<@!" in msg:
        return msg.replace("<@!", "").replace(">", "")
    elif "<@" in msg:
        return msg.replace("<@", "").replace(">", "")
    else:
        return msg


async def get_beatmap_data(hash_):

    default_data = {
        "max_combo": 0,
        "diff_approach": 0,
        "diff_aim": 0,
        "diff_speed": 0,
        "bpm": 0,
        "difficultyrating": 0,
        "beatmap_id": 0,
        "beatmapset_id": 0,
        "title": "?"
    }

    # noinspection PyBroadException
    try:
        await asyncio.sleep(0.5)
        beatmap_data = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_API}&h={hash_}").json()
    except Exception:
        beatmap_data = default_data
    else:
        try:
            beatmap_data = beatmap_data[0]
        except IndexError:
            beatmap_data = default_data

    return beatmap_data


class OsuGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def get_user(user: tuple):
        return "".join(user).replace(" ", "_")

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command(name="osu")
    async def osuplayer(self, ctx: commands.Context, *user):
        # user_json = osu_api.get_user({"u": user})[0]

        if user:
            user = self.get_user(mention_to_uid(user))
            try:
                user_json = osu_api.get_user({"u": DATABASE.child("OSU_USERS").get().val()[user]["user"]})
            except KeyError:
                user_json = osu_api.get_user({"u": user})

                if user_json == []:
                    return await ctx.reply("Não foi possivel encontrar o usuário!")
        else:
            try:
                user_json = \
                    osu_api.get_user({"u": DATABASE.child("OSU_USERS").child(ctx.author.id).get().val()["user"]})[0]
            except TypeError:
                return await ctx.reply("Você não possui uma conta cadastrada, use `ms!osuset <user>`")
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
            f"PP: `{int(float(profile_best_play['pp']))}pp`\n"
            f"Beatmap: [{played_beatmap_profile['title']}]"
            f"(https://osu.ppy.sh/beatmapsets/{profile_best_play['beatmap_id']})\n"
            f"Rank: `{profile_best_play['rank']}`"
            "**"
        ))

        user_embed.set_thumbnail(url=f"https://a.ppy.sh/{user_json['user_id']}")
        user_embed.set_footer(text=f"Level: {profile_level:.2f}")

        await ctx.reply(content=f"<@{ctx.author.id}>", embed=user_embed)

    @commands.command(name="osu-set", aliases=["osuset"])
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

    @commands.command(name="osu-rs")
    async def recent(self, ctx, *user):
        user = self.get_user(user)

        async def get_username(user_):
            try:
                return osu_api.get_user({'u': user_})[0]['username']
            except IndexError:
                return "index_error"

        if user:
            try:
                user = DATABASE.child("OSU_USERS").child(mention_to_uid(user)).get().val()["user"]
            except TypeError:
                pass
        else:
            try:
                user = self.get_user(DATABASE.child("OSU_USERS").child(ctx.author.id).get().val()["user"])
            except TypeError:
                return await ctx.reply(
                    "Você não tem uma conta cadastrada, utilize `ms!osuset <user>`"
                    "ou informe qual usuario você quer pegar a play recente `ms!rs <user>`"
                )

        username = await get_username(user)
        if username == "index_error":
            return await ctx.reply(f"O usuário {user} não possui uma conta cadastrada")
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
                            f"Dificuldade: `{played_map['version']}`\n"
                            f"Score: `{recentplay['score']} •"
                            f" {recentplay['maxcombo']}/{played_map['max_combo']}`\n"
                            f"Rank: `{recentplay['rank']} • [{recentplay['count300']} - {recentplay['count100']} -"
                            f" {recentplay['count50']} - {recentplay['countmiss']}]`**",
                timestamp=parse(recentplay['date'])
            )

            rs_user_json = osu_api.get_user({"u": user})[0]
            recent_embed.set_thumbnail(
                url=f"https://b.ppy.sh/thumb/{played_map['beatmapset_id']}l.jpg"
            )
            recent_embed.set_footer(text=f"Precisão: {accuracy}%")
            recent_embed.set_author(icon_url=f"https://a.ppy.sh/{rs_user_json['user_id']}",
                                    name=f"Play recente do(a) {username}")

            await ctx.reply(content=f"<@{ctx.author.id}>", embed=recent_embed)


class OsuDroid(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.missing_uid_msg = "Você esqueceu de por a `<uid>` do usuário!" \
                               " você também pode setar seu usuário com `ms!droidset <user>`"

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)
        self._brdpp_rank.start()

    @commands.command(name="rs", aliases=["recentme"])
    async def droidrecent(self, ctx, uid=None):
        """
        Veja sua play mais recente do osu!droid, ou a de outro jogador
        se você passar o paramêtro de <uid>, ms!rs <uid>
        """

        uid_original = uid

        if uid is None:
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception as e:
                print(e)
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()
        try:
            _droid_data = await get_droid_data(uid)
        except IndexError:
            return await ctx.reply(f"Não existe essa uid ou o usuário não se cadastrou: {mention_to_uid(uid_original)}")
        try:
            rs_data = _droid_data["beatmap_data"]["rs_0"]
        except KeyError:
            await ctx.reply(f"O usuário infelizmente não possui nenhuma play, ghost de...")
        else:
            rs_embed = discord.Embed(timestamp=rs_data["date"].replace(tzinfo=timezone("Africa/Algiers")))
            rs_embed.set_author(
                name=f"Play recente do(a) {rs_data['username']}",
                icon_url=_droid_data["user_data"]["avatar_url"],
                url=f"http://ops.dgsrz.com/profile.php?uid={uid}"
            )

            rs_embed.set_footer(text="Play feita")

            mod_dict = {
                "None": "NM",
                "Hidden": "HD",
                "DoubleTime": "DT",
                "HardRock": "HR",
                "Precise": "PR"
            }

            mod_list = [mod_dict[mod.strip()] for mod in rs_data["mods"].split(",")]
            mods = "".join(mod_list)

            rs_embed.add_field(name="Dados da play", value="**"
                                                           f"Beatmap: `{rs_data['beatmap']}`\n"
                                                           f"Precisão: `{rs_data['accuracy']}%`\n"
                                                           f"Score: `{rs_data['score']}`\n"
                                                           f"Combo: `{rs_data['combo']}x`\n"
                                                           f"Mods: `{mods}`\n"
                                                           "**")

            await ctx.reply(content=f"<@{ctx.author.id}>", embed=rs_embed)

    @commands.command(name="ppcheck")
    async def pp_check(self, ctx, uid=None):
        """
        Veja seus lindos pps do osu!droid :), ms!ppcheck <uid>,
        Lembrando que você pode cadastrar seu usuário com ms!droidset <uid>!
        Ai você não precisará passar o parâmetro de uid para ver seu usuário.
        """

        uid_original = uid

        if uid is None:
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception as e:
                print(e)
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()
        try:
            try:
                profile_data = (await get_droid_data(uid))["user_data"]
            except IndexError:
                return await ctx.reply(
                    f"Não existe uma uid ou o usuário não se cadastrou: {mention_to_uid(uid_original)}"
                )
            else:
                if profile_data == "OFFLINE":
                    return await ctx.reply(
                        "A ppboard do rian8337 está offline, logo não foi possivel obter os dados :("
                    )

            if profile_data["username"].startswith("154"):
                return await ctx.reply(
                    "Infelizmente você ou o usuário não possuem sua id cadastrada,"
                    " cadastre agora mesmo usando: `ms!droidset <uid>`"
                )

        except KeyError as e:
            print(e)
            await ctx.reply(f"Não existe uma user id chamada: {uid}")

        user_data = (await get_droid_data(uid))["user_data"]
        ppcheck_embed = discord.Embed()

        ppcheck_embed.set_author(
            name=(default_author_name := f"TOP PLAYS DO(A) {user_data['username'].upper()}"),
            url=(default_author_url := f"http://droidppboard.herokuapp.com/profile?uid={uid}"),
            icon_url=(default_icon_url := user_data["avatar_url"])
        )

        def _is_nomod(mods):
            if mods == "":
                mods = "NM"
                return mods
            else:
                return mods
        try:
            user_data["pp_data"][:5]
        except TypeError:
            return ctx.reply("O usuário não possui uma conta cadastrada!")

        message = await ctx.reply("Adiquirindo dados...")

        for _, play in enumerate(user_data["pp_data"][:5]):
            play["beatmap_data"] = (await get_beatmap_data(play["hash"]))
            if "DT" in play["mods"] or "NC" in play["mods"]:
                play["beatmap_data"]["bpm"] = int(float(play["beatmap_data"]["bpm"])) * 1.50
            user_data["pp_data"][_]['beatmap_data'] = play["beatmap_data"]
            play["mods"] = _is_nomod(play["mods"])
            ppcheck_embed.add_field(
                name=f"{_ + 1}.{play['title']} +{play['mods']}",
                value=(
                    (
                        f"```"
                        f"{play['combo']}x/{play['beatmap_data']['max_combo']}x |"
                        f" {play['accuracy']}%"
                        f" | {play['miss']} miss\n{int(float(play['pp']))}dpp |"
                        f" (aim: {float(play['beatmap_data']['diff_aim']):.2f},"
                        f" speed: {float(play['beatmap_data']['diff_speed']):.2f})"
                        f" |\nbpm: {play['beatmap_data']['bpm']}"
                        f" | diff: {float(play['beatmap_data']['difficultyrating']):.2f}★\n"
                        f"```"
                        f"\n**[Link do(a) {play['beatmap_data']['title']}](https://osu.ppy.sh"
                        f"/beatmapsets/"
                        f"{play['beatmap_data']['beatmapset_id']}#osu/"
                        f"{play['beatmap_data']['beatmap_id']})**"
                    )
                ), inline=False
            )

        ppcheck_embed.set_thumbnail(
            url=f"https://b.ppy.sh/thumb/{user_data['pp_data'][0]['beatmap_data']['beatmapset_id']}l.jpg"
        )

        await message.edit(content=f"<@{ctx.author.id}>", embed=ppcheck_embed)

        # if profile_data["raw_pp"] != "OFFLINE":
        #    _save_droid_uid_data(uid, profile_data)

        await message.add_reaction("⬅")
        await message.add_reaction("➡")

        start = 0
        end = 5

        timeout = time.time() + 60
        while time.time() < timeout:
            valid_reaction: tuple = await self.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: (
                        user == ctx.author and str(reaction.emoji) in ("⬅", "➡") and reaction.message == message
                )
            )

            if valid_reaction:
                if valid_reaction[0].emoji == "➡":
                    start += 5
                    end += 5
                else:
                    start -= 5
                    end -= 5
                if end == 0:
                    start = 70
                    end = 75
                elif end == 80:
                    start = 0
                    end = 5
                next_ppcheck_embed = discord.Embed()
                try:
                    index = start
                    for _, play in enumerate(user_data["pp_data"][start:end]):
                        index += 1
                        play["mods"] = _is_nomod(play["mods"])
                        play["beatmap_data"] = await get_beatmap_data(play["hash"])
                        if "DT" in play["mods"] or "NC" in play["mods"]:
                            play["beatmap_data"]["bpm"] = int(play["beatmap_data"]["bpm"]) * 1.50
                        
                        user_data["pp_data"][_]['beatmap_data'] = play["beatmap_data"]

                        next_ppcheck_embed.add_field(
                            name=f"{index}. {play['title']} +{play['mods']}",
                            value=(
                                (
                                    f"```"
                                    f"{play['combo']}x/{play['beatmap_data']['max_combo']}x |"
                                    f" {play['accuracy']}%"
                                    f" | {play['miss']} miss\n{int(float(play['pp']))}dpp |"
                                    f" (aim: {float(play['beatmap_data']['diff_aim']):.2f},"
                                    f" speed: {float(play['beatmap_data']['diff_speed']):.2f})"
                                    f" |\nbpm: {play['beatmap_data']['bpm']}"
                                    f" | diff: {float(play['beatmap_data']['difficultyrating']):.2f}★\n"
                                    f"```"
                                    f"\n**[Link do(a) {play['beatmap_data']['title']}](https://osu.ppy.sh"
                                    f"/beatmapsets/"
                                    f"{play['beatmap_data']['beatmapset_id']}#osu/"
                                    f"{play['beatmap_data']['beatmap_id']})**"
                                )
                            ), inline=False
                        )
                    next_ppcheck_embed.set_thumbnail(
                        url=f"https://b.ppy.sh/thumb/"
                            f"{user_data['pp_data'][index - 5]['beatmap_data']['beatmapset_id']}l.jpg"
                    )
                except (IndexError, KeyError) as e:
                    print(e)

                next_ppcheck_embed.set_author(name=default_author_name,
                                              url=default_author_url,
                                              icon_url=default_icon_url)

                await message.edit(embed=next_ppcheck_embed)
        return await message.clear_reactions()

    @commands.command(name="pf", aliases=["pfme"])
    async def droid_pfme(self, ctx, uid=None):
        """
        Veja seu lindo perfil do osu!droid,
        ou o perfil de outra pessoa.
        """

        uid_original = uid

        if uid is None:
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception as e:
                print(e)
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()
        try:
            try:
                profile_data = (await get_droid_data(uid))["user_data"]
            except IndexError:
                return await ctx.reply(
                    f"Não existe uma uid ou o usuário não se cadastrou: {mention_to_uid(uid_original)}")
            # if profile_data["username"] == "153460":
            #    return await ctx.reply(f"Não existe uma uid chamada: {uid}")
            profile_embed = discord.Embed()

            if profile_data["username"].startswith("154"):
                return await ctx.reply(
                    "Infelizmente você ou o usuário não possuem sua id cadastrada,"
                    " cadastre agora mesmo usando: `ms!droidset <uid>`"
                )

            try:
                raw_pp = int(profile_data["raw_pp"])
            except ValueError:
                raw_pp = "OFFLINE"

            profile_embed.set_thumbnail(url=profile_data['avatar_url'])
            profile_embed.set_author(url=f"http://ops.dgsrz.com/profile.php?uid={uid}",
                                     name=f"Perfil do(a) {profile_data['username']}")

            profile_embed.add_field(name="---Performance", value="**"
                                                                 f"Ele(a) é do(a)"
                                                                 f" {(user_country := profile_data['country'])}"
                                                                 f"(:flag_{user_country.lower()}:)\n"
                                                                 f"Total score: `{profile_data['total_score']}`\n"
                                                                 f"Total dpp: `{raw_pp}`\n"
                                                                 f"Overall acc: `{profile_data['overall_acc']}%`\n"
                                                                 f"Playcount: `{profile_data['playcount']}`"
                                                                 "**")
            await ctx.reply(content=f"<@{ctx.author.id}>", embed=profile_embed)

        except KeyError as e:
            print(e)
            await ctx.reply(f"Não existe uma user id chamada: {uid}")

    @commands.command(name="droidset")
    async def droid_set(self, ctx, uid=None):

        if not uid:
            return await ctx.reply("Você esqueceu de por para qual usuário(a) você quer setar!")

        user_data = (await get_droid_data(uid))["user_data"]

        if user_data["username"] != "153456":
            DATABASE.child("DROID_USERS").child(ctx.author.id).set({"user": user_data})
        else:
            return await ctx.reply(f"Não existe uma uid chamada: {uid}")

        droidset_embed = discord.Embed(
            title=f"Você cadastrou seu usuário! {user_data['username']}"
        )

        droidset_embed.set_image(url=user_data["avatar_url"])

        await ctx.reply(f"<@{ctx.author.id}>", embed=droidset_embed)

    @tasks.loop(minutes=30, seconds=0)
    async def _brdpp_rank(self):

        if debug:
            return None

        try:
            br_rank_channel: discord.TextChannel = self.bot.get_channel(789613566684430346)
            br_rank_message: discord.Message = await br_rank_channel.fetch_message(789691247911632956)
        except AttributeError:
            return print("Erro ao atualizar o rank de dpp")

        fetched_data = []

        uid_list = DATABASE.child("BR_UIDS").get().val()["uids"]

        for user in uid_list:

            diff_aim_list = []
            diff_speed_list = []
            diff_ar_list = []

            await asyncio.sleep(0.5)
            user_data = (await get_droid_data(user))["user_data"]

            if user_data["raw_pp"] is not None or user_data["pp_data"] is not None:

                for top_play in user_data["pp_data"]:

                    beatmap_data = await get_beatmap_data(top_play["hash"])

                    if "DT" not in top_play["mods"]:
                        diff_ar_list.append(float(beatmap_data["diff_approach"]))
                        diff_aim_list.append(float(beatmap_data["diff_aim"]))
                        diff_speed_list.append(float(beatmap_data["diff_speed"]))
                    else:
                        diff_ar_list.append((float(beatmap_data["diff_approach"]) * 2 + 13) / 3)
                        diff_aim_list.append(float(beatmap_data["diff_aim"]) * 1.50)
                        diff_speed_list.append(float(beatmap_data["diff_speed"]) * 1.50)

                to_calculate = [
                    diff_ar_list,
                    diff_speed_list,
                    diff_aim_list
                ]

                calculated = []

                res = None

                for calc_list in to_calculate:
                    try:
                        res = sum(calc_list) / len(calc_list)
                    except ZeroDivisionError:
                        res = 0
                    finally:
                        calculated.append(res)

                user_data["reading"] = calculated[0]
                user_data["speed"] = calculated[1]
                user_data["aim"] = calculated[2]

                fetched_data.append(user_data)

        fetched_data = fetched_data[:25]
        fetched_data.sort(key=lambda e: e["raw_pp"], reverse=True)

        updated_data = discord.Embed(title="RANK DPP BR", timestamp=datetime.utcnow())
        updated_data.set_footer(text="Atualizado")

        for i, data in enumerate(fetched_data):
            updated_data.add_field(
                name=f"{i + 1} - {data['username']}",
                value=(
                    f">>> ```\n{float(data['raw_pp']):.2f}pp - accuracy: {data['overall_acc']:.2f}%\n"
                    f"[speed: {data['speed']:.2f} | aim: {data['aim']:.2f} | reading: AR{data['reading']:.2f}]\n```"
                ),
                inline=False
            )

        # noinspection PyBroadException

        try:
            return await br_rank_message.edit(content="", embed=updated_data)
        except Exception:
            return await br_rank_channel.send("Não foi possivel encontrar a mensagem do rank dpp")


def setup(bot):
    bot.add_cog(OsuGame(bot))
    bot.add_cog(OsuDroid(bot))
