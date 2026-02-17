# logik.py
import difflib
from werkzeuge import TextUtils

class TariffManager:
    """
    Behandelt die Preislogik gemäß User Story 3.2
    """
    def calculate_ticket(self, stations_count, is_multi_ticket, has_social_card, pay_cash):
        # Ermittlung der Kategorie
        if stations_count <= 3:
            category = "Kurzstrecke"
            base_single = 1.50
            base_multi = 5.00
        elif stations_count <= 8:
            category = "Mittelstrecke"
            base_single = 2.00
            base_multi = 7.00
        else:
            category = "Langstrecke"
            base_single = 3.00
            base_multi = 10.00

        # Basispreis wählen
        price = base_multi if is_multi_ticket else base_single

        # 1. Ticketart-Zuschlag für Einzeltickets (+10%)
        if not is_multi_ticket:
            price = price * 1.10

        # 2. Sozialrabatt (-20%)
        if has_social_card:
            price = price * 0.80

        # 3. Zahlart-Zuschlag (+15% bei Barzahlung)
        if pay_cash:
            price = price * 1.15

        return round(price, 2), category

class RouteManager:
    """
    Verwaltet die Stationen und die Suche (User Story 3.1)
    """
    def __init__(self):
        # U1 Nürnberg/Fürth Stationen
        self.stations = [
            "Fürth Hardhöhe", "Fürth Klinikum", "Fürth Stadthalle", "Fürth Rathaus",
            "Fürth Hauptbahnhof", "Jakobinenstraße", "Stadtgrenze", "Muggenhof",
            "Eberhardshof", "Maximilianstraße", "Bärenschanze", "Gostenhof",
            "Plärrer", "Weißer Turm", "Lorenzkirche", "Hauptbahnhof",
            "Aufseßplatz", "Maffeiplatz", "Frankenstraße", "Hasenbuck",
            "Bauernfeindstraße", "Messe", "Langwasser Nord", "Scharfreiterring",
            "Langwasser Mitte", "Langwasser Süd"
        ]

    def find_station(self, user_input):
        normalized_input = TextUtils.normalize(user_input)
        best_match = None
        best_ratio = 0.0

        for station in self.stations:
            # Station für Vergleich ebenfalls normalisieren
            normalized_station = TextUtils.normalize(station)

            # Fuzzy Matching
            matcher = difflib.SequenceMatcher(None, normalized_input, normalized_station)
            ratio = matcher.ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = station

        # Schwellenwert prüfen (80%)
        if best_ratio >= 0.8:
            return best_match
        else:
            return None

    def get_station_index(self, station_name):
        return self.stations.index(station_name)