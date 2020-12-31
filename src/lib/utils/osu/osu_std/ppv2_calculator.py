import requests

from src.lib.external.oppadc import oppadc
from src.paths import RECENT_OSU_FILE_PATH


def get_ppv2(beatmap_id, mods: str = "NM", misses: int = 0,
             accuracy: float = 100.00, max_combo: int = None, formatted: bool = False):
    """
    :param max_combo: the max_combo obtained on the play, defaults to beatmap max-combo
    :param formatted: returns with 2 floats decimals if set to true
    :param accuracy: accuracy of the play
    :param misses: number of misses of the play
    :param mods: a string of the mods used e.g: DTHD
    :param beatmap_id: id of the beatmap you want to get br pp info
    :return: a dict: {raw_pp, aim_pp, speed_pp, acc_pp, acc_percent}
    """

    beatmap_data: str = str(requests.get(f"https://osu.ppy.sh/osu/{beatmap_id}", allow_redirects=True
                                         ).content).replace("\\n", "\n").replace("\\r", "\r"
                                                                                 )[2:][:-2].replace("\n", "")

    with open(RECENT_OSU_FILE_PATH, "w+") as recent_file:
        recent_file.write(beatmap_data)
        recent_file.close()

    beatmap: oppadc.OsuMap = oppadc.OsuMap(file_path=RECENT_OSU_FILE_PATH)

    if max_combo is None:
        max_combo = beatmap.maxCombo()

    # noinspection PyTypeChecker
    calculated_pp = beatmap.getPP(Mods=mods, accuracy=accuracy, misses=misses, combo=max_combo)

    raw_pp = calculated_pp.total_pp
    aim_pp = calculated_pp.aim_pp
    speed_pp = calculated_pp.speed_pp
    acc_pp = calculated_pp.speed_pp
    acc_percent = calculated_pp.accuracy

    if not formatted:
        return {
            "beatmap": beatmap,
            "raw_pp": raw_pp,
            "aim_pp": aim_pp,
            "speed_pp": speed_pp,
            "acc_pp": acc_pp,
            "acc_percent": acc_percent
        }
    else:
        return {
            "beatmap": beatmap,
            "raw_pp": f"{raw_pp: .2f}",
            "aim_pp": f"{aim_pp: .2f}",
            "speed_pp": f"{speed_pp: .2f}",
            "acc_pp": f"{acc_pp: .2f}",
            "acc_percent": f"{acc_percent: .2f}"
        }
