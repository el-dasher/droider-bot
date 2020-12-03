from abc import ABC
from urllib.request import urlopen
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from datetime import datetime


def get_droid_data(user_id):

    old_data = []
    beatmap_data = []

    user_url = f"http://ops.dgsrz.com/profile.php?uid={user_id}"
    droid_html = urlopen(user_url).read()
    droid_data_soup = BeautifulSoup(droid_html, features="html.parser")

    class DroidParser(HTMLParser, ABC):
        def handle_data(self, html_data):
            html_data = html_data.replace("\n", "").replace("\r", "").strip()
            if len(html_data) != 1 and html_data != "":
                # noinspection PyBroadException
                try:
                    if html_data[0] != "{" and html_data[-1] != "}":

                        html_data = html_data.strip().split("/")

                        old_data.append(html_data.copy())

                        if old_data[old_data.index(html_data) - 1][0] != html_data[0]:
                            beatmap_name = old_data[old_data.index(html_data) - 1][0]
                        else:
                            beatmap_name = None

                        html_data[0] = datetime.strptime(html_data[0].strip(), "%Y-%m-%d %H:%M:%S")
                        html_data.append(beatmap_name)

                        beatmap_data.append(html_data)

                except Exception:
                    pass

    pp_user_url = f"https://ppboard.herokuapp.com/profile?uid={user_id}"
    pp_html = urlopen(pp_user_url).read()
    pp_data_soup = BeautifulSoup(pp_html, features="html.parser")

    total_pp = []

    class PPBoardParser(HTMLParser, ABC):
        def handle_data(self, pp_html_data):
            if "{" not in pp_html_data or "}" not in pp_html_data:
                total_pp.append(pp_html_data)
                print(total_pp)
    pp_parser = PPBoardParser()
    pp_parser.feed(str(pp_data_soup))

    droid_parser = DroidParser()
    droid_parser.feed(str(droid_data_soup))
    data_dicts = {}
    for i, data in enumerate(beatmap_data):
        data_dict = {
            "user_data": {
                "username": old_data[26][0],
                "raw_pp": float(total_pp[8][9:].strip()),
                "total_score": int(old_data[-13][0].replace(",", "")),
                "overall_acc": old_data[-11][0][:-1],
                "playcount": old_data[-9][0]
            },
            f"rs_{i}": {
                "username": old_data[26][0],
                "beatmap": data[5],
                "date": data[0],
                "score": int(data[1].replace(",", "")),
                "mods": data[2],
                "combo": int(data[3][:-2]),
                "accuracy": data[4][:-1]
            }
        }

        data_dicts.update(data_dict)

    return data_dicts
