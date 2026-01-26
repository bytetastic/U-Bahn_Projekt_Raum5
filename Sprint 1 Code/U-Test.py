from datetime import datetime, timedelta


class UTestFahrplan:
    def __init__(self):
        self._strecke = {
            "A": [("B", 2)],
            "B": [("C", 3)],
            "C": [("D", 1)],
            "D": []
        }
        self._erster_start_A = "05:00"
        self._letzter_start_A = "23:00"
        self._intervall = 10

    def _get_fahrzeit_ab_A(self, ziel_station):
        total_minuten = 0
        aktuelle_pos = "A"

        while aktuelle_pos != ziel_station:
            nachbarn = self._strecke.get(aktuelle_pos, [])
            if not nachbarn:
                return None

            naechste_station, dauer = nachbarn[0]
            total_minuten += dauer
            aktuelle_pos = naechste_station

        return total_minuten

    def hole_naechste_abfahrt(self, station_name, wunschzeit_str):

        minuten_ab_A = self._get_fahrzeit_ab_A(station_name)
        if minuten_ab_A is None:
            return f"Fehler: Station '{station_name}' nicht im System."
        try:
            wunsch_zeit = datetime.strptime(wunschzeit_str, "%H:%M")
        except ValueError:

            return "Fehler: Ungültiges Zeitformat (Bitte HH:MM nutzen)."

        start_A = datetime.strptime(self._erster_start_A, "%H:%M")
        ende_A = datetime.strptime(self._letzter_start_A, "%H:%M")

        aktueller_start_A = start_A

        while aktueller_start_A <= ende_A:
            abfahrt_ziel = aktueller_start_A + timedelta(minutes=minuten_ab_A)

            if abfahrt_ziel >= wunsch_zeit:
                return abfahrt_ziel.strftime("%H:%M")

            aktueller_start_A += timedelta(minutes=self._intervall)

        return "Leider fährt heute kein Zug mehr."


def main():
    system = UTestFahrplan()
    print("=== Auskunft - Abfahrtszeiten ===")
    station = input("Haltestelle (A, B, C, D): ").upper().strip()
    uhrzeit = input("Gewünschte Zeit (z.B. 08:07): ").strip()
    ergebnis = system.hole_naechste_abfahrt(station, uhrzeit)

    if "Fehler" in ergebnis:
        print(ergebnis)

    else:
        print(f"\nDie nächste Bahn fährt an Station {station} um {ergebnis} Uhr ab.")


if __name__ == "__main__":
    main()