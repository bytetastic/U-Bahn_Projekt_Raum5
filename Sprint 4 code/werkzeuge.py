# werkzeuge.py
import re

class TextUtils:
    """
    Hilfsklasse für Normalisierung (US 3.1) und Uhrzeit-Parsing (US 4.4)
    """

    @staticmethod
    def normalize(text):
        if not text:
            return ""
        text = text.strip().lower()
        text = text.replace("hbf.", "hauptbahnhof")
        text = text.replace("hbf", "hauptbahnhof")
        text = text.replace("str.", "straße")
        text = text.replace("fr.-", "friedrich-")
        text = text.replace("-", " ")
        text = text.replace("ä", "ae")
        text = text.replace("ö", "oe")
        text = text.replace("ü", "ue")
        text = text.replace("ß", "ss")
        return text

    @staticmethod
    def parse_time(time_str):
        """
        US 4.4: Akzeptiert diverse Formate (9, 09, 9:30, 09.30, 9,3, 0930, 9 30)
        und gibt einen standardisierten String 'HH:MM' zurück.
        """
        time_str = str(time_str).strip()
        if not time_str:
            return None

        # Fall 1: Nur 1 oder 2 Ziffern (z.B. "9" oder "14" -> Volle Stunde)
        if time_str.isdigit() and len(time_str) <= 2:
            h = int(time_str)
            m = 0
        # Fall 2: 3 oder 4 Ziffern ohne Trenner (z.B. "930" oder "0930")
        elif time_str.isdigit() and len(time_str) in [3, 4]:
            h = int(time_str[:-2])
            m = int(time_str[-2:])
        # Fall 3: Mit irgendwelchen Trennzeichen (Punkt, Komma, Doppelpunkt, Leerzeichen)
        else:
            parts = re.split(r'[:.,\s]+', time_str)
            if len(parts) == 1:
                h = int(parts[0])
                m = 0
            elif len(parts) >= 2:
                h = int(parts[0])
                m = int(parts[1]) if parts[1] else 0
            else:
                return None

        # Logische Validierung
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"
        return None