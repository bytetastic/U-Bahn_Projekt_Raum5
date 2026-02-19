# logik.py
import difflib
import math
from werkzeuge import TextUtils


class TariffManager:
    """
    Behandelt die Preislogik
    """

    def calculate_ticket(self, stations_count, is_multi_ticket, has_social_card, pay_cash):
        if stations_count <= 3:
            category = "Kurzstrecke"
            base_single, base_multi = 1.50, 5.00
        elif stations_count <= 8:
            category = "Mittelstrecke"
            base_single, base_multi = 2.00, 7.00
        else:
            category = "Langstrecke"
            base_single, base_multi = 3.00, 10.00

        price = base_multi if is_multi_ticket else base_single

        if not is_multi_ticket: price *= 1.10
        if has_social_card: price *= 0.80
        if pay_cash: price *= 1.15

        return round(price, 2), category


class RouteManager:
    """
    Verwaltet die Stationen und die Suche
    """

    def __init__(self):
        self.stations = [
            "Langwasser Süd", "Gemeinschaftshaus", "Langwasser Mitte",
            "Scharfreiterring", "Langwasser Nord", "Messe",
            "Bauernfeindstraße", "Hasenbuck", "Frankenstraße",
            "Maffeiplatz", "Aufseßplatz", "Hauptbahnhof",
            "Lorenzkirche", "Weißer Turm", "Plärrer",
            "Gostenhof", "Bärenschanze", "Maximilianstraße",
            "Eberhardshof", "Muggenhof", "Stadtgrenze",
            "Jakobinenstraße", "Fürth Hbf."
        ]

    def find_station(self, user_input):
        normalized_input = TextUtils.normalize(user_input)
        best_match, best_ratio = None, 0.0

        for station in self.stations:
            normalized_station = TextUtils.normalize(station)
            ratio = difflib.SequenceMatcher(None, normalized_input, normalized_station).ratio()
            if ratio > best_ratio:
                best_ratio, best_match = ratio, station

        return best_match if best_ratio >= 0.8 else None

    def get_station_index(self, station_name):
        return self.stations.index(station_name)


