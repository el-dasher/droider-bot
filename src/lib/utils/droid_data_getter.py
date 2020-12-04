from abc import ABC
from urllib.request import urlopen
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from datetime import datetime
from src.settings import DATABASE
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from random import randint

ppcheck_data = []


def get_droid_data(user_id):
    # noinspection PyGlobalUndefined
    
    droid_scheduler = AsyncIOScheduler
    global ppcheck_data
    old_data = []
    beatmap_data = []
    html_imgs = []

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

        def handle_starttag(self, tag, attrs):
            if tag == "img":
                html_imgs.append(attrs)

    pp_user_url = f"https://ppboard.herokuapp.com/profile?uid={user_id}"

    # noinspection PyBroadException
    try:
        pp_html = urlopen(pp_user_url).read()
    except Exception:
        pp_board_state = "OFFLINE"
        completed_pp_data = None
    else:
        pp_data_soup = BeautifulSoup(pp_html, features="html.parser")

        pp_data = []
        completed_pp_data = []

        class PPBoardParser(HTMLParser, ABC):
            def __init__(self):
                super().__init__()
                self.counter = 0

            def handle_data(self, pp_html_data):
                if "{" not in pp_html_data or "}" not in pp_html_data:
                    pp_data.append(pp_html_data)

                    if pp_html_data != "-> Raw PP: ":
                        if not str(pp_html_data).__contains__("Net pp"):
                            beatmap_specifict_data = [pp_html_data]
                            completed_pp_data.append(beatmap_specifict_data)

        pp_parser = PPBoardParser()
        pp_parser.feed(str(pp_data_soup))

        for _ in range(9):
            try:
                completed_pp_data.pop(0)
            except IndexError:
                pass

        ppcheck_data = []

        for x, y in zip(completed_pp_data[::2], completed_pp_data[1::2]):
            ppcheck_data.append({"beatmap-mod": x, "pp_raw": y})

    droid_parser = DroidParser()
    droid_parser.feed(str(droid_data_soup))
    # data_dicts = {}

    beatmap_dicts = {}
    
    
    if pp_data == "OFFLINE":
    	if (backup_pp_data := DATABASE.child("DROID_UID_DATA").child(user_id).get().val()) is not None:
    		pp_data = backup_pp_data["pp_raw"]
    	else:
    	    pp_data = "OFFLINE"
    else:
        pp_data = float(pp_data[8][9:].strip())
    print(DATABASE.child("DROID_UID_DATA").child(user_id).get().val())
    for i, data in enumerate(beatmap_data):
        beatmap_dicts[f"rs_{i}"] = {
            "username": old_data[26][0],
            "beatmap": data[5],
            "date": data[0],
            "score": data[1],
            "mods": data[2],
            "combo": int(data[3][:-2]),
            "accuracy": float(data[4][:-1])
        }

    try:
        user_data = {
            "username": old_data[26][0],
            "avatar_url": html_imgs[3][0][1],
            "user_id": user_id,
            "country": old_data[27][0],
            "raw_pp": pp_data,
            "total_score": old_data[-13][0],
            "overall_acc": float(old_data[-11][0][:-1]),
            "playcount": int(old_data[-9][0])
        }
    except ValueError:
        user_data = {
            "username": old_data[26][0],
            "avatar_url": html_imgs[3][0][1],
            "user_id": user_id,
            "country": old_data[27][0],
            "raw_pp": pp_data,
            "total_score": old_data[-12][0],
            "overall_acc": float(old_data[-10][0][:-1]),
            "playcount": "Erro!"
        }
    try:
        data_dict = {"user_data": user_data, "beatmap_data": beatmap_dicts, "pp_data": ppcheck_data}
    except NameError:
        data_dict = {"user_data": user_data, "beatmap_data": beatmap_dicts, "pp_data": [{"s": "OFFLINE"}]}
    
    if pp_data != "offline":
        trigger = CronTrigger(hour=1, minute=randint(0, 59), second=0)
            
        updated_user_data = droid_scheduler.add_job(get_droid_data(user_id)["user_data"]["pp_raw"], trigger)
        droid_scheduler.add_job(lambda: DATABASE.child("DROID_UID_DATA").child(user_id).set(updated_user_data) if updated_user_data != "OFFLINE" else print(), trigger)
            
    # return data_dicts
    return data_dict

