# main.py
import datetime
from logik import RouteManager, TariffManager, TimetableManager


class TravelApp:
    """
    Hauptklasse für die Interaktion (User Story 3.3 & Sprint 2)
    """

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
                print("Fehler: Die Eingabe war nicht eindeutig oder die Station existiert nicht. Bitte wiederholen.")

    def get_valid_time_input(self, prompt_text):
        while True:
            time_input = input(prompt_text)
            try:
                datetime.datetime.strptime(time_input, "%H:%M")
                return time_input
            except ValueError:
                print("Fehler: Bitte die Zeit im Format HH:MM eingeben (z.B. 08:35).")

    def run(self):
        print("=== Kurzstrecke Projekt 2 Sprint 3 ===")

        # 1. Start, Ziel und Zeit erfassen
        start_station = self.get_valid_station_input("Startbahnhof eingeben: ")
        end_station = self.get_valid_station_input("Zielbahnhof eingeben: ")

        if start_station == end_station:
            print("Start und Ziel sind identisch. Keine Fahrt nötig.")
            return

        wunschzeit = self.get_valid_time_input("Früheste gewünschte Abfahrtszeit (HH:MM): ")

        # 2. Entfernungsberechnung und Richtung
        start_idx = self.route_mgr.get_station_index(start_station)
        end_idx = self.route_mgr.get_station_index(end_station)
        station_count = abs(end_idx - start_idx)

        richtung = "Richtung Langwasser Süd" if start_idx < end_idx else "Richtung Fürth Hardhöhe"

        # 3. Fahrplan-Berechnung (SOFORTIGE AUSGABE)
        dep_rounded, arr_exact, arr_rounded = self.time_mgr.calculate_travel(start_idx, end_idx, wunschzeit)
        print(f"   -> Nächste Abfahrt ab {start_station}: {dep_rounded} Uhr ({richtung})")

        # 4. Tarif-Abfrage
        print("\n--- Tarifauswahl ---")
        while True:
            t_type = input("Ticketart wählen (1=Einzelticket, 2=Mehrfahrtenticket): ")
            if t_type in ['1', '2']:
                is_multi = (t_type == '2')
                break

        while True:
            soc = input("Besitzen Sie einen Sozialpass? (j/n): ").lower()
            if soc in ['j', 'n']:
                has_social = (soc == 'j')
                break

        while True:
            pay = input("Möchten Sie bar zahlen? (j/n): ").lower()
            if pay in ['j', 'n']:
                pays_cash = (pay == 'j')
                break

        # 5. Preis-Berechnung
        final_price, category = self.tariff_mgr.calculate_ticket(station_count, is_multi, has_social, pays_cash)
        ticket_name = "Mehrfahrtenticket" if is_multi else "Einzelticket"
        current_time_str = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')

        # 6. Ausgabe / Zusammenfassung
        print("\n" + "=" * 45)
        print("             REISEZUSAMMENFASSUNG             ")
        print("=" * 45)
        print(f"Zeitstempel: {current_time_str}")
        print(f"Von:         {start_station}")
        print(f"Nach:        {end_station}")
        print(f"Fahrt:       {richtung} ({station_count} Stationen)")
        print("-" * 45)
        print(f"Wunschzeit:  {wunschzeit} Uhr")
        print(f"Abfahrt:     {dep_rounded} Uhr")
        print(f"Ankunft:     {arr_exact} (aufgerundet: {arr_rounded} Uhr)")
        print("-" * 45)
        print(f"Tarif:       {category} - {ticket_name}")
        if has_social: print("             (Sozialrabatt -20%)")
        if pays_cash:  print("             (Barzahlungsaufschlag +15%)")
        print(f"ENDPREIS:    {final_price:.2f} €")
        print("=" * 45)


if __name__ == "__main__":
    app = TravelApp()
    app.run()