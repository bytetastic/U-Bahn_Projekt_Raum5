from datetime import datetime, timedelta
from netzplan import Route
from ausgabe import UI


class FahrplanApp:
    def __init__(self):
        self.route = Route()
        self.ui = UI()

        self.betriebsstart = datetime.strptime("05:00", "%H:%M")
        self.takt = 10  # Minuten

    def run(self):
        self.ui.zeige_header()

        # 1. Start-Station abfragen
        eingabe = self.ui.frage_nach_station("Start-Haltestelle: ")
        start_idx, start_name = self.route.finde_station(eingabe)

        if start_idx is None:
            self.ui.zeige_fehler("Station nicht gefunden.")
            return
        self.ui.zeige_korrektur_info(eingabe, start_name)

        # 2. Ziel-Station abfragen
        eingabe = self.ui.frage_nach_station("Ziel-Haltestelle: ")
        ziel_idx, ziel_name = self.route.finde_station(eingabe)

        if ziel_idx is None:
            self.ui.zeige_fehler("Ziel nicht gefunden.")
            return
        self.ui.zeige_korrektur_info(eingabe, ziel_name)

        # Gleicher Start/Ziel Check
        if start_idx == ziel_idx:
            self.ui.zeige_fehler("Start und Ziel sind identisch.")
            return

        # 3. Richtung bestimmen
        if start_idx < ziel_idx:
            richtung = "hin"
            self.ui.zeige_richtung("Fürth Hbf.")
        else:
            richtung = "rueck"
            self.ui.zeige_richtung("Langwasser Süd")

        # 4. Zeit abfragen
        wunschzeit = self.ui.frage_nach_zeit()
        if wunschzeit is None:
            return

        # Schritt A: Wann kommt der allererste Zug an der Station an?
        offset_sekunden = self.route.berechne_zeit_bis_station(start_idx, richtung)
        erste_bahn = self.betriebsstart + timedelta(seconds=offset_sekunden)

        # Schritt B: Taktung berechnen
        if wunschzeit <= erste_bahn:
            abfahrt = erste_bahn
        else:
            # Wie viel Zeit ist seit der ersten Bahn vergangen?
            differenz = (wunschzeit - erste_bahn).total_seconds()
            takt_sekunden = self.takt * 60

            # Anzahl der Takte berechnen (Ganzzahldivision)
            takte_anzahl = int(differenz / takt_sekunden)

            # Wenn wir auch nur 1 Sekunde über dem Takt sind, müssen wir den nächsten nehmen
            if differenz % takt_sekunden > 0:
                takte_anzahl += 1

            abfahrt = erste_bahn + timedelta(minutes=takte_anzahl * self.takt)

        if abfahrt.hour < 4:  # Einfacher Check für Betriebsschluss (nächster Tag)
            self.ui.zeige_fehler("Betriebsschluss! Heute fährt keine Bahn mehr.")
        else:
            wartezeit = int((abfahrt - wunschzeit).total_seconds() / 60)
            self.ui.zeige_ergebnis(start_name, ziel_name, abfahrt, wartezeit)


# Das Programm starten
if __name__ == "__main__":
    app = FahrplanApp()
    app.run()