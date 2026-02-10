from datetime import datetime

class UI:
    def zeige_header(self):
        print("\n=== U1 Fahrplanauskunft (Sprint 2) ===")

    def frage_nach_station(self, text):
        return input(text)

    def frage_nach_zeit(self):
        zeit_input = input("Gewünschte Abfahrtszeit (HH:MM): ")
        try:
            return datetime.strptime(zeit_input, "%H:%M")
        except ValueError:
            print("Ungültiges Zeitformat! Bitte HH:MM eingeben.")
            return None

    def zeige_fehler(self, nachricht):
        print(f"FEHLER: {nachricht}")

    def zeige_korrektur_info(self, eingabe, gefunden):
        # Zeigt eine Info, falls die Autokorrektur zugeschlagen hat
        if eingabe.lower() != gefunden.lower():
            print(f"   (Meinten Sie '{gefunden}'? Übernehme diesen Wert.)")

    def zeige_richtung(self, endstation):
        print(f"-> Richtung: {endstation}")

    def zeige_ergebnis(self, start, ziel, abfahrt, wartezeit):
        print(f"\n--- Ihre Verbindung ---")
        print(f"Von:       {start}")
        print(f"Nach:      {ziel}")
        # Sekunden entfernen für saubere Anzeige
        uhrzeit_str = abfahrt.strftime('%H:%M')
        print(f"Abfahrt:   {uhrzeit_str} Uhr")
        print(f"Wartezeit: {wartezeit} Minute(n)")