import asyncio
import time
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Union

import discord
import requests
from dateutil.parser import parse
from discord.ext import commands, tasks

from src.lib.utils.basic_utils import ready_up_cog
from src.lib.utils.osu.osu_droid.droid_calculator import OsuDroidBeatmapData
from src.lib.utils.osu.osu_droid.droid_data_getter import OsuDroidProfile
from src.paths import debug
from src.setup import DATABASE
from src.setup import OSU_API
from src.setup import OSU_API_KEY


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
        await ctx.trigger_typing()

        if user:
            user = self.get_user(mention_to_uid(user))
            try:
                user_json = OSU_API.get_user({"u": DATABASE.child("OSU_USERS").get().val()[user]["user"]})
            except KeyError:
                user_json = OSU_API.get_user({"u": user})

                if len(user_json) == 0:
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
    async def osu_set(self, ctx: commands.Context, *user):
        await ctx.trigger_typing()
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
    async def recent(self, ctx: commands.Context, *user):
        await ctx.trigger_typing()
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
        self._update_pps.start()

    @commands.command(name="rs", aliases=["recentme"])
    async def droidrecent(self, ctx, uid=None):
        """
        Veja sua play mais recente do osu!droid, ou a de outro jogador
        se você passar o paramêtro de <uid>, ms!rs <uid>
        """

        await ctx.trigger_typing()
        if uid is None:
            # noinspection PyBroadException
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception:
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()

        user = OsuDroidProfile(uid, needs_player_html=True)
        await user.setup()
        rs_data = user.recent_play

        if rs_data['code'] == 400:
            await ctx.reply(f"O usuário infelizmente não possui nenhuma play ou o mesmo não possui uma conta...")
        else:
            rs_bm_data = await get_beatmap_data(rs_data["hash"])

            rs_embed = discord.Embed(color=ctx.author.color, timestamp=rs_data['date'])
            rs_embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{rs_bm_data['beatmapset_id']}l.jpg")

            if is_beatmap_valid(rs_bm_data):
                beatmap_data = OsuDroidBeatmapData(int(rs_bm_data['beatmap_id']), rs_data['mods'],
                                                   int(rs_data['misscount']), float(rs_data['accuracy'][:-1]),
                                                   int(rs_data['combo'][:-1]),
                                                   True)

                play_bpp = beatmap_data.get_bpp()['raw_pp']

                max_bpp = beatmap_data.get_bpp(max_values=True)['raw_pp']
                beatmap_stats = beatmap_data.original_diff

                bm_data_string = (
                    ">>> **"
                    "CS/OD/AR/HP:"
                    f" {beatmap_stats.cs:.2f}/"
                    f"{beatmap_stats.od:.2f}/"
                    f"{beatmap_stats.ar:.2f}/"
                    f"{beatmap_stats.hp:.2f}"
                    "**"
                )

            else:
                play_bpp = 0
                max_bpp = 0
                bm_data_string = "> Não foi possivel encontrar o beatmap nos servidores do osu..."

            rs_embed.add_field(
                name=f"Dados da play do(a) {user.username}",
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

            rs_embed.set_footer(text="\u200b", icon_url=rs_data['rank_url'])

            rs_embed.set_author(
                name=f"{rs_data['title']} +{rs_data['mods']} - {float(rs_bm_data['difficultyrating']):.2f}★",
                url=f"https://osu.ppy.sh/b/{rs_bm_data['beatmap_id']}",
                icon_url=user.avatar
            )

            await ctx.reply(content=f"<@{ctx.author.id}>", embed=rs_embed)

    # noinspection PyBroadException
    @commands.command(name="ppcheck")
    async def pp_check(self, ctx: commands.Context, uid=None, faster=None):

        await ctx.trigger_typing()
        uid_original: int = uid
        discord_id: Union[int, None] = None

        if uid is None:
            # noinspection PyBroadException
            discord_id = ctx.author.id
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception:
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            discord_id = uid_original
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()

        not_registered_msg = "O usuário ou você não possui uma conta registrada na database" \
                             " ou você esqueceu de submitar seus pp's use `&pp` ou `&bind uid>`" \
                             " Para os respectivos erros."

        if uid == "+" or faster == "+":
            discord_id = mention_to_uid(str(uid_original))
            if uid == "+":
                uid = ctx.author.id
                discord_id = ctx.author.id

            faster = True
        else:
            faster = False

        try:
            user = OsuDroidProfile(uid, needs_pp_data=True)
            await user.setup()
        except KeyError:
            return await ctx.reply("Não foi posssivel encontrar o usuário :(")

        if faster is True:
            try:
                pp_data = DATABASE.child("DROID_USERS").child(discord_id).child("user").child("pp_data").get().val()
            except Exception:
                return await ctx.reply(not_registered_msg)
            else:
                try:
                    pp_data['list'] = sorted(pp_data['list'], key=lambda item: item['bpp'], reverse=True)
                except KeyError:
                    return await ctx.reply("Ocorreu um erro ao pegar o bpp das plays do usúario!")
        else:
            try:
                pp_data = user.pp_data
            except KeyError:
                return await ctx.reply(f"Não existe uid: {uid_original}, cadastrada na alice, Ok?")
        if pp_data is None:
            return await ctx.reply(not_registered_msg)

        ppcheck_embed = discord.Embed(color=ctx.author.color)
        dpp_board_is_offline = False

        async def generate_ppcheck_embed(embed: discord.Embed, index_start: int = 0, index_end: int = 5):
            embed.set_author(
                name=f"TOP PLAYS DO(A) {pp_data['username'].upper()}",
                url=f"http://droidppboard.herokuapp.com/profile?uid={uid}",
            )

            bpp_data = False

            try:
                total_bpp = DATABASE.child(
                    "DROID_USERS"
                ).child(discord_id).child("user").child("pp_data").get().val()['total_bpp']
            except TypeError:
                total_bpp = 0.00
            else:
                bpp_data = True
            try:
                total_dpp = pp_data['total']
            except KeyError:
                nonlocal dpp_board_is_offline
                dpp_board_is_offline = True
                return await ctx.reply("O site do rian está infelizmente está offline :(")
            else:
                embed.add_field(name="\u200b", value=f">>> ```\n{total_dpp:.2f}dpp /"
                                                     f" {float(total_bpp):.2f}bpp\n```")

            for i_, play_ in enumerate(pp_data['list'][index_start:index_end]):
                if faster:
                    if bpp_data:
                        bpp_string = f"| {float(play_['bpp']):.2f}bpp - ({float(play_['net_bpp']):.2f}) |"
                    else:
                        bpp_string = "| 0bpp - (0) |"
                else:
                    bpp_string = ""

                embed.add_field(
                    name=f"{index_start + i_ + 1}. {play_['title']} +{play_['mods']}",
                    value=f">>> ```\n"
                          f"| {play_['combo']}x |"
                          f" {play_['accuracy']}%"
                          f" | {play_['miss']} miss | {int(float(play_['pp']))}dpp |\n{bpp_string}"
                          f"```", inline=False
                )

        if dpp_board_is_offline:
            return

        await generate_ppcheck_embed(ppcheck_embed, index_end=5)
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
                next_ppcheck_embed = discord.Embed(color=ctx.author.color)
                await generate_ppcheck_embed(next_ppcheck_embed, index_start=start, index_end=end)

                await message.edit(embed=next_ppcheck_embed)
        return await message.clear_reactions()

    @commands.command(name="completecalc", aliases=["pp"])
    async def submit_pp(self, ctx: commands.Context, user: discord.Member = None):

        """
        Submita o seu ppcheck atual para a database :)
        """

        await ctx.trigger_typing()

        user_to_submit = ctx.author.id
        submit_string: str = "O seu pp sera submitado à database em até 1 hora!"
        succesful_msg: str = "O seu pp foi submitado com sucesso!"
        fail_msg: str = "Não foi possível submitar seu pp!"
        if dict(ctx.author.guild_permissions)['administrator'] is True:
            if user is not None:
                user_to_submit = user.id
                submit_string = "O pp dele será submitado à database em até 1 hora!"
                succesful_msg = "O pp dele foi submitado com sucesso!"
                fail_msg = "Não foi possivel submitar o pp dele!"

        # noinspection PyBroadException
        try:
            uid = DATABASE.child("DROID_USERS").child(user_to_submit).child("user").child("user_id").get().val()
        except Exception:
            return await ctx.reply("Você não tem uma conta cadastrada no bot, faça o mesmo com: `&bind <uid>`")
        else:
            await ctx.reply(submit_string)
            # noinspection PyBroadException
            try:
                await self.submit_user_data(uid, user_to_submit, 36)
            except Exception:
                return await ctx.reply(fail_msg)
            else:
                return await ctx.reply(succesful_msg)

    @staticmethod
    async def submit_user_data(uid: int, discord_id: Union[int, str], sleep_time: float = 12):
        try:
            user = OsuDroidProfile(uid, needs_pp_data=True)
            await user.setup()
        except KeyError:
            return

        pp_data = user.pp_data

        for play in pp_data['list']:
            await asyncio.sleep(sleep_time)
            try:
                beatmap_data = OsuDroidBeatmapData((await get_beatmap_data(play['hash']))['beatmap_id'],
                                                   mods=play['mods'],
                                                   misses=play['miss'],
                                                   accuracy=play['accuracy'],
                                                   max_combo=play['combo']
                                                   )
            except KeyError:
                play['bpp'] = 0
                play['diff'] = {"diff_approach": 0, "diff_drain": 0, "diff_size": 0, "diff_overall": 0}
            else:
                play['bpp'] = beatmap_data.get_bpp()['raw_pp']

                raw_data = beatmap_data.data

                ar = raw_data.ar
                cs = raw_data.cs
                hp = raw_data.hp
                od = raw_data.od

                play['diff'] = {"diff_approach": ar, "diff_drain": hp, "diff_size": cs, "diff_overall": od}

        pp_data['total_bpp'] = 0
        for i, play in enumerate(pp_data['list']):
            play_bpp = play['bpp']
            play['net_bpp'] = play_bpp * 0.95 ** i
            pp_data['total_bpp'] += play['net_bpp']

        DATABASE.child("DROID_UID_DATA").child(uid).set(pp_data)
        DATABASE.child("DROID_USERS").child(discord_id).child("user").child("pp_data").set(pp_data)

        return pp_data

    @commands.command(name="pf", aliases=["pfme", "pfid"])
    async def droid_pfme(self, ctx, uid=None):
        """
        Veja seu lindo perfil do osu!droid,
        ou o perfil de outra pessoa.
        """

        await ctx.trigger_typing()
        uid_original = uid

        if uid is None:
            # noinspection PyBroadException
            try:
                uid = DATABASE.child("DROID_USERS").child(ctx.author.id).child("user").child("user_id").get().val()
            except Exception:
                return await ctx.reply(self.missing_uid_msg)
        elif len(uid) >= 9:
            uid = DATABASE.child("DROID_USERS").child(mention_to_uid(uid)).child("user").child("user_id").get().val()
        try:
            user = OsuDroidProfile(uid, needs_player_html=True, needs_pp_data=True)
            await user.setup()
        except KeyError:
            return await ctx.reply("Não foi possível encontrar este usuário!")
        else:
            profile_embed = discord.Embed(color=ctx.author.color)

            profile_embed.set_thumbnail(url=user.avatar)
            profile_embed.set_author(url=f"http://ops.dgsrz.com/profile.php?uid={uid}",
                                     name=f"Perfil do(a) {user.username}")

            total_bpp = DATABASE.child('DROID_USERS').child(uid_original).child('total_bpp').get().val()
            if total_bpp is None:
                total_bpp = 0

            user_country = user.country
            profile_embed.add_field(name="---Performance", value="**"
                                                                 f"Ele(a) é do(a)"
                                                                 f" {user_country}"
                                                                 f"(:flag_{user_country.lower()}:)\n"
                                                                 f"Rank: #{user.rankscore}\n"
                                                                 f"Total score: {user.score}\n"
                                                                 f"Total DPP: {user.total_pp:.2f}\n"
                                                                 f"Total BPP: {total_bpp:.2f}\n"
                                                                 f"Overall acc: {user.acc}\n"
                                                                 f"Playcount: {user.playcount}"
                                                                 "**")
            await ctx.reply(content=f"<@{ctx.author.id}>", embed=profile_embed)

    @commands.command(name="droidset", aliases=["bind"])
    async def droid_set(self, ctx, uid: Union[str, int] = None, discord_user: Union[discord.Member, str] = None):
        await ctx.trigger_typing()

        user_to_bind: Union[str, int, discord.Member] = ctx.author.id
        if dict(ctx.author.guild_permissions)['administrator'] is True:
            if discord_user is not None:
                user_to_bind = discord_user
        if not uid:
            return await ctx.reply("Você esqueceu de por para qual usuário(a) você quer setar!")
        else:
            try:
                uid = [int(s) for s in uid.split() if s.isdigit()][0]
            except IndexError:
                return await ctx.reply("O uid pode apenas conter números :(")
        user = OsuDroidProfile(uid, needs_player_html=True)
        await user.setup()
        
        if type(user_to_bind) == discord.Member:
            user_to_bind = user_to_bind.id
        else:
            try:
                user_to_bind = int(user_to_bind)
            except ValueError:
                return await ctx.reply("O id precisa ser um íntegro!")

        username = user.username
        if user_to_bind == ctx.author.id:
            bind_msg = f"Você cadastrou seu usuário! {username}"
        else:
            user_to_bind = ctx.guild.get_member(user_to_bind)

            if type(user_to_bind) != discord.Member:
                bind_msg_user = "ele(a)"
            else:
                bind_msg_user = user_to_bind.display_name
                user_to_bind = user_to_bind.id

            bind_msg = f"O adm cadastrou o(a) {username} pro(a) {bind_msg_user}"
        if username != "":
            DATABASE.child("DROID_USERS").child(user_to_bind).set({"user": user.profile})
        else:
            return await ctx.reply(f"Não existe uma uid chamada: {uid}")

        droidset_embed = discord.Embed(title=bind_msg, color=ctx.author.color)
        droidset_embed.set_image(url=user.avatar)

        await ctx.reply(f"<@{ctx.author.id}>", embed=droidset_embed)

    @commands.command()
    async def calc(self, ctx: commands.Context, link: str = None, *params):
        await ctx.trigger_typing()
        error_message: str = f'"{link}", Não é um link ou id válido!'

        if link is None:
            return await ctx.reply("Você esqueceu do link do beatmap!")
        else:
            try:
                beatmap_id: int = int(link.split("/")[-1])
            except ValueError:
                return await ctx.reply(error_message)

        mods: str = "NM"
        misses: int = 0
        accuracy: float = 100.00
        speed: float = 1.00

        parameter: str
        for parameter in params:
            if parameter.startswith("+"):
                mods = parameter[1:]
            elif parameter.startswith("-"):
                misses = int(parameter[1:])
            elif parameter.endswith("%"):
                accuracy = float(parameter[:-1])
            elif parameter.endswith("s"):
                speed = float(parameter[:-1])
        try:
            beatmap_data = OsuDroidBeatmapData(beatmap_id, mods, misses, accuracy, custom_speed=speed)
        except AttributeError:
            return await ctx.reply(error_message)
        else:
            beatmap_pp_data = beatmap_data.get_bpp()
            beatmap_diff_data = beatmap_data.original_diff
            raw_beatmap_data = beatmap_data.data

            calc_embed = discord.Embed(color=ctx.author.color)

            title = raw_beatmap_data.title

            calc_embed.set_author(
                name=f"{title} +{mods} -{misses} {float(accuracy):.2f}% {speed}x",
                url=link
            )

            calc_embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap_id}l.jpg")

            cs = beatmap_diff_data.cs
            od = beatmap_diff_data.od
            ar = beatmap_diff_data.ar
            hp = beatmap_diff_data.hp

            calc_embed.add_field(name="Dados de BPP", value=">>> **"
                                                            f"BPP: {beatmap_pp_data['raw_pp']: .2f}\n"
                                                            f"Aim BPP: {beatmap_pp_data['aim_pp']: .2f}\n"
                                                            f"Speed BPP: {beatmap_pp_data['speed_pp']: .2f}\n"
                                                            f"Acc BPP: {beatmap_pp_data['acc_pp']: .2f}"
                                                            f"**"
                                 )

            calc_embed.add_field(name="Dados do beatmap", value=">>> **"
                                                                f"CS/OD/AR/HP:\n {cs:.2f}/{od:.2f}/{ar:.2f}/{hp:.2f}"
                                                                f"**")

            return await ctx.reply(f"<@{ctx.author.id}>", embed=calc_embed)

    @tasks.loop(hours=24)
    async def _update_pps(self):
        if debug:
            return None

        discord_ids: list = list((pp_datas := DATABASE.child("DROID_USERS").get().val()))

        for uid in discord_ids:
            try:
                await self.submit_user_data(pp_datas[uid]['user']['user_id'], uid, sleep_time=12)
            except JSONDecodeError:
                pass

    @tasks.loop(hours=1)
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
            bpp_aim_list, bpp_speed_list, diff_ar_list = [], [], []

            print(uid)

            try:
                raw_user_data = OsuDroidProfile(uid, needs_player_html=True, needs_pp_data=True)
                await raw_user_data.setup()
            except KeyError:
                continue

            db_user_data = DATABASE.child("DROID_UID_DATA").child(uid).get().val()

            try:
                top_plays = db_user_data['list']
            except (KeyError, TypeError):
                try:
                    top_plays = raw_user_data.pp_data['list']
                except KeyError:
                    continue

                for x in top_plays:
                    x['bpp'], x['net_bpp'] = 0, 0

            try:
                for top_play in top_plays:
                    # Sleep = loop_time * 1.50 if 30 UIDS or less
                    await asyncio.sleep(1.5)

                    beatmap_data = OsuDroidBeatmapData((
                        (await get_beatmap_data(top_play["hash"]))['beatmap_id']
                    ), mods=top_play['mods'], misses=top_play['miss'],
                        accuracy=top_play['accuracy'], max_combo=top_play['combo'],
                        formatted=True, custom_speed=1.00
                    )

                    beatmap_bpp_data = beatmap_data.get_bpp()

                    bpp_aim_list.append(float(beatmap_bpp_data['aim_pp']))
                    bpp_speed_list.append(float(beatmap_bpp_data["speed_pp"]))

                    diff_ar_list.append((float(beatmap_data.data.ar)))

                to_calculate = [
                    diff_ar_list,
                    bpp_speed_list,
                    bpp_aim_list,
                ]

                calculated = []

                for calc_list in to_calculate:
                    try:
                        res = sum(calc_list) / len(calc_list)
                    except ZeroDivisionError:
                        pass
                    else:
                        calculated.append(res)

                total_bpp = 0
                if db_user_data is not None:
                    try:
                        total_bpp = db_user_data['total_bpp']
                    except KeyError:
                        pass
                try:
                    user_data = {
                        "profile": raw_user_data.profile,
                        "total_bpp": total_bpp,
                        "pp_data": top_plays,
                        "reading": calculated[0],
                        "speed": calculated[1],
                        "aim": calculated[2],
                    }
                except IndexError:
                    print("ERRO " + str(uid))
                    pass
                else:
                    fetched_data.append(user_data)
            except (KeyError, JSONDecodeError):
                pass

        print(fetched_data)

        fetched_data.sort(key=lambda e: e['profile']['raw_pp'], reverse=True)
        top_players = fetched_data[:25]

        DATABASE.child("TOP_PLAYERS").child("data").set(top_players)

        updated_data = discord.Embed(title="RANK DPP BR", timestamp=datetime.utcnow(), color=self.bot.user.color)
        updated_data.set_footer(text="Atualizado")

        for i, data in enumerate(top_players):

            data['profile']['raw_pp'] = float(data['profile']['raw_pp'])
            data['total_bpp'] = float(data['total_bpp'])
            data['profile']['overall_acc'] = float(data['profile']['overall_acc'][:-1])
            data['speed'] = float(data['speed'])
            data['aim'] = float(data['aim'])
            data['reading'] = float(data['reading'])

            if len(data["pp_data"]) < 75:
                data["speed"], data["aim"], data["reading"], data["consistency"] = 0, 0, 0, 0

            updated_data.add_field(
                name=f"{i + 1} - {data['profile']['username']}",
                value=(
                    f">>> ```\n{data['profile']['raw_pp']:.2f}dpp - {data['total_bpp']:.2f}bpp\n"
                    f" accuracy: {data['profile']['overall_acc']:.2f}% - rankscore: #{data['profile']['rankscore']}\n"
                    f""
                    f"[speed: {data['speed']:.2f} |"
                    f" aim: {data['aim']:.2f} |"
                    f" reading: AR{data['reading']:.2f}]"
                    f"\n"
                    f"```"
                    f""
                    # f" consistência: {data['consistency']:.2f}]"
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
