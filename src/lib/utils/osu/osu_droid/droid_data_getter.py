from datetime import datetime, timedelta
from typing import Dict

import requests
from bs4 import BeautifulSoup

from src.setup import DPPBOARD_API as DPP_BOARD_API

import aiohttp
from json.decoder import JSONDecodeError


class OsuDroidProfile:
    def __init__(self, uid: int, needs_player_html: bool = False, needs_pp_data: bool = False):
        self.needs_player_html = needs_player_html,
        self.needs_pp_data = needs_pp_data

        self.uid = uid
        self._user_pp_data_json = None
        self._player_html = None
        self._stats = None

    async def setup(self):
        async with aiohttp.ClientSession() as session:
            if self.needs_player_html:
                url = f"http://ops.dgsrz.com/profile.php?uid={self.uid}"
                async with session.get(url) as res:
                    self._player_html = BeautifulSoup(await res.text(), features="html.parser")
                    self._stats = list(map(lambda a: a.text,
                                           self._player_html.find_all("span", class_="pull-right")[-5:]))
            if self.needs_pp_data:
                url = f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}"
                async with session.get(url) as res:
                    try:
                        self._user_pp_data_json = (await res.json(content_type='text/html'))['data']
                    except JSONDecodeError:
                        self._user_pp_data_json = {
                            "uid": 0,
                            "username": "None",
                            "list": []
                        }

    @staticmethod
    def _replace_mods(modstring: str):
        modstring = modstring.replace("DoubleTime", "DT").replace(
            "Hidden", "HD").replace("HardRock", "HR").replace(
            "Hidden", "HD").replace("HardRock", "HR").replace(
            "Precise", "PR").replace("NoFail", "NF").replace(
            "Easy", "EZ").replace("NightCore", "NC").replace(
            "Precise", "PR").replace("None", "NM").replace(",", "").strip().replace(" ", "")

        if modstring == "":
            modstring = "NM"

        return modstring

    @staticmethod
    def _handle_rank(rank_src) -> Dict[str, str]:
        rank_url: str = f"http://ops.dgsrz.com/{rank_src}"
        rank_str: str = rank_src.split("/")[-1].split("-")[-2]

        return {
            "rank_url": rank_url,
            "rank_str": rank_str
        }

    # I probably will make everything here acessible through a class later
    def get_play_data(self, play_html):
        play = play_html

        title = play.find("strong", class_="block").text

        rank_data = self._handle_rank(play.find("img")['src'])
        rank_str = rank_data['rank_str']
        rank_url = rank_data['rank_url']

        stats = list(map(lambda a: a.strip(), play.find("small").text.split("/")))
        date = datetime.strptime(stats[0], '%Y-%m-%d %H:%M:%S') - timedelta(hours=1)
        score = stats[1]
        mods = self._replace_mods(stats[2])

        combo = stats[3]
        accuracy = stats[4]

        hidden_data = list(map(lambda a: a.strip().split(":")[1].replace("}", ""),
                               play.find("span", class_="hidden").text.split(",")))

        misscount = hidden_data[0]
        hash_ = hidden_data[1]

        return {
            "title": title,
            "score": score,
            "mods": mods,
            "combo": combo,
            "accuracy": accuracy,
            "misscount": misscount,
            "date": date,
            "hash": hash_,
            "rank_str": rank_str,
            "rank_url": rank_url
        }

    @property
    def profile(self):

        return {
            "username": self.username,
            "avatar_url": self.avatar,
            "rankscore": self.rankscore,
            "raw_pp": self.total_pp,
            "country": self.country,
            "total_score": self.score,
            "overall_acc": self.acc,
            "playcount": self.playcount,
            "user_id": self.uid
        }

    @property
    def score(self):
        score = self._stats[0]
        return score

    @property
    def acc(self):
        accuracy = self._stats[1]
        return accuracy

    @property
    def playcount(self):
        playcount = self._stats[2]
        return playcount

    @property
    def username(self):
        username = self._player_html.find("div", class_="h3 m-t-xs m-b-xs").text
        return username

    @property
    def rankscore(self):
        rankscore = self._player_html.find("span", class_="m-b-xs h4 block").text
        return rankscore

    @property
    def avatar(self):
        avatar = self._player_html.find("a", class_="thumb-lg").find("img")['src']
        return avatar

    @property
    def country(self):
        country = self._player_html.find("small", class_="text-muted").text
        return country

    @property
    def basic_user_data(self):
        data = self._user_pp_data_json

        return {
            "uid": data['uid'],
            "username": data['username']
        }

    @property
    def pp_data(self):
        try:
            data = (raw_data := self._user_pp_data_json)['pp']
        except KeyError:
            return {
                "uid": 0,
                "username": "None",
                "list": []
            }

        data['uid'] = raw_data['uid']
        data['username'] = raw_data['username']
        data['list'] = [{**d, **{"mods": self._replace_mods(d['mods'])}} for d in data['list']]

        return data

    @property
    def total_pp(self):

        total_pp = 0
        try:
            data = self._user_pp_data_json
        except (KeyError, AttributeError, TypeError):
            pass
        else:
            total_pp = data["pp"]["total"]
        finally:
            return total_pp

    @property
    def best_play(self):
        data = self._user_pp_data_json

        return data["pp"]["list"][0]

    @property
    def recent_play(self):
        recent_play = {}
        status_code = 200
        try:
            recent_play = self.get_play_data(BeautifulSoup(requests.get(
                f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                                           ).find("li", class_="list-group-item"))
        except (IndexError, KeyError, AttributeError):
            status_code = 400
        else:
            recent_play['mods'] = self._replace_mods(recent_play['mods'])
        finally:
            recent_play['code'] = status_code

        return recent_play

    @property
    def recent_plays(self):
        unfiltered_recent_plays = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                                ).find_all("li", class_="list-group-item")

        recent_plays = []
        for play in unfiltered_recent_plays:
            try:
                play_data = self.get_play_data(play)
            except AttributeError:
                pass
            else:
                recent_plays.append(play_data)
        return recent_plays
