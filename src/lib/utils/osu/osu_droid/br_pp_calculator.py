from src.lib.utils.osu.osu_std.ppv2_calculator import get_ppv2


def get_bpp(beatmap_id, mods: str = "NM", misses: int = 0,
            accuracy: float = 100.00, max_combo: int = None, formatted: bool = False):
    mods = f"{mods.upper()}TD"
    useful_data = get_ppv2(beatmap_id, mods, misses, accuracy, max_combo, formatted=False)

    beatmap = useful_data["beatmap"]

    beatmap.od -= 4
    beatmap.cs -= 4

    if "PR" in mods:
        beatmap.od += 4
    if "SC" in mods:
        beatmap.cs += 4
    if "REZ" in mods:
        beatmap.ar -= 0.5
        beatmap.cs -= 4
        beatmap.od /= 4
        beatmap.hp /= 4

    pp_data = beatmap.getPP(Mods=mods, accuracy=accuracy, combo=max_combo, recalculate=True)

    raw_pp = pp_data.total_pp
    aim_pp = pp_data.aim_pp
    speed_pp = pp_data.speed_pp
    acc_pp = pp_data.acc_pp
    acc_percent = pp_data.accuracy

    if not formatted:
        return {
            "raw_pp": raw_pp,
            "aim_pp": aim_pp,
            "speed_pp": speed_pp,
            "acc_pp": acc_pp,
            "acc_percent": acc_percent
        }
    else:
        return {
            "raw_pp": f"{raw_pp: .2f}",
            "aim_pp": f"{aim_pp: .2f}",
            "speed_pp": f"{speed_pp: .2f}",
            "acc_pp": f"{acc_pp: .2f}",
            "acc_percent": f"{acc_percent: .2f}"
        }
