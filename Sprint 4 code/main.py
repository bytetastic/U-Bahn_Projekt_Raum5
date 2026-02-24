# main.py
from logik import RouteManager, TariffManager, TimetableManager
from werkzeuge import TextUtils


class TravelApp:
    def __init__(self):
        self.route_mgr = RouteManager()
        self.tariff_mgr = TariffManager()
        self.time_mgr = TimetableManager(self.route_mgr)

    def get_valid_station_input(self, prompt_text):
        while True:
            user_input = input(prompt_text)
            found_station = self.route_mgr.find_station(user_input)
            if found_station:
                print(f"   -> Erkannt als: {found_station}")
                return found_station
            else:
                print("Fehler: Station nicht gefunden.")

    def get_valid_time_input(self, prompt_text):
        while True:
            time_input = input(prompt_text)
            parsed_time = TextUtils.parse_time(time_input)
            if parsed_time:
                print(f"   -> Zeit erkannt: {parsed_time} Uhr")
                return parsed_time
            else:
                print("Fehler: Ungültiges Format (00:00 bis 23:59). Probier z.B. 9, 0930 oder 14.15")

    def run(self):
        print("=== Reiseauskunft Gesamtes Netz (Sprint 4) ===")
        start_station = self.get_valid_station_input("Startbahnhof eingeben: ")
        end_station = self.get_valid_station_input("Zielbahnhof eingeben: ")

        if start_station == end_station:
            print("Start und Ziel sind identisch.")
            return

        wunschzeit = self.get_valid_time_input("Früheste gewünschte Abfahrtszeit: ")

        path = self.route_mgr.get_shortest_path(start_station, end_station)
        if not path:
            print("Keine Route gefunden!")
            return

        timeline = self.time_mgr.calculate_travel(path, wunschzeit)
        station_count = len(path)

        print("\n--- Tarifauswahl ---")
        t_type = input("Ticketart wählen (1=Einzelticket, 2=Mehrfahrtenticket): ")
        is_multi = (t_type == '2')
        soc = input("Sozialpass? (j/n): ").lower() == 'j'
        pay = input("Bar zahlen? (j/n): ").lower() == 'j'

        final_price, category = self.tariff_mgr.calculate_ticket(station_count, is_multi, soc, pay)

        # Ausgabe generieren
        print("\n" + "=" * 50)
        print("                 REISEPLAN                 ")
        print("=" * 50)

        # Fahrgast-Rundungen
        def format_passenger(sec, round_up=False):
            m = int((sec // 60) % 60)
            h = int((sec // 3600) % 24)
            if round_up and int(sec % 60) >= 30: m += 1
            if m == 60: m = 0; h = (h + 1) % 24
            return f"{h:02d}:{m:02d}"

        start_zeit = format_passenger(timeline[0]['dep_sec'], round_up=False)
        ziel_zeit = format_passenger(timeline[-1]['arr_sec'], round_up=True)

        print(f"Von:         {start_station}")
        print(f"Nach:        {end_station}")
        print(f"Reisezeit:   {start_zeit} Uhr  ->  {ziel_zeit} Uhr")
        print("-" * 50)
        print(" DEINE ROUTE:")

        for stop in timeline:
            if stop == timeline[0]:
                print(f"  [{format_passenger(stop['dep_sec'])}] Abfahrt {stop['station']} (Linie {stop['linie']})")
            elif stop == timeline[-1]:
                print(f"  [{format_passenger(stop['arr_sec'], True)}] Ankunft {stop['station']}")
            elif stop.get("is_transfer"):
                print(
                    f"   >>> UMSTIEG am {stop['station']}: Wechsel von {stop['alte_linie']} auf {stop['linie']} (ca. {stop['transfer_min']} Min. Fußweg) <<<")
                print(f"  [{format_passenger(stop['dep_sec'])}] Abfahrt {stop['station']} (Linie {stop['linie']})")

        print("-" * 50)
        print(f"Tarif:       {category} | {final_price:.2f} €")
        print("=" * 50)


if __name__ == "__main__":
    app = TravelApp()
    app.run()