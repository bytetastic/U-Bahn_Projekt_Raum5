# test_skript.py
from adapter import adapter_klasse


def automatischer_testlauf():
    # Wir erstellen eine Instanz deines Adapters
    tester = adapter_klasse()

    print("🚀 STARTE AUTOMATISIERTE TESTS...\n" + "=" * 50)

    # ==========================================
    # TESTFALL 1: Einfache Fahrt (ohne Umstieg auf U1)
    # ==========================================
    print("Test 1: Langwasser Süd -> Messe (Direktfahrt, Einzelticket)")
    ergebnis1 = tester.ausfuehren_testfall(
        eingabe_start="Langwasser Süd",
        eingabe_ziel="Messe",
        eingabe_startzeit="08:00",
        eingabe_einzelfahrkarte=True,
        eingabe_sozialrabatt=False,
        eingabe_barzahlung=False
    )

    try:
        assert ergebnis1["fehler"] == False, "Es sollte kein Fehler auftreten."
        assert "U1" in ergebnis1["bahnlinien_gesamtfahrt"], "U1 muss genutzt werden."
        assert len(ergebnis1["umstieg_haltestellen"]) == 0, "Hier darf es keinen Umstieg geben!"
        assert ergebnis1["preis_endbetrag"] > 0, "Preis muss berechnet worden sein."
        print("✅ Test 1 BESTANDEN!\n")
    except AssertionError as e:
        print(f"❌ Test 1 FEHLGESCHLAGEN: {e}\n")

    # ==========================================
    # TESTFALL 2: Fahrt mit Umstieg (U1 -> U2)
    # ==========================================
    print("Test 2: Langwasser Süd -> Flughafen (Mit Umstieg am Hbf/Plärrer)")
    ergebnis2 = tester.ausfuehren_testfall(
        eingabe_start="Langwasser Süd",
        eingabe_ziel="Flughafen",
        eingabe_startzeit="09:00",
        eingabe_einzelfahrkarte=True,
        eingabe_sozialrabatt=True,  # Mit Sozialrabatt
        eingabe_barzahlung=False
    )

    try:
        assert ergebnis2["fehler"] == False, "Es sollte kein Fehler auftreten."
        # Prüfen, ob der Umstieg erkannt wurde (Hauptbahnhof oder Plärrer sind gültige Kreuzungen)
        assert "Hauptbahnhof" in ergebnis2["umstieg_haltestellen"] or "Plärrer" in ergebnis2[
            "umstieg_haltestellen"], "Falscher oder fehlender Umsteigebahnhof!"
        assert "U1" in ergebnis2["bahnlinien_gesamtfahrt"] and "U2" in ergebnis2[
            "bahnlinien_gesamtfahrt"], "Muss U1 und U2 nutzen!"
        print("✅ Test 2 BESTANDEN!\n")
    except AssertionError as e:
        print(f"❌ Test 2 FEHLGESCHLAGEN: {e}\n")

    # ==========================================
    # TESTFALL 3: Fehlerhafte Eingabe abfangen
    # ==========================================
    print("Test 3: Quatsch-Eingabe (Fehlerabfang testen)")
    ergebnis3 = tester.ausfuehren_testfall(
        eingabe_start="GibtEsNicht",  # Station existiert nicht
        eingabe_ziel="Messe",
        eingabe_startzeit="25:99",  # Ungültige Uhrzeit
        eingabe_einzelfahrkarte=True,
        eingabe_sozialrabatt=False,
        eingabe_barzahlung=False
    )

    try:
        assert ergebnis3["fehler"] == True, "Das System muss hier einen Fehler erkennen (fehler=True)!"
        print("✅ Test 3 BESTANDEN!\n")
    except AssertionError as e:
        print(f"❌ Test 3 FEHLGESCHLAGEN: {e}\n")

    print("=" * 50 + "\n🎉 ALLE TESTS ABGESCHLOSSEN!")


if __name__ == "__main__":
    automatischer_testlauf()