# werkzeuge.py

class TextUtils:
    """
    Hilfsklasse für Normalisierung und Mapping
    """

    @staticmethod
    def normalize(text):
        if not text:
            return ""

        # 2. Trimmen und Kleinschreibung
        text = text.strip().lower()

        text = text.replace("hbf.", "hauptbahnhof")
        text = text.replace("hbf", "hauptbahnhof")  # Fängt Eingaben OHNE Punkt ab!

        text = text.replace("str.", "straße")
        text = text.replace("fr.-", "friedrich-")
        # 3. Vereinheitlichung Sonderzeichen
        text = text.replace("-", " ")

        # 4. Ersetzung von Umlauten und ß
        text = text.replace("ä", "ae")
        text = text.replace("ö", "oe")
        text = text.replace("ü", "ue")
        text = text.replace("ß", "ss")

        return text