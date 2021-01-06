import asyncio
import time
from datetime import datetime

import discord
import requests
from dateutil.parser import parse
from discord.ext import commands, tasks

from src.lib.utils.basic_utils import ready_up_cog
from src.lib.utils.osu.osu_droid.br_pp_calculator import get_bpp
from src.lib.utils.osu.osu_droid.droid_data_getter import OsuDroidProfile
from src.paths import debug
from src.setup import DATABASE
from src.setup import OSU_API
from src.setup import OSU_API_KEY
from json.decoder import JSONDecodeError


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
        beatmap_data = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OSU_API_KEY}&h={hash_}").json()
    except Exception:
        beatmap_data = default_data
    else:
        try:
            beatmap_data = beatmap_data[0]
        except IndexError:
            beatmap_data = default_data

    return beatmap_data


def is_beatmap_valid(beatmap_json):
    if beatmap_json["title"] == "?":
        return False
    else:
        return True


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
        # user_json = OSU_API.get_user({"u": user})[0]

        if user:
            user = self.get_user(mention_to_uid(user))
            try:
                user_json = OSU_API.get_user({"u": DATABASE.child("OSU_USERS").get().val()[user]["user"]})
            except KeyError:
                user_json = OSU_API.get_user({"u": user})

                if user_json == []:
                    return await ctx.reply("Não foi possivel encontrar o usuário!")
        else:
            try:
                user_json = \
                    OSU_API.get_user({"u": DATABASE.child("OSU_USERS").child(ctx.author.id).get().val()["user"]})[0]
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

        profile_best_play = OSU_API.get_user_best({"u": user_json['user_id']})[0]
        played_beatmap_profile = OSU_API.get_beatmaps({"b": profile_best_play["beatmap_id"]})[0]

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
            set_user_json = OSU_API.get_user({"u": user})[0]
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
                return OSU_API.get_user({'u': user_})[0]['username']
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
            recentplay = OSU_API.get_user_recent({"u": user})[0]
        except IndexError:
            await ctx.reply(f"O {username} não possui nenhuma play recente :(")
        else:
            played_map = OSU_API.get_beatmaps({"b": recentplay["beatmap_id"]})[0]
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

            rs_user_json = OSU_API.get_user({"u": user})[0]
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

        if uid is None:
            # noinspection PyBroadException
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception:
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()
        user = OsuDroidProfile(uid)
        try:
            rs_data = user.recent_play
        except (IndexError, KeyError):
            await ctx.reply(f"O usuário infelizmente não possui nenhuma play ou o mesmo não possui uma conta...")
        else:
            rs_bm_data = await get_beatmap_data(rs_data["hash"])

            rs_embed = discord.Embed()
            rs_embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{rs_bm_data['beatmapset_id']}l.jpg")

            if is_beatmap_valid(rs_bm_data):
                play_bpp = get_bpp(int(rs_bm_data['beatmap_id']), rs_data['mods'],
                                   int(rs_data['misscount']), float(rs_data['accuracy'][:-1]),
                                   int(rs_data['combo'][:-1]),
                                   True)['raw_pp']
                max_bpp = get_bpp(int(rs_bm_data['beatmap_id']), rs_data['mods'], formatted=True)['raw_pp']

                bm_data_string = (">>> **"
                                  f"CS/OD/AR/HP:"
                                  f" {rs_bm_data['diff_size']}/{rs_bm_data['diff_overall']}/"
                                  f"{rs_bm_data['diff_approach']}/{rs_bm_data['diff_drain']}\n"
                                  "**")
            else:
                play_bpp = 0
                max_bpp = 0
                bm_data_string = "> Não foi possivel encontrar o beatmap nos servidores do osu..."

            rs_embed.add_field(
                name=f"Dados da play do(a) {user.profile['username']}",
                value=">>> **"
                      f"BPP: {play_bpp}/{max_bpp}\n"
                      f"Precisão: {rs_data['accuracy']}\n"
                      f"Score: {rs_data['score']}\n"
                      f"Combo: {rs_data['combo']} / {rs_bm_data['max_combo']}x\n"
                      f"Misses: {rs_data['misscount']}"
                      "**"
            )

            rs_embed.add_field(
                name="Dados do beatmap",
                value=bm_data_string
            )

            rs_embed.set_author(
                name=f"{rs_data['title']} +{rs_data['mods']} - {float(rs_bm_data['difficultyrating']):.2f}★",
                url=f"https://osu.ppy.sh/b/{rs_bm_data['beatmap_id']}",
                icon_url=user.profile['avatar_url']
            )

            await ctx.reply(content=f"<@{ctx.author.id}>", embed=rs_embed)

    # noinspection PyBroadException
    @commands.command(name="ppcheck")
    async def pp_check(self, ctx, uid=None):
        faster = False

        def get_default_ppmsg(play_dict: dict):
            return (
                f">>> ```\n"
                f"| {play_dict['combo']}x |"
                f" {play_dict['accuracy']}%"
                f" | {play_dict['miss']} miss | {int(float(play_dict['pp']))}dpp |"
                f"```"
            )

        uid_original = uid

        if uid is None:
            # noinspection PyBroadException
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception:
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()
        user = OsuDroidProfile(uid)

        if uid == "+":
            faster = True
        not_registered_msg = "Você não possui uma conta registrada na database" \
                             " ou você esqueceu de submitar seus pp's use `&pp` ou `&bind uid>`" \
                             "Para os respectivos erros."

        if faster is True:
            try:
                pp_data = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("pp_data").get().val()
            except Exception:
                return await ctx.reply(not_registered_msg)
        else:
            try:
                pp_data = user.pp_data
            except KeyError:
                return await ctx.reply(f"Não existe uid: {uid_original}, cadastrada na alice, Ok?")

        ppcheck_embed = discord.Embed()

        try:
            ppcheck_embed.set_author(
                name=(default_author_name := f"TOP PLAYS DO(A) {pp_data['username'].upper()}"),
                url=(default_author_url := f"http://droidppboard.herokuapp.com/profile?uid={uid}"),
            )
        except TypeError:
            return await ctx.reply(not_registered_msg)

        for i, play in enumerate((pp_data := pp_data['list'])[:5]):
            ppcheck_embed.add_field(
                name=f"{i + 1}. {play['title']} +{play['mods']}",
                value=get_default_ppmsg(play), inline=False
            )

        message = await ctx.reply(content=f"<@{ctx.author.id}>", embed=ppcheck_embed)

        await message.add_reaction("⬅")
        await message.add_reaction("➡")

        start = 0
        end = 5

        timeout = time.time() + 120
        while time.time() < timeout:
            valid_reaction: tuple = await self.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user_: (
                        user_ == ctx.author and str(reaction.emoji) in ("⬅", "➡") and reaction.message == message
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

                index = start
                for i, play in enumerate(pp_data[start:end]):
                    index += 1

                    next_ppcheck_embed.add_field(
                        name=f"{index}. {play['title']} +{play['mods']}",
                        value=get_default_ppmsg(play), inline=False
                    )

                next_ppcheck_embed.set_author(name=default_author_name,
                                              url=default_author_url,
                                              )
                await message.edit(embed=next_ppcheck_embed)
        return await message.clear_reactions()

    @commands.command(name="pp")
    async def submit_pp(self, ctx: commands.Context):
        """
        Submita o seu ppcheck atual para a database :)
        """
        # noinspection PyBroadException
        try:
            uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
        except Exception:
            return await ctx.reply("Você não tem uma conta cadastrada no bot, faça o mesmo com: `&bind <uid>`")
        else:
            try:
                user = OsuDroidProfile(uid)
                DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("pp_data").set(user.pp_data)

                return await ctx.reply("Os seus pp's foram submitados à database com sucesso!")
            except Exception as e:
                print(e)
                return await ctx.reply("Não foi possivel submitar os seus pp's à database.")

    @commands.command(name="pf", aliases=["pfme"])
    async def droid_pfme(self, ctx, uid=None):
        """
        Veja seu lindo perfil do osu!droid,
        ou o perfil de outra pessoa.
        """

        uid_original = uid

        if uid is None:
            # noinspection PyBroadException
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception:
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()
        user = OsuDroidProfile(uid)
        try:
            try:
                dict(user.profile)
            except IndexError:
                return await ctx.reply(
                    f"Não existe uma uid ou o usuário não se cadastrou: {uid_original}")

            profile_embed = discord.Embed()
            profile_data = user.profile

            profile_embed.set_thumbnail(url=profile_data['avatar_url'])
            profile_embed.set_author(url=f"http://ops.dgsrz.com/profile.php?uid={uid}",
                                     name=f"Perfil do(a) {profile_data['username']}")

            total_dpp = f"{user.total_pp: .2f}"

            profile_embed.add_field(name="---Performance", value="**"
                                                                 f"Ele(a) é do(a)"
                                                                 f" {(user_country := profile_data['country'])}"
                                                                 f"(:flag_{user_country.lower()}:)\n"
                                                                 f"Rank: `#{profile_data['rankscore']}`\n"
                                                                 f"Total score: `{profile_data['total_score']}`\n"
                                                                 f"Total dpp: `{total_dpp}`\n"
                                                                 f"Overall acc: `{profile_data['overall_acc']}`\n"
                                                                 f"Playcount: `{profile_data['playcount']}`"
                                                                 "**")
            await ctx.reply(content=f"<@{ctx.author.id}>", embed=profile_embed)

        except KeyError:
            await ctx.reply(f"Não existe uma user id chamada: {uid}")

    @commands.command(name="droidset", aliases=["bind"])
    async def droid_set(self, ctx, uid=None):

        if not uid:
            return await ctx.reply("Você esqueceu de por para qual usuário(a) você quer setar!")
        else:
            try:
                uid = [int(s) for s in uid.split() if s.isdigit()][0]
            except IndexError:
                return await ctx.reply("O uid pode apenas conter números :(")

        user = OsuDroidProfile(uid)
        profile = user.profile

        if profile['username'] != "":
            DATABASE.child("DROID_USERS").child(ctx.author.id).set({"user": user.profile})
        else:
            return await ctx.reply(f"Não existe uma uid chamada: {uid}")

        droidset_embed = discord.Embed(
            title=f"Você cadastrou seu usuário! {profile['username']}"
        )

        droidset_embed.set_image(url=profile['avatar_url'])

        await ctx.reply(f"<@{ctx.author.id}>", embed=droidset_embed)

    @commands.command()
    async def calc(self, ctx, link: str = None, *params):
        error_message: str = f'"{link}", Não é um link ou id válido!'

        if link is None:
            return await ctx.send("Você esqueceu do link do beatmap!")
        else:
            try:
                beatmap_id: int = int(link.split("/")[-1])
            except ValueError:
                return await ctx.send(error_message)

        mods: str = "NM"
        misses: int = 0
        accuracy: float = 100.00

        parameter: str
        for parameter in params:
            if parameter.startswith("+"):
                mods = parameter[1:]
            elif parameter.startswith("-"):
                misses = int(parameter[1:])
            elif parameter.endswith("%"):
                accuracy = float(parameter[:-1])

        beatmap_pp_data = get_bpp(beatmap_id, mods, misses, accuracy)

        if len(beatmap_pp_data) == 0:
            return await ctx.send(error_message)
        else:
            beatmap_data = OSU_API.get_beatmaps({"b": beatmap_id})[0]

            calc_embed = discord.Embed()

            calc_embed.set_author(
                name=f"{beatmap_data['title']} +{mods} -{misses} {float(accuracy):.2f}%",
                url=link
            )

            calc_embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap_data['beatmapset_id']}l.jpg")

            calc_embed.add_field(name="Calculado...", value=">>> **"
                                                            f"BPP: {beatmap_pp_data['raw_pp']: .2f}\n"
                                                            f"Aim BPP: {beatmap_pp_data['aim_pp']: .2f}\n"
                                                            f"Speed BPP: {beatmap_pp_data['speed_pp']: .2f}\n"
                                                            f"Acc BPP: {beatmap_pp_data['acc_pp']: .2f}"
                                                            f"**"
                                 )
            return await ctx.reply(f"<@{ctx.author.id}>", embed=calc_embed)

    @tasks.loop(hours=1, minutes=0, seconds=0)
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

        for uid in uid_list:

            diff_aim_list, diff_speed_list, diff_ar_list, diff_size_list, combo_list = [], [], [], [], []

            await asyncio.sleep(0.5)
            user = OsuDroidProfile(uid)
            try:
                if user.total_pp is not None or user.pp_data["list"] is not None:

                    for top_play in user.pp_data['list']:
                        await asyncio.sleep(1.25)
                        beatmap_data = await get_beatmap_data(top_play["hash"])

                        combo_list.append(top_play["combo"])
                        if "DT" not in top_play["mods"]:
                            diff_ar_list.append(float(beatmap_data["diff_approach"]))
                            diff_aim_list.append(float(beatmap_data["diff_aim"]))
                            diff_speed_list.append(float(beatmap_data["diff_speed"]))
                            diff_size_list.append(float(beatmap_data["diff_size"]))
                        else:
                            diff_ar_list.append((float(beatmap_data["diff_approach"]) * 2 + 13) / 3)
                            diff_aim_list.append(float(beatmap_data["diff_aim"]) * 1.50)
                            diff_speed_list.append(float(beatmap_data["diff_speed"]) * 1.50)
                            diff_size_list.append(float(beatmap_data["diff_size"]) / 1.50)

                    to_calculate = [
                        diff_ar_list,
                        diff_speed_list,
                        diff_aim_list,
                        combo_list
                    ]

                    calculated = []

                    for calc_list in to_calculate:
                        try:
                            res = sum(calc_list) / len(calc_list)
                        except ZeroDivisionError:
                            pass
                        else:
                            calculated.append(res)

                    user_data = {"profile": user.profile, "pp_data": user.pp_data["list"], "reading": calculated[0],
                                 "speed": calculated[1], "aim": calculated[2],
                                 "consistency": calculated[3] * 100 / 6142 / 10}

                    fetched_data.append(user_data)
            except (KeyError, JSONDecodeError):
                pass
        print(fetched_data)
        fetched_data.sort(key=lambda e: e["profile"]["raw_pp"], reverse=True)
        top_players = fetched_data[:25]

        DATABASE.child("TOP_PLAYERS").child("data").set(top_players)

        updated_data = discord.Embed(title="RANK DPP BR", timestamp=datetime.utcnow())
        updated_data.set_footer(text="Atualizado")

        for i, data in enumerate(top_players):

            data['profile']['raw_pp'] = float(data['profile']['raw_pp'])
            data['profile']['overall_acc'] = float(data['profile']['overall_acc'][:-1])
            data['speed'] = float(data['speed'])
            data['aim'] = float(data['aim'])
            data['reading'] = float(data['reading'])
            data['consistency'] = float(data['consistency'])

            if len(data["pp_data"]) < 75:
                data["speed"], data["aim"], data["reading"], data["consistency"] = 0, 0, 0, 0

            updated_data.add_field(
                name=f"{i + 1} - {data['profile']['username']}",
                value=(
                    f">>> ```\n{data['profile']['raw_pp']:.2f}pp - accuracy: {data['profile']['overall_acc']:.2f}%\n"
                    f"[speed: {data['speed']:.2f} | aim: {data['aim']:.2f} | reading: AR{data['reading']:.2f}]\n"
                    f" / consistência: {data['consistency']:.2f}]\n```"
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