class TimetableManager:
    """
    Fahrplan-Logik
    """

    def __init__(self, route_mgr):
        self.route_mgr = route_mgr
        self.hubs = ["Hauptbahnhof", "Plärrer", "Fürth Hbf.", "Langwasser Süd"]

        # EXAKTE Fahrzeiten aus dem Netzplan U1 (Minuten in Sekunden umgerechnet)
        self.segment_times = [
            180,  # 0: Langwasser Süd -> Gem.haus (3 Min)
            120,  # 1: Gem.haus -> Langw. Mitte (2 Min)
            120,  # 2: Langw. Mitte -> Scharfreit. (2 Min)
            180,  # 3: Scharfreit. -> Langw. Nord (3 Min)
            120,  # 4: Langw. Nord -> Messe (2 Min)
            180,  # 5: Messe -> Bauernfeind. (3 Min)
            120,  # 6: Bauernfeind. -> Hasenbuck (2 Min)
            120,  # 7: Hasenbuck -> Frankenstr. (2 Min)
            120,  # 8: Frankenstr. -> Maffeiplatz (2 Min)
            60,  # 9: Maffeiplatz -> Aufseßplatz (1 Min)
            120,  # 10: Aufseßplatz -> Hauptbahnhof (2 Min)
            120,  # 11: Hauptbahnhof -> Lorenzkirche (2 Min)
            180,  # 12: Lorenzkirche -> Weißer Turm (3 Min)
            120,  # 13: Weißer Turm -> Plärrer (2 Min)
            120,  # 14: Plärrer -> Gostenhof (2 Min)
            60,  # 15: Gostenhof -> Bärenschanze (1 Min)
            120,  # 16: Bärenschanze -> Maximilian. (2 Min)
            120,  # 17: Maximilian. -> Eberhardshof (2 Min)
            120,  # 18: Eberhardshof -> Muggenhof (2 Min)
            180,  # 19: Muggenhof -> Stadtgrenze (3 Min)
            120,  # 20: Stadtgrenze -> Jakobinenstr. (2 Min)
            180  # 21: Jakobinenstr. -> Fürth Hbf. (3 Min)
        ]

        # Arrays für die vorab berechneten Ankunfts- und Abfahrtszeiten des ALLERERSTEN Zuges
        self.dep_dir1 = [0] * 23
        self.arr_dir1 = [0] * 23
        self.dep_dir2 = [0] * 23
        self.arr_dir2 = [0] * 23

        self._precompute_schedules()

    def get_stop_time(self, station_name):
        return 60 if station_name in self.hubs else 30

    def _precompute_schedules(self):
        # --- RICHTUNG 1: Langwasser (0) -> Fürth (22) ---
        t = 5 * 3600  # Start um exakt 05:00:00 Uhr
        self.dep_dir1[0] = t
        self.arr_dir1[0] = t

        for i in range(22):
            t += self.segment_times[i]
            self.arr_dir1[i + 1] = t
            t += self.get_stop_time(self.route_mgr.stations[i + 1])
            self.dep_dir1[i + 1] = t

        # --- RICHTUNG 2: Fürth (22) -> Langwasser (0) ---
        # Der erste Zug aus Langwasser kommt in Fürth an und wendet (60s Halt)
        # Seine exakte Abfahrt ist somit in self.dep_dir1[22] gespeichert! (06:00:30)
        t = self.dep_dir1[22]
        self.dep_dir2[22] = t
        self.arr_dir2[22] = t

        for i in range(22, 0, -1):
            t += self.segment_times[i - 1]
            self.arr_dir2[i - 1] = t
            t += self.get_stop_time(self.route_mgr.stations[i - 1])
            self.dep_dir2[i - 1] = t

    def calculate_travel(self, start_idx, end_idx, wunschzeit_str):
        hours, minutes = map(int, wunschzeit_str.split(':'))
        wunsch_sec = hours * 3600 + minutes * 60

        # Hole die "Muster-Zeiten" des allerersten Zuges des Tages
        if start_idx < end_idx:
            base_dep = self.dep_dir1[start_idx]
            base_arr = self.arr_dir1[end_idx]
        else:
            base_dep = self.dep_dir2[start_idx]
            base_arr = self.arr_dir2[end_idx]

        travel_duration = base_arr - base_dep

        # Finde den nächsten Taktzyklus (10 Minuten = 600 Sekunden)
        if wunsch_sec <= base_dep:
            actual_dep = base_dep
        else:
            diff = wunsch_sec - base_dep
            cycles = math.ceil(diff / 600.0)
            actual_dep = base_dep + cycles * 600

        actual_arr = actual_dep + travel_duration

        # Formatierung (Stunden, Minuten, Sekunden)
        def format_time(total_seconds):
            h = int((total_seconds // 3600) % 24)
            m = int((total_seconds // 60) % 60)
            s = int(total_seconds % 60)

            exact_str = f"{h:02d}:{m:02d}:{s:02d}"

            # Aufrunden für Ankunft
            rounded_m = m + 1 if s >= 30 else m
            rounded_h = h
            if rounded_m == 60:
                rounded_m = 0
                rounded_h = (h + 1) % 24
            rounded_str = f"{rounded_h:02d}:{rounded_m:02d}"

            # Abrunden (Floor) für die Abfahrt (Man will dem Fahrgast keine zu späte Zeit nennen)
            floored_str = f"{h:02d}:{m:02d}"

            return exact_str, rounded_str, floored_str

        dep_exact, dep_rounded, dep_floored = format_time(actual_dep)
        arr_exact, arr_rounded, arr_floored = format_time(actual_arr)

        return dep_floored, arr_exact, arr_rounded