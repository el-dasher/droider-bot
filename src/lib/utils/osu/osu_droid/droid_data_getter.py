import requests
from bs4 import BeautifulSoup

from src.setup import DPPBOARD_API as DPP_BOARD_API


class OsuDroidProfile:
    def __init__(self, uid: int):
        self.uid = uid

    @property
    def profile(self):
        unfiltered_profile_info = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                                ).find_all("div", attrs={"class": "panel"})[1].find_all(
            "span", attrs={"class": "pull-right"})[:3]

        profile_info = [profile_data.text for profile_data in unfiltered_profile_info]

        return {
            "username": self.username,
            "avatar_url": self.avatar,
            "rankscore": self.rankscore,
            "raw_pp": self.total_pp,
            "country": self.country,
            "total_score": profile_info[0],
            "overall_acc": profile_info[1],
            "playcount": profile_info[2],
            "player_best": self.best_play,
            "user_id": self.uid
        }

    @property
    def pp_data(self):
        data = requests.get(f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}")

        return data.json()["data"]["pp"]

    @property
    def avatar(self):
        avatar_url = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                   ).find_all("section", attrs={"class": "scrollable"})[2].find("img")["src"]

        return avatar_url

    @property
    def rankscore(self):
        rankscore = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                  ).find_all("section", attrs={"class": "scrollable"}
                                             )[1].find("span", attrs={"class": "m-b-xs h4 block"}).text

        return rankscore

    @property
    def username(self):
        username = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                 ).find_all("section", attrs={"class": "scrollable"}
                                            )[1].find("div", attrs={"class": "h3 m-t-xs m-b-xs"}).text

        return username

    @property
    def country(self):
        username = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                 ).find_all("section", attrs={"class": "scrollable"}
                                            )[1].find("small").text

        return username

    @property
    def total_pp(self):
        data = requests.get(f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}")

        return data.json()["data"]["pp"]["total"]

    @property
    def best_play(self):
        data = requests.get(f"http://droidppboard.herokuapp.com/api/getplayertop?key={DPP_BOARD_API}&uid={self.uid}")

        return data.json()["data"]["pp"]["list"][0]

    @property
    def recent_plays(self):
        unfiltered_recent_plays = BeautifulSoup(requests.get(
            f"http://ops.dgsrz.com/profile.php?uid={self.uid}").text, features="html.parser"
                                                ).find_all("section", attrs={"class": "scrollable"})[1].find_all(
            "li", attrs={"class": "list-group-item"})
        semi_filtered_recent_plays = list(filter(lambda a: len(a) > 0,
                                                 [play.find_all("a", attrs={"class": "clear"})
                                                  for play in unfiltered_recent_plays]
                                                 )
                                          )
        recent_plays = []
        for play in semi_filtered_recent_plays:
            for tag in play:
                play_info = (tag.text.replace("\n", "").strip().split("/"))
                play_info[-1] = play_info[-1].split("{")

                accuracy = play_info[-1][0].replace(" ", "")

                play_info[-1] = play_info[-1][1].split('"miss": ')
                play_info.append(play_info[-1][0])
                play_info.append(play_info[-2][-1])

                play_info.pop(-3)

                play_info.append(play_info[0].split("]")[-1])
                play_info[0] = play_info[0].split("]")[0] + "]"
                play_info[-2] = play_info[-2].split('"hash": ')
                play_info.append(play_info[-2][0].split(","))
                play_info.append(play_info[-1][0].split(":")[1])
                play_info.append(play_info[-2][1].split(":")[1].replace("}", ""))

                play_info.pop(-3)
                play_info.pop(-4)
                play_info.pop(-4)

                play_info = list(filter(lambda a: len(a) > 0, play_info))

                if len(play_info[-2]) == 0:
                    play_info[-2] = 0

                play_info[2] = play_info[2].replace(",", "")

                for i, data in enumerate(play_info):
                    if i > 0 and i != 4:
                        play_info[i] = data.replace(" ", "")
                        if i == 2:
                            if len(data) == 2 or "None" in data:
                                play_info[i] = "NM"
                            play_info[i] = play_info[i].replace("DoubleTime", "DT").replace(
                                "Hidden", "HD").replace("HardRock", "HR").replace(
                                "Precise", "PR").replace("NoFail", "NF").replace(
                                    "Easy", "EZ").replace("NightCore", "NC")

                title = play_info[0]
                score = play_info[1]
                mods = play_info[2]
                combo = play_info[3]
                date = play_info[4]
                misscount = play_info[5]
                hash_ = play_info[6]

                recent_plays.append({
                    "title": title,
                    "score": score,
                    "mods": mods,
                    "combo": combo,
                    "accuracy": accuracy,
                    "misscount": misscount,
                    "date": date,
                    "hash": hash_
                })

        return recent_plays
