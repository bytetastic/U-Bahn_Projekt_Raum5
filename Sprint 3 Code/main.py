# main.py
import datetime
from logik import RouteManager, TariffManager


class TravelApp:
    """
    Hauptklasse für die Interaktion (User Story 3.3)
    """

    def __init__(self):
        self.route_mgr = RouteManager()
        self.tariff_mgr = TariffManager()

    def get_valid_station_input(self, prompt_text):
        while True:
            user_input = input(prompt_text)
            found_station = self.route_mgr.find_station(user_input)

            if found_station:
                print(f"   -> Erkannt als: {found_station}")
                return found_station
            else:
                print(
                    "Fehler: Die Eingabe war nicht eindeutig oder die Station existiert nicht. Bitte wiederholen.")

    def run(self):
        print("=== Kurzstrecke Projekt Part 2 ===")

        # 1. Start und Ziel erfassen
        start_station = self.get_valid_station_input("Startbahnhof eingeben: ")
        end_station = self.get_valid_station_input("Zielbahnhof eingeben: ")

        if start_station == end_station:
            print("Start und Ziel sind identisch. Keine Fahrt nötig.")
            return

        # 2. Entfernungsberechnung
        start_idx = self.route_mgr.get_station_index(start_station)
        end_idx = self.route_mgr.get_station_index(end_station)

        station_count = abs(end_idx - start_idx)

        # Fahrzeit: Annahme 2 Minuten pro Station
        travel_minutes = station_count * 2
        current_time = datetime.datetime.now()
        arrival_time = current_time + datetime.timedelta(minutes=travel_minutes)

        # 3. Tarif-Abfrage
        print("\n--- Tarifauswahl ---")

        # Ticketart
        while True:
            t_type = input("Ticketart wählen (1=Einzelticket, 2=Mehrfahrtenticket): ")
            if t_type in ['1', '2']:
                is_multi = (t_type == '2')
                break
            print("Bitte 1 oder 2 eingeben.")

        # Sozialrabatt
        while True:
            soc = input("Besitzen Sie einen Sozialpass? (j/n): ").lower()
            if soc in ['j', 'n']:
                has_social = (soc == 'j')
                break

        # Zahlart
        while True:
            pay = input("Möchten Sie bar zahlen? (j/n): ").lower()
            if pay in ['j', 'n']:
                pays_cash = (pay == 'j')
                break

        # 4. Berechnung
        final_price, category = self.tariff_mgr.calculate_ticket(station_count, is_multi, has_social, pays_cash)
        ticket_name = "Mehrfahrtenticket" if is_multi else "Einzelticket"

        # 5. Ausgabe / Zusammenfassung
        print("\n" + "=" * 30)
        print("       Kurzstrecke Projekt Part 2 / Sprint 3      ")
        print("=" * 30)
        print(f"Zeitstempel: {current_time.strftime('%d.%m.%Y %H:%M')}")
        print(f"Start:       {start_station}")
        print(f"Ziel:        {end_station}")
        print(f"Stationen:   {station_count} ({category})")
        print("-" * 30)
        print(f"Abfahrt:     {current_time.strftime('%H:%M')} Uhr")
        print(f"Ankunft:     {arrival_time.strftime('%H:%M')} Uhr (ca.)")
        print("-" * 30)
        print(f"Tarif:       {ticket_name}")
        if has_social: print("             (Sozialrabatt angewandt)")
        if pays_cash:  print("             (Barzahlungsaufschlag)")
        print(f"ENDPREIS:    {final_price:.2f} €")
        print("=" * 30)


if __name__ == "__main__":
    app = TravelApp()
    app.run()