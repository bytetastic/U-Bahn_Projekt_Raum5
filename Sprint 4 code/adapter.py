# adapter.py
from datetime import time, timedelta
from logik import RouteManager, TariffManager, TimetableManager
from werkzeuge import TextUtils


class adapter_klasse:
    def __init__(self):
        self.route_mgr = RouteManager()
        self.tariff_mgr = TariffManager()
        self.time_mgr = TimetableManager(self.route_mgr)

    def _sec_to_time(self, sec):
        h = int((sec // 3600) % 24)
        m = int((sec // 60) % 60)
        s = int(sec % 60)
        return time(h, m, s)

    def _sec_to_time_rounded(self, sec, round_up=False):
        h = int((sec // 3600) % 24)
        m = int((sec // 60) % 60)
        s = int(sec % 60)
        if round_up and s >= 30:
            m += 1
        if m == 60:
            m = 0
            h = (h + 1) % 24
        return time(h, m, 0)

    def ausfuehren_testfall(self, eingabe_start: str, eingabe_ziel: str,
                            eingabe_startzeit: str, eingabe_einzelfahrkarte: bool,
                            eingabe_sozialrabatt: bool, eingabe_barzahlung: bool) -> dict:

        # 1. Standard-Rückgabe bei Fehler (US 4.7.4)
        error_result = {
            "fehler": True,
            "ausgabe_startzeit_fahrgast": time(0, 0), "ausgabe_zielzeit_fahrgast": time(0, 0),
            "ausgabe_startzeit_algo": time(0, 0, 0), "ausgabe_zielzeit_algo": time(0, 0, 0),
            "bahnlinien_gesamtfahrt": [], "route": {}, "umstieg_haltestellen": [],
            "umstiege_exakt": {}, "umstiege_fahrgast": {}, "umstieg_bahnlinien": [],
            "dauer_gesamtfahrt": timedelta(0), "preis_endbetrag": 0.0
        }

        # 2. Eingaben validieren (US 4.4 Uhrzeit + US 4.1 Stationen)
        start = self.route_mgr.find_station(eingabe_start)
        ziel = self.route_mgr.find_station(eingabe_ziel)
        wunschzeit = TextUtils.parse_time(eingabe_startzeit)

        if not start or not ziel or not wunschzeit or start == ziel:
            return error_result

        # 3. Kürzesten Pfad suchen
        path = self.route_mgr.get_shortest_path(start, ziel)
        if not path:
            return error_result

        # 4. Zeitplan berechnen
        timeline = self.time_mgr.calculate_travel(path, wunschzeit)

        # 5. Preis berechnen
        preis, _ = self.tariff_mgr.calculate_ticket(
            len(path), not eingabe_einzelfahrkarte, eingabe_sozialrabatt, eingabe_barzahlung
        )

        # 6. Ergebnisse für den Adapter formatieren (genau nach US 4.7.2)
        start_sec = timeline[0]["dep_sec"]
        ziel_sec = timeline[-1]["arr_sec"]

        route_dict = {}
        linien_set = set()
        umstieg_stationen = []
        umstiege_exakt = {}
        umstiege_fahrgast = {}
        umstieg_linien = []

        for stop in timeline:
            linien_set.add(stop["linie"])
            route_dict[stop["station"]] = [
                stop["linie"],
                self._sec_to_time(stop["arr_sec"]),
                self._sec_to_time(stop["dep_sec"])
            ]

            if stop.get("is_transfer"):
                umstieg_stationen.append(stop["station"])
                umstieg_linien.append(stop["linie"])
                umstiege_exakt[stop["station"]] = [
                    self._sec_to_time(stop["arr_sec"]),
                    self._sec_to_time(stop["dep_sec"])
                ]
                umstiege_fahrgast[stop["station"]] = [
                    self._sec_to_time_rounded(stop["arr_sec"], round_up=True),
                    self._sec_to_time_rounded(stop["dep_sec"], round_up=False)
                ]

        return {
            "fehler": False,
            "ausgabe_startzeit_fahrgast": self._sec_to_time_rounded(start_sec, round_up=False),
            "ausgabe_zielzeit_fahrgast": self._sec_to_time_rounded(ziel_sec, round_up=True),
            "ausgabe_startzeit_algo": self._sec_to_time(start_sec),
            "ausgabe_zielzeit_algo": self._sec_to_time(ziel_sec),
            "bahnlinien_gesamtfahrt": list(linien_set),
            "route": route_dict,
            "umstieg_haltestellen": umstieg_stationen,
            "umstiege_exakt": umstiege_exakt,
            "umstiege_fahrgast": umstiege_fahrgast,
            "umstieg_bahnlinien": umstieg_linien,
            "dauer_gesamtfahrt": timedelta(seconds=(ziel_sec - start_sec)),
            "preis_endbetrag": preis
        }