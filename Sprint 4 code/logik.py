# logik.py
import difflib
import math
import heapq
import itertools
from werkzeuge import TextUtils


class TariffManager:
    def calculate_ticket(self, stations_count, is_multi_ticket, has_social_card, pay_cash):
        if stations_count <= 3:
            category, base_single, base_multi = "Kurzstrecke", 1.50, 5.00
        elif stations_count <= 8:
            category, base_single, base_multi = "Mittelstrecke", 2.00, 7.00
        else:
            category, base_single, base_multi = "Langstrecke", 3.00, 10.00

        price = base_multi if is_multi_ticket else base_single
        if not is_multi_ticket: price *= 1.10
        if has_social_card: price *= 0.80
        if pay_cash: price *= 1.15
        return round(price, 2), category


class RouteManager:
    def __init__(self):
        # Echter Netzplan
        raw_data = """U1;Langwasser Süd;3;Gemeinschaftshaus
U1;Gemeinschaftshaus;2;Langwasser Mitte
U1;Langwasser Mitte;2;Scharfreiterring
U1;Scharfreiterring;3;Langwasser Nord
U1;Langwasser Nord;2;Messe
U1;Messe;3;Bauernfeindstraße
U1;Bauernfeindstraße;2;Hasenbuck
U1;Hasenbuck;2;Frankenstraße
U1;Frankenstraße;2;Maffeiplatz
U1;Maffeiplatz;1;Aufseßplatz
U1;Aufseßplatz;2;Hauptbahnhof
U1;Hauptbahnhof;2;Lorenzkirche
U1;Lorenzkirche;3;Weißer Turm
U1;Weißer Turm;2;Plärrer
U1;Plärrer;2;Gostenhof
U1;Gostenhof;1;Bärenschanze
U1;Bärenschanze;2;Maximilianstraße
U1;Maximilianstraße;2;Eberhardshof
U1;Eberhardshof;2;Muggenhof
U1;Muggenhof;3;Stadtgrenze
U1;Stadtgrenze;2;Jakobinenstraße
U1;Jakobinenstraße;3;Fürth Hbf.
U2;Röthenbach;2;Hohe Marter
U2;Hohe Marter;2;Schweinau
U2;Schweinau;2;St. Leonhard
U2;St. Leonhard;2;Rothenburger Straße
U2;Rothenburger Straße;3;Plärrer
U2;Plärrer;2;Opernhaus
U2;Opernhaus;2;Hauptbahnhof
U2;Hauptbahnhof;2;Wöhrder Wiese
U2;Wöhrder Wiese;1;Rathenauplatz
U2;Rathenauplatz;2;Rennweg
U2;Rennweg;2;Schoppershof
U2;Schoppershof;2;Nordostbahnhof
U2;Nordostbahnhof;3;Herrnhütte
U2;Herrnhütte;2;Ziegelstein
U2;Ziegelstein;3;Flughafen
U3;Gustav-Adolf-Straße;4;Sündersbühl
U3;Sündersbühl;2;Rothenburger Straße
U3;Rothenburger Straße;3;Plärrer
U3;Plärrer;2;Opernhaus
U3;Opernhaus;2;Hauptbahnhof
U3;Hauptbahnhof;2;Wöhrder Wiese
U3;Wöhrder Wiese;1;Rathenauplatz
U3;Rathenauplatz;2;Maxfeld
U3;Maxfeld;3;Kaulbachplatz
U3;Kaulbachplatz;2;Friedrich-Ebert-Platz"""

        self.lines = {}
        for row in raw_data.strip().split('\n'):
            parts = row.strip().split(';')
            linie, s1, t_min, s2 = parts[0], parts[1], int(parts[2]), parts[3]

            if linie not in self.lines:
                self.lines[linie] = []
                self.lines[linie].append({"name": s1, "time_to_next": t_min * 60})
            else:
                self.lines[linie][-1]["time_to_next"] = t_min * 60

            if len(self.lines[linie]) == 0 or self.lines[linie][-1]["name"] != s2:
                self.lines[linie].append({"name": s2, "time_to_next": 0})

        self.hubs = [
            "Hauptbahnhof", "Plärrer",
            "Langwasser Süd", "Fürth Hbf.", "Röthenbach", "Flughafen",
            "Gustav-Adolf-Straße", "Friedrich-Ebert-Platz"
        ]

        self.all_stations = list(set([station["name"] for line in self.lines.values() for station in line]))

        self.graph = {station: [] for station in self.all_stations}
        for line, stations in self.lines.items():
            for i in range(len(stations) - 1):
                s1, s2 = stations[i]["name"], stations[i + 1]["name"]
                t = stations[i]["time_to_next"]
                self.graph[s1].append({"ziel": s2, "linie": line, "dir": "Hin", "fahrzeit": t})
                self.graph[s2].append({"ziel": s1, "linie": line, "dir": "Rueck", "fahrzeit": t})

    def get_stop_time(self, station_name):
        return 60 if station_name in self.hubs else 30

    def find_station(self, user_input):
        normalized_input = TextUtils.normalize(user_input)
        best_match, best_ratio = None, 0.0
        for station in self.all_stations:
            ratio = difflib.SequenceMatcher(None, normalized_input, TextUtils.normalize(station)).ratio()
            if ratio > best_ratio:
                best_ratio, best_match = ratio, station
        return best_match if best_ratio >= 0.8 else None

    def get_shortest_path(self, start, end):
        """ US 4.3.1: Dijkstra Algorithmus mit Umstiegs-Bestrafung """
        tie_breaker = itertools.count()  # Generiert fortlaufende Nummern (0, 1, 2, 3...)

        # Queue: (Kosten, Zähler, Aktuelle_Station, Aktuelle_Linie, Pfad)
        queue = [(0, next(tie_breaker), start, "START", [])]
        visited = {}

        while queue:
            cost, _, curr_station, curr_line, path = heapq.heappop(queue)

            if curr_station in visited and visited[curr_station] <= cost:
                continue
            visited[curr_station] = cost

            if curr_station == end:
                return path

            for edge in self.graph[curr_station]:
                next_station, next_line, next_dir = edge["ziel"], edge["linie"], edge["dir"]
                travel_time = edge["fahrzeit"] + self.get_stop_time(next_station)

                # Umstiegs-Bestrafung (+5 Min = 300 Sek)
                transfer_penalty = 300 if curr_line != "START" and curr_line != next_line else 0

                new_path = path + [{"von": curr_station, "nach": next_station, "linie": next_line, "dir": next_dir}]

                # Den Zähler (next(tie_breaker)) mit in die Queue packen, um den Dictionary-Crash zu verhindern
                heapq.heappush(queue,
                               (cost + travel_time + transfer_penalty, next(tie_breaker), next_station, next_line,
                                new_path))

        return None


class TimetableManager:
    def __init__(self, route_mgr):
        self.route_mgr = route_mgr
        self.takt_sec = 600
        self.start_of_day_sec = 5 * 3600

        # NEU: Wir haben keinen festen Puffer mehr, sondern berechnen ihn dynamisch!
        self.schedule = {}
        self._precompute_base_schedule()

    def get_transfer_time(self, station_name):
        """ Gibt die exakte Umstiegszeit (in Sekunden) für die jeweilige Station zurück """
        if station_name in ["Hauptbahnhof", "Plärrer"]:
            return 300  # 5 Minuten an den großen Knotenpunkten
        return 180  # 3 Minuten an allen anderen Stationen

    def _precompute_base_schedule(self):
        for line, stations in self.route_mgr.lines.items():
            self.schedule[line] = {"Hin": {}, "Rueck": {}}
            t = self.start_of_day_sec
            for i in range(len(stations)):
                station = stations[i]["name"]
                arr = t
                dep = t if i == 0 else t + self.route_mgr.get_stop_time(station)
                self.schedule[line]["Hin"][station] = {"arr": arr, "dep": dep}
                if i < len(stations) - 1:
                    t = dep + stations[i]["time_to_next"]

            t = self.start_of_day_sec
            for i in range(len(stations) - 1, -1, -1):
                station = stations[i]["name"]
                arr = t
                dep = t if i == len(stations) - 1 else t + self.route_mgr.get_stop_time(station)
                self.schedule[line]["Rueck"][station] = {"arr": arr, "dep": dep}
                if i > 0:
                    t = dep + stations[i - 1]["time_to_next"]

    def calculate_travel(self, path, wunschzeit_str):
        hours, minutes = map(int, wunschzeit_str.split(':'))
        current_time_sec = hours * 3600 + minutes * 60
        timeline = []

        for i, step in enumerate(path):
            is_start = (i == 0)
            is_transfer = (i > 0 and path[i - 1]["linie"] != step["linie"])

            if is_start or is_transfer:
                # NEU: Dynamische Umstiegszeit abfragen und addieren
                transfer_sec = 0
                if is_transfer:
                    transfer_sec = self.get_transfer_time(step["von"])
                    current_time_sec += transfer_sec

                line, direction = step["linie"], step["dir"]
                base_dep = self.schedule[line][direction][step["von"]]["dep"]

                if current_time_sec <= base_dep:
                    actual_dep = base_dep
                else:
                    cycles = math.ceil((current_time_sec - base_dep) / self.takt_sec)
                    actual_dep = base_dep + cycles * self.takt_sec

                if is_start:
                    timeline.append({
                        "station": step["von"], "linie": line,
                        "arr_sec": actual_dep, "dep_sec": actual_dep
                    })
                else:
                    timeline[-1]["dep_sec"] = actual_dep
                    timeline[-1]["alte_linie"] = timeline[-1]["linie"]
                    timeline[-1]["linie"] = line
                    timeline[-1]["is_transfer"] = True
                    # Wir speichern die Minuten für die Ausgabe in der main.py
                    timeline[-1]["transfer_min"] = int(transfer_sec / 60)

                current_time_sec = actual_dep

            line, direction = step["linie"], step["dir"]
            base_dep = self.schedule[line][direction][step["von"]]["dep"]
            base_arr = self.schedule[line][direction][step["nach"]]["arr"]
            travel_duration = base_arr - base_dep

            current_time_sec += travel_duration

            is_end = (i == len(path) - 1)
            next_is_transfer = (not is_end and path[i + 1]["linie"] != step["linie"])

            if is_end or next_is_transfer:
                timeline.append({
                    "station": step["nach"], "linie": line,
                    "arr_sec": current_time_sec, "dep_sec": current_time_sec
                })
            else:
                stop_time = self.route_mgr.get_stop_time(step["nach"])
                dep_sec = current_time_sec + stop_time
                timeline.append({
                    "station": step["nach"], "linie": line,
                    "arr_sec": current_time_sec, "dep_sec": dep_sec
                })
                current_time_sec = dep_sec

        return timeline