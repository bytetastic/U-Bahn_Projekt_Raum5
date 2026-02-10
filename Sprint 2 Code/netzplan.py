import difflib
from datetime import timedelta


class Route:
    def __init__(self):
        # 1. Alle Stationen der U1 in korrekter Reihenfolge
        self.stationen = [
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

        # 2. Fahrtzeiten zwischen den Stationen (Index 0 = Zeit von Station 0 zu 1)
        self.fahrtzeiten = [3, 2, 2, 3, 2, 3, 2, 2, 2, 1, 2, 2, 3, 2, 2, 1, 2, 2, 2, 3, 2, 3]

        # 3. Haltezeiten definieren
        # Dictionary Comprehension: Setzt erst mal alle auf 30
        self.haltezeiten = {station: 30 for station in self.stationen}

        # Ausnahmen überschreiben (Knotenpunkte & Endhaltestellen)
        self.haltezeiten["Langwasser Süd"] = 60
        self.haltezeiten["Hauptbahnhof"] = 60
        self.haltezeiten["Plärrer"] = 60
        self.haltezeiten["Fürth Hbf."] = 60

    def finde_station(self, eingabe):
        """
        Sucht eine Station und gleicht mit difflib Eingabe von User zu 60% ab.
        Rückgabe: (Index, Echter_Name) oder (None, None) falls nicht gefunden.
        """
        suche = eingabe.strip().lower()

        # A) Exakte Suche (ignoriert Groß-/Kleinschreibung)
        for i, name in enumerate(self.stationen):
            if name.lower() == suche:
                return i, name

        # B) Autokorrektur (Fuzzy Search)
        # Sucht den ähnlichsten Begriff (60% Ähnlichkeit nötig)
        treffer = difflib.get_close_matches(eingabe, self.stationen, n=1, cutoff=0.6)
        if treffer:
            gefunden = treffer[0]
            return self.stationen.index(gefunden), gefunden

        return None, None

    def berechne_zeit_bis_station(self, ziel_index, richtung):
        """
        Berechnet die Sekunden, die der Zug vom Start (05:00 Uhr)
        bis zur Abfahrt an der Ziel-Station braucht.
        """
        sekunden = 0

        if richtung == "hin":
            # Wir fahren von Langwasser (Index 0) Richtung Fürth
            for i in range(ziel_index):
                sekunden += self.fahrtzeiten[i] * 60  # Fahrtzeit addieren

                # Haltezeit addieren (weil der Zug an der Station hält, bevor er weiterfährt)
                # Wir addieren den Halt der Station i+1 (wo wir ankommen)
                # Wichtig: Nur solange wir nicht VOR dem Start sind
                if i < ziel_index:
                    station_name = self.stationen[i + 1]
                    sekunden += self.haltezeiten[station_name]

        else:  # Rückfahrt
            # 1. Erstmal die komplette Hinfahrt bis Fürth berechnen
            index_fuerth = len(self.stationen) - 1
            zeit_hin = self.berechne_zeit_bis_station(index_fuerth, "hin")

            # 2. Wendezeit draufrechnen (60 sek)
            sekunden = zeit_hin + 60

            # 3. Jetzt die Strecke rückwärts addieren
            # Wir starten beim letzten Index und zählen runter bis zum ziel_index
            for i in range(index_fuerth - 1, ziel_index - 1, -1):
                sekunden += self.fahrtzeiten[i] * 60

                # Haltezeit an der aktuellen Station draufrechnen
                station_name = self.stationen[i]
                sekunden += self.haltezeiten[station_name]

        return sekunden