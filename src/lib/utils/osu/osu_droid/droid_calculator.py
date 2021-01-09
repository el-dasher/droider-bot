from src.lib.utils.osu.osu_std.ppv2_calculator import get_ppv2


# A fórmula para calcular o OD do droid não é exatamente OD do std -5 mas isso deve servir por enquanto
# eu não consegui entender a fórmula do rian since eu sou bem mongol.
class OsuDroidBeatmapData:
    def __init__(self, beatmap_id, mods: str = "NM", misses: int = 0,
                 accuracy: float = 100.00, max_combo: int = None, formatted: bool = False, custom_speed: float = 1.00):
        self._beatmap_id = beatmap_id
        self._misses = misses
        self._mods = mods
        self._accuracy = accuracy
        self._max_combo = max_combo
        self._formatted = formatted
        self._custom_speed = custom_speed

    def get_bpp(self):
        beatmap_id = self._beatmap_id
        mods = self._mods
        misses = self._misses
        accuracy = self._accuracy
        max_combo = self._max_combo
        custom_speed = self._custom_speed
        formatted = self._formatted

        mods = f"{mods.upper()}TD"
        useful_data = get_ppv2(beatmap_id, mods, misses, accuracy, max_combo, formatted=False)

        beatmap = useful_data["beatmap"]

        beatmap.od -= 5
        beatmap.cs -= 4

        if "PR" in mods:
            beatmap.od += 5
        if "SC" in mods:
            beatmap.cs += 4
        if "REZ" in mods:
            beatmap.ar -= 0.5
            beatmap.cs -= 4
            beatmap.od /= 4
            beatmap.hp /= 4
        if "SU" in mods:
            custom_speed = 1.25 * custom_speed

        pp_data = beatmap.getPP(Mods=mods, accuracy=accuracy, misses=misses, combo=max_combo, recalculate=True)

        raw_pp = pp_data.total_pp
        aim_pp = pp_data.aim_pp
        speed_pp = pp_data.speed_pp
        acc_pp = pp_data.acc_pp
        acc_percent = pp_data.accuracy

        raw_pp -= aim_pp
        raw_pp -= speed_pp

        aim_pp *= 0.8
        speed_pp *= custom_speed

        raw_pp += aim_pp
        raw_pp += speed_pp

        pp_datas = [raw_pp, aim_pp, speed_pp, acc_pp]
        for i in pp_datas:
            if i < 0:
                raw_pp += i * -1

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

    def get_diff(self):
        beatmap_id = self._beatmap_id
        mods = self._mods
        misses = self._misses
        accuracy = self._accuracy
        max_combo = self._max_combo

        mods = mods.upper()
        useful_data = get_ppv2(beatmap_id, mods, misses, accuracy, max_combo, formatted=False)

        beatmap = useful_data["beatmap"]

        if "PR" in mods:
            beatmap.od += 5
        if "SC" in mods:
            beatmap.cs += 4
        if "REZ" in mods:
            beatmap.ar -= 0.5
            beatmap.cs -= 4
            beatmap.od /= 4
            beatmap.hp /= 4

        diff_data = beatmap.getDifficulty(Mods=mods, recalculate=True)

        return {
            "diff_approach": diff_data.ar,
            "diff_size": diff_data.cs,
            "diff_overall": diff_data.od,
            "diff_drain": diff_data.hp,
            "mods": mods
        }
