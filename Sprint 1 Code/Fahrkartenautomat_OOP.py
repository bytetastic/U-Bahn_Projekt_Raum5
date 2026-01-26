import sys
import time
from datetime import datetime

try:
    from colorama import init, Fore, Style

    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

try:
    import winsound

    HAS_SOUND = True
except (ImportError, AttributeError):
    HAS_SOUND = False


class UbahnNetz:
    def __init__(self):
        self.netzdaten = {
            "Fürth Hbf.": ["Jakobinenstr."], "Jakobinenstr.": ["Fürth Hbf.", "Stadtgrenze"],
            "Stadtgrenze": ["Jakobinenstr.", "Muggenhof"], "Muggenhof": ["Stadtgrenze", "EberhardsHof"],
            "EberhardsHof": ["Muggenhof", "Maximilianstr."], "Maximilianstr.": ["EberhardsHof", "Bärenschanze"],
            "Bärenschanze": ["Maximilianstr.", "Gostenhof"], "Gostenhof": ["Bärenschanze", "Plärrer"],
            "Gustav-Adolf-Str.": ["Sündersbühl"], "Sündersbühl": ["Gustav-Adolf-Str.", "Rothenburger Str."],
            "Plärrer": ["Rothenburger Str.", "Gostenhof", "Weißer Turm", "Opernhaus"],
            "Rothenburger Str.": ["Sündersbühl", "Plärrer", "St. Leonhard"],
            "Weißer Turm": ["Plärrer", "Lorenzkirche"], "Lorenzkirche": ["Weißer Turm", "Hauptbahnhof"],
            "Opernhaus": ["Plärrer", "Hauptbahnhof"],
            "Hauptbahnhof": ["Lorenzkirche", "Opernhaus", "Aufseßplatz", "Wöhrder Wiese"],
            "St. Leonhard": ["Rothenburger Str.", "Schweinau"], "Schweinau": ["St. Leonhard", "Hohe Marter"],
            "Hohe Marter": ["Schweinau", "Röthenbach"], "Röthenbach": ["Hohe Marter"],
            "Wöhrder Wiese": ["Hauptbahnhof", "Rathenauplatz"],
            "Rathenauplatz": ["Wöhrder Wiese", "Rennweg", "Maxfeld"],
            "Rennweg": ["Rathenauplatz", "Schoppershof"], "Schoppershof": ["Rennweg", "Nordostbahnhof"],
            "Nordostbahnhof": ["Schoppershof", "Herrnhütte"], "Herrnhütte": ["Nordostbahnhof", "Ziegelstein"],
            "Ziegelstein": ["Herrnhütte", "Flughafen"], "Flughafen": ["Ziegelstein"],
            "Aufseßplatz": ["Hauptbahnhof", "Maffeiplatz"], "Maffeiplatz": ["Aufseßplatz", "Frankenstr."],
            "Frankenstr.": ["Maffeiplatz", "Hasenbuck"], "Hasenbuck": ["Frankenstr.", "Bauernfeindstr."],
            "Bauernfeindstr.": ["Hasenbuck", "Messe"], "Messe": ["Bauernfeindstr.", "Langwasser Nord"],
            "Langwasser Nord": ["Messe", "Scharfreiterring"],
            "Scharfreiterring": ["Langwasser Nord", "Langwasser Mitte"],
            "Langwasser Mitte": ["Scharfreiterring", "Gemeinschaftshaus"],
            "Gemeinschaftshaus": ["Langwasser Mitte", "Langwasser Süd"], "Langwasser Süd": ["Gemeinschaftshaus"],
            "Fr.-Ebert-Platz": ["Kaulbachplatz"], "Kaulbachplatz": ["Fr.-Ebert-Platz", "Maxfeld"],
            "Maxfeld": ["Kaulbachplatz", "Rathenauplatz"]
        }
        self.alle_stationen = list(self.netzdaten.keys())

    def ist_station_gueltig(self, name):
        return name in self.alle_stationen

    def finde_route(self, start, ziel):
        if not self.ist_station_gueltig(start) or not self.ist_station_gueltig(ziel): return None
        if start == ziel: return [start]
        warteschlange = [(start, [start])]
        besucht = {start}
        while warteschlange:
            akt, pfad = warteschlange.pop(0)
            for nachbar in self.netzdaten.get(akt, []):
                if nachbar == ziel: return pfad + [ziel]
                if nachbar not in besucht:
                    besucht.add(nachbar)
                    warteschlange.append((nachbar, pfad + [nachbar]))
        return None


class Fahrkartenrechner:
    def __init__(self):
        self.RABATT_SOZIAL = 0.20
        self.GEBUEHR_BAR = 0.15

    def berechne_preis(self, anzahl, optionen):
        basis = 1.00 if anzahl <= 3 else (1.20 if anzahl <= 8 else 1.50)
        preis = basis * 1.10
        mods = [f"Einzelticket-Zuschlag (+10%): +{basis * 0.10:.2f} €"]

        if optionen.get("sozial"):
            r = preis * self.RABATT_SOZIAL
            preis -= r
            mods.append(f"Sozialrabatt (-20%): -{r:.2f} €")
        if optionen.get("bar"):
            g = preis * self.GEBUEHR_BAR
            preis += g
            mods.append(f"Bargeld-Zahlgebühr (+15%): +{g:.2f} €")
        return round(preis, 2), basis, mods

    def erstelle_quittung(self, d):
        def c(color_obj, text):
            if HAS_COLOR: return f"{color_obj}{text}{Style.RESET_ALL}"
            return text

        print("\n" + "=" * 50)
        print(c(Fore.WHITE + Style.BRIGHT if HAS_COLOR else "", "🎫 IHR FAHRSCHEIN (Quittung) 🎫"))
        print("=" * 50)
        print(f"Fahrt: {d['start']} nach {d['ziel']}")
        print(f"Distanz: {d['distanz']} Stationen")
        print("-" * 50)
        print(c(Fore.CYAN if HAS_COLOR else "", "Route:"))
        print(" -> ".join(d['route']))
        print("-" * 50)
        print(f"Basispreis: {d['basis']:.2f} €")
        for m in d['mods']:
            if HAS_COLOR:
                col = Fore.GREEN if "-" in m or "rabatt" in m.lower() else Fore.RED
                print("  " + c(col, m))
            else:
                print(f"  {m}")
        print("-" * 50)
        print(c(Fore.WHITE + Style.BRIGHT if HAS_COLOR else "", f"FINALER PREIS: {d['endpreis']:.2f} €"))
        print(f"Gültig: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("=" * 50)


class Fahrkartenautomat:
    def __init__(self):
        self._netz = UbahnNetz()
        self._rechner = Fahrkartenrechner()

    def _play_sound(self, s_type):
        # Wenn kein Sound-Modul oder falsches OS, tu einfach gar nichts.
        if not HAS_SOUND: return
        try:
            if s_type == "error":
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
            elif s_type == "click":
                winsound.Beep(800, 50)
        except:
            pass

    def _spinner(self, text):
        if not HAS_COLOR:
            print(f"{text}...")
            return
        syms = ['|', '/', '-', '\\']
        for i in range(10):
            sys.stdout.write(f"\r{Fore.YELLOW}{text} {syms[i % 4]}")
            sys.stdout.flush()
            time.sleep(0.1)
        print("\r" + " " * 40 + "\r")

    def starten(self):
        print("\n" + "=" * 50)
        title = "🚆 Intelligenter Fahrkartenautomat (OOP)"
        if HAS_COLOR:
            print(Fore.GREEN + Style.BRIGHT + title)
        else:
            print(title)
        print("=" * 50)

        start = self._eingabe_station("Bitte Startstation eingeben: ")
        ziel = self._eingabe_station("Bitte Zielstation eingeben: ")

        self._spinner("Berechne Route")
        route = self._netz.finde_route(start, ziel)

        if not route:
            print("❌ Fehler: Keine Route gefunden.")
            return

        sozial = self._erfrage_ja_nein("Haben Sie Anspruch auf Sozialrabatt?")
        bar = self._erfrage_ja_nein("Möchten Sie Bar bezahlen?")

        preis, basis, mods = self._rechner.berechne_preis(len(route) - 1, {"sozial": sozial, "bar": bar})

        self._rechner.erstelle_quittung({
            "start": start, "ziel": ziel, "distanz": len(route) - 1,
            "route": route, "basis": basis, "mods": mods, "endpreis": preis
        })

    def _eingabe_station(self, prompt):
        while True:
            s = input(prompt).strip()
            if self._netz.ist_station_gueltig(s):
                self._play_sound("click")
                return s
            print("❌ Fehler: Unbekannte Station!")
            self._play_sound("error")

    def _erfrage_ja_nein(self, frage):
        while True:
            antwort = input(f"{frage} (j/n): ").strip().lower()
            if antwort in ('j', 'n'):
                self._play_sound("click")
                return antwort == 'j'
            print("❌ Bitte nur 'j' oder 'n' eingeben.")
            self._play_sound("error")


if __name__ == "__main__":
    Fahrkartenautomat().starten()