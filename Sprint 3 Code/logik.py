# logik.py
import difflib
from werkzeuge import TextUtils


class TariffManager:
    """
    Behandelt die Preislogik gemäß User Story 3.2
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

        # Zuschläge und Rabatte
        if not is_multi_ticket: price *= 1.10
        if has_social_card: price *= 0.80
        if pay_cash: price *= 1.15

        return round(price, 2), category


class RouteManager:
    """
    Verwaltet die Stationen und die Suche (User Story 3.1)
    """

    def __init__(self):
        # Exakte Liste gemäß Vorgabe (Index 0 = Langwasser Süd, Index 22 = Fürth Hbf.)
        self.stations = [
            "Langwasser Süd",
            "Gemeinschaftshaus",
            "Langwasser Mitte",
            "Scharfreiterring",
            "Langwasser Nord",
            "Messe",
            "Bauernfeindstraße",
            "Hasenbuck",
            "Frankenstraße",
            "Maffeiplatz",
            "Aufseßplatz",
            "Hauptbahnhof",
            "Lorenzkirche",
            "Weißer Turm",
            "Plärrer",
            "Gostenhof",
            "Bärenschanze",
            "Maximilianstraße",
            "Eberhardshof",
            "Muggenhof",
            "Stadtgrenze",
            "Jakobinenstraße",
            "Fürth Hbf."
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
    Fahrplan-Logik gemäß Sprint 2 (10-Min-Takt, Haltezeiten)
    """

    def __init__(self, route_mgr):
        self.route_mgr = route_mgr
        self.hubs = ["Hauptbahnhof", "Plärrer", "Fürth Hbf.", "Langwasser Süd"]

    def get_stop_time(self, station_name):
        # 60 Sekunden für Hauptknoten und Endstationen, sonst 30
        return 60 if station_name in self.hubs else 30

    def calculate_travel(self, start_idx, end_idx, wunschzeit_str):
        # 1. Wunschzeit parsen (z.B. "08:02" zu Sekunden umwandeln)
        hours, minutes = map(int, wunschzeit_str.split(':'))
        wunsch_sec = hours * 3600 + minutes * 60

        # Richtung (1 = Richtung Fürth Hbf., -1 = Richtung Langwasser Süd)
        direction = 1 if start_idx < end_idx else -1

        # 2. passender Takt (vereinfacht: Züge fahren ab 05:00 alle 10 Min)
        start_of_day_sec = 5 * 3600  # 05:00 Uhr in Sekunden

        # Theoretische Abfahrt am Startbahnhof bestimmen
        if wunsch_sec < start_of_day_sec:
            departure_sec = start_of_day_sec
        else:
            # Auf den nächsten 10-Minuten-Takt (600 Sekunden) aufrunden
            elapsed = wunsch_sec - start_of_day_sec
            remainder = elapsed % 600
            if remainder == 0:
                departure_sec = wunsch_sec
            else:
                departure_sec = wunsch_sec + (600 - remainder)

        # 3. Ankunftszeit berechnen (Fahrt zum Ziel simulieren)
        arrival_sec = departure_sec
        current_idx = start_idx

        while current_idx != end_idx:
            # Wir fahren zur nächsten Station
            current_idx += direction
            # Annahme für die reine Fahrzeit (ca. 105s zwischen Stationen)
            arrival_sec += 105

            # Haltezeit addieren (außer an der allerletzten Station der Reise)
            if current_idx != end_idx:
                arrival_sec += self.get_stop_time(self.route_mgr.stations[current_idx])

        # 4. Formatierung und Rundung für die Ausgabe
        def format_time(total_seconds):
            h = int((total_seconds // 3600) % 24)
            m = int((total_seconds % 3600) // 60)
            s = int(total_seconds % 60)

            # Mathematisches Aufrunden ab 30 Sekunden
            rounded_m = m + 1 if s >= 30 else m
            rounded_h = h
            if rounded_m == 60:
                rounded_m = 0
                rounded_h = (h + 1) % 24

            exact_str = f"{h:02d}:{m:02d}:{s:02d}"
            rounded_str = f"{rounded_h:02d}:{rounded_m:02d}"
            return exact_str, rounded_str

        dep_exact, dep_rounded = format_time(departure_sec)
        arr_exact, arr_rounded = format_time(arrival_sec)

        return dep_rounded, arr_exact, arr_rounded