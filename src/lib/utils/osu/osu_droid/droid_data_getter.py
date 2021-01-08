import requests
from bs4 import BeautifulSoup

from src.setup import DPPBOARD_API as DPP_BOARD_API


class OsuDroidProfile:
    def __init__(self, uid: int):
        self.uid = uid

    @staticmethod
    def _replace_mods(modstring: str):
        modstring = modstring.replace("DoubleTime", "DT").replace(
            "Hidden", "HD").replace("HardRock", "HR").replace(
            "Precise", "PR").replace("NoFail", "NF").replace(
            "Easy", "EZ").replace("NightCore", "NC").replace(
            "Precise", "PR").replace(",", "").strip().replace(" ", "")

        if modstring == "":
            modstring = "NM"

        return modstring

    def get_play_data(self, play_html):
        play = play_html

        title = play.find("strong", attrs={"class": "block"}).text
        stats = list(map(lambda a: a.strip(), play.find("small").text.split("/")))
        date = stats[0]
        score = stats[1]
        mods = self._replace_mods(stats[2])

        combo = stats[3]
        accuracy = stats[4]

        hidden_data = list(map(lambda a: a.strip().split(":")[1].replace("}", ""),
                               play.find("span", attrs={"class": "hidden"}).text.split(",")))

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
            "hash": hash_
        }

    @property
    def profile(self):
        profile_info = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                     )
        stats = list(map(lambda a: a.text, profile_info.find_all("div", attrs={"class": "panel"})[1].find_all(
            "span", attrs={"class": "pull-right"})[:3]))
        username = profile_info.find_all("section", attrs={"class": "scrollable"}
                                         )[1].find("div", attrs={"class": "h3 m-t-xs m-b-xs"}).text
        country = profile_info.find_all("section", attrs={"class": "scrollable"}
                                        )[1].find("small").text
        avatar = profile_info.find_all("section", attrs={"class": "scrollable"})[2].find("img")["src"]
        rankscore = profile_info.find_all("section", attrs={"class": "scrollable"}
                                          )[1].find("span", attrs={"class": "m-b-xs h4 block"}).text

        try:
            raw_pp = self.total_pp
        except KeyError:
            raw_pp = 0

        return {
            "username": username,
            "avatar_url": avatar,
            "rankscore": rankscore,
            "raw_pp": raw_pp,
            "country": country,
            "total_score": stats[0],
            "overall_acc": stats[1],
            "playcount": stats[2],
            "user_id": self.uid
        }

    @property
    def basic_user_data(self):
        data = requests.get(f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}"
                            ).json()['data']

        return {
            "uid": data['uid'],
            "username": data['username']
        }

    @property
    def pp_data(self):
        data = (raw_data := requests.get(
            f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}"
        ).json()['data'])['pp']

        data['uid'] = raw_data['uid']
        data['username'] = raw_data['username']
        data['list'] = [{**d, **{"mods": self._replace_mods(d['mods'])}} for d in data['list']]

        return data

    @property
    def rankscore(self):
        rankscore = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                  )
        return rankscore

    @property
    def total_pp(self):
        data = requests.get(f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}")

        # noinspection PyBroadException
        try:
            return data.json()["data"]["pp"]["total"]
        except Exception:
            return 0

    @property
    def best_play(self):
        data = requests.get(f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}")

        return data.json()["data"]["pp"]["list"][0]

    @property
    def recent_play(self):
        recent_play = self.get_play_data(BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                                       ).find_all("section", attrs={"class": "scrollable"})[1].find_all(
            "li", attrs={"class": "list-group-item"})[0].find_all("a")[-1])

        recent_play['mods'] = self._replace_mods(recent_play['mods'])
        print(self._replace_mods(recent_play['mods']))

        return recent_play

    @property
    def recent_plays(self):
        unfiltered_recent_plays = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                                ).find_all("section", attrs={"class": "scrollable"})[1].find_all(
            "li", attrs={"class": "list-group-item"})

        recent_plays = []
        for play in unfiltered_recent_plays:
            try:
                play_data = self.get_play_data(play)
            except AttributeError:
                pass
            else:
                recent_plays.append(play_data)
        return recent_plays
