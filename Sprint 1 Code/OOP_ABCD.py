from datetime import datetime, timedelta


class Strecke:

    def __init__(self):
        self.stationen_daten = {
            "A": 0,  # Start
            "B": 2,  # 2 Min ab A
            "C": 2 + 3,  # 5 Min ab A
            "D": 2 + 3 + 1  # 6 Min ab A
        }

    def gib_fahrtzeit_ab_start(self, station_name):
        if station_name in self.stationen_daten:
            minuten = self.stationen_daten[station_name]
            return timedelta(minutes=minuten)
        else:
            return None



class Fahrplan:
    def __init__(self, start_uhrzeit, end_uhrzeit, takt_minuten, strecken_objekt):
        self.start = datetime.strptime(start_uhrzeit, "%H:%M")
        self.ende = datetime.strptime(end_uhrzeit, "%H:%M")
        self.takt = timedelta(minutes=takt_minuten)


        self.strecke = strecken_objekt

    def suche_naechste_bahn(self, station, user_zeit_str):
        # 1. User-Eingabe verstehen
        wunsch_zeit = datetime.strptime(user_zeit_str, "%H:%M")

        # 2. Fragen wir die Strecke: Wie lange braucht der Zug bis zur Station?
        dauer_bis_station = self.strecke.gib_fahrtzeit_ab_start(station)

        if dauer_bis_station is None:
            return "Fehler: Unbekannte Station!"

        aktueller_zug = self.start

        while aktueller_zug <= self.ende:
            abfahrt_an_station = aktueller_zug + dauer_bis_station

            if abfahrt_an_station >= wunsch_zeit:
                return f"Nächste Bahn ab {station}: {abfahrt_an_station.strftime('%H:%M')} Uhr"


            aktueller_zug = aktueller_zug + self.takt

        return "Kein Zug mehr heute."


meine_u_bahn_strecke = Strecke()

mein_fahrplan = Fahrplan("05:00", "23:00", 10, meine_u_bahn_strecke)

print("--- U-Test System (OOP) ---")
eingabe_ort = input("Haltestelle (A, B, C, D): ").upper()
eingabe_zeit = input("Zeit (HH:MM): ")

ergebnis = mein_fahrplan.suche_naechste_bahn(eingabe_ort, eingabe_zeit)
print(ergebnis)