# Sprint 1: Grundlagen der Fahrplanauskunft (Modell "U-Test")

**Kontext & Szenario**

Wir modellieren den Betrieb einer neuen Teststrecke. Die Strecke besteht aus vier Stationen (A, B, C, D) und wird im Einrichtungsbetrieb (nur von A nach D) befahren.

User Story: Verkehrsbetrieb (Kunde)

"Unser Betrieb startet täglich um 05:00 Uhr an der Startstation A. Ab dann fährt alle 10 Minuten ein Zug los, bis der letzte Zug um 23:00 Uhr an Station A startet."

User Story: Fahrgast

"Als Fahrgast möchte ich eine Haltestelle und meine gewünschte Zeit eingeben, um zu erfahren, wann die nächste Bahn dort tatsächlich abfährt."

Technische Spezifikation "U-Test"

1. Die Strecke (Graphenmodell)

Die Strecke ist als gerichteter Graph definiert:

A → B: 2 Minuten

B → C: 3 Minuten

C → D: 1 Minute

Haltezeit: In diesem Modell beträgt die Verweildauer an den Stationen 0 Minuten (Ankunftszeit = Abfahrtszeit).

2. Der Takt

Erste Abfahrt (A): 05:00 Uhr

Letzte Abfahrt (A): 23:00 Uhr

Intervall: Alle 10 Minuten (05:00, 05:10, 05:20, ...)

Akzeptanzkriterien für das Inkrement (Code)

Datenstruktur: Die Strecke muss als Adjazenzliste im Code abgebildet sein.

Eingabe: Das System akzeptiert zwei Parameter:

Den Namen der Haltestelle (A, B, C oder D).

Die gewünschte Abfahrtszeit (z. B. 08:07 Uhr).

Verarbeitung:

Das System berechnet die Durchfahrtszeiten aller Züge für die gewählte Haltestelle basierend auf der Startzeit an Station A und den summierten Fahrtzeiten.

Ausgabe: * Ausgabe der nächstmöglichen tatsächlichen Abfahrtszeit, die gleich oder nach der gewünschten Zeit liegt.

Beispiel: Wer an Station B um 05:01 Uhr sein möchte, erhält die Info "05:12 Uhr" (da der erste Zug um 05:00 in A startet und um 05:02 in B ankommt – zu früh; der zweite Zug startet um 05:10 in A und ist um 05:12 in B).

Hilfestellung zur Logik

Zeitpunkt der $n$-ten Bahn an Station $X$:
$T(X) = T_{Start,A} + (n \times 10\text{ Min}) + \text{Fahrtzeit}(A \to X)$
