# werkzeuge.py

class TextUtils:
    """
    Hilfsklasse für Normalisierung und Mapping gemäß User Story 3.1
    """

    @staticmethod
    def normalize(text):
        if not text:
            return ""

        # 1. Mapping (Kürzel ersetzen)
        text = text.replace("Hbf.", "Hauptbahnhof")
        text = text.replace("Str.", "Straße")
        text = text.replace("Fr.-", "Friedrich-")

        # 2. Trimmen und Kleinschreibung
        text = text.strip().lower()

        # 3. Vereinheitlichung Sonderzeichen
        text = text.replace("-", " ")

        # 4. Ersetzung von Umlauten und ß
        text = text.replace("ä", "ae")
        text = text.replace("ö", "oe")
        text = text.replace("ü", "ue")
        text = text.replace("ß", "ss")

        return text