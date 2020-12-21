import pyttanko
import requests

from src.paths import RECENT_OSU_FILE_PATH

PARSER = pyttanko.parser()


def get_bpp(beatmap_id, mods: str = "NM", misses: int = 0, accuracy: float = 100.00):
    """
    :param accuracy: accuracy of the play
    :param misses: number of misses of the play
    :param mods: a string of the mods used e.g: DTHD
    :param beatmap_id: id of the beatmap you want to get br pp info
    :return: a dict: {raw_pp, aim_pp, speed_pp, acc_pp, acc_percent}
    """

    mods: int = pyttanko.mods_from_str(mods)

    beatmap_data: str = str(requests.get(f"https://osu.ppy.sh/osu/{beatmap_id}", allow_redirects=True
                                         ).content).replace("\\n", "\n").replace("\\r", "\r"
                                                                                 )[2:][:-2].replace("\n", "")

    with open(RECENT_OSU_FILE_PATH, "w+") as recent_file:
        recent_file.write(beatmap_data)
        recent_file.close()

    beatmap: pyttanko.beatmap = PARSER.map(open(RECENT_OSU_FILE_PATH))

    beatmap.cs = beatmap.cs - 4
    beatmap.od = beatmap.od - 4

    beatmap.nobjects = beatmap.ncircles + beatmap.nspinners + beatmap.nsliders

    stars = pyttanko.diff_calc().calc(beatmap)

    accuracy = pyttanko.acc_round(accuracy, beatmap.nobjects, misses)

    n300 = accuracy[0]
    n100 = accuracy[1]
    n50 = accuracy[2]

    raw_pp, aim_pp, speed_pp, acc_pp, acc_percent = pyttanko.ppv2(
        stars.aim, stars.speed, bmap=beatmap, mods=mods, nmiss=misses, n300=n300, n100=n100, n50=n50)

    if stars.aim_length_bonus + stars.speed_length_bonus < 2.50:

        raw_pp -= aim_pp
        raw_pp -= speed_pp

        aim_pp -= aim_pp // 1.50
        speed_pp -= speed_pp // 3

        raw_pp += aim_pp
        raw_pp += speed_pp
    else:

        raw_pp -= aim_pp
        raw_pp -= speed_pp

        aim_pp -= aim_pp // 2
        speed_pp -= speed_pp // 4

        raw_pp += aim_pp
        raw_pp += speed_pp

    return {
        "raw_pp": raw_pp,
        "aim_pp": aim_pp,
        "speed_pp": speed_pp,
        "acc_pp": acc_pp,
        "acc_percent": acc_percent
    }
