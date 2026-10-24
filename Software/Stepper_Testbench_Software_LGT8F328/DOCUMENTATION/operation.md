# Bedienung · Software 2.1

| Situation | Eingabe | Verhalten |
| --- | --- | --- |
| Einschalten | Stick zentriert lassen | Kalibrierung; anschließend LOCK. Es startet keine Fahrt. |
| Freigeben | Zentriert 1,1 s drücken; dann loslassen | ARM. Der Stick muss während der gesamten Haltezeit zentriert bleiben. |
| Richtung / Tempo | X links/rechts und Y auf/ab | X wählt die Richtung. Der Betrag der Y-Auslenkung bestimmt die Geschwindigkeit. |
| Dauerlauf beenden | X oder Y in die Mitte | Der Sollwert fährt über die Bremsrampe auf null. |
| Fahrt starten | Im Modus Fahrt beide Achsen auslenken | Eine Fahrt wird mit dem dabei gewählten Tempo gestartet; danach läuft sie unabhängig vom Stick zu Ende. |
| Weitere Fahrt | X nach Fahrtende zentrieren, dann erneut auslenken | Keine vorab gespeicherte Wiederholung. Zentrieren während einer laufenden Fahrt bricht sie nicht ab. |
| Stoppen / Sperren | Einmal kurz drücken | Neue STEP-Flanken werden gestoppt; ein bereits laufender Impuls endet. LOCK. |
| Menü öffnen | Zweimal kurz drücken | Abstand der entprellten Druckereignisse unter 350 ms. Die erste Betätigung stoppt bereits. |
| Menü bedienen | Y: Seite; X: Wert | Längeres Halten wiederholt. Bei diagonaler Eingabe wird nur die Seite gewechselt. |
| Speichern / verlassen | Im Menü einmal drücken | EEPROM speichern, Ausgänge konfigurieren, zurück zu LOCK. |

## Menü

| Nr. | Anzeige | Werte | Bedeutung |
| --- | --- | --- | --- |
| 1 | Treiber | TB6600 / A4988 | Wählt den STEP-Ausgang. Keine elektrische Umschaltung des Motors. |
| 2 | Modus | Dauerlauf / Fahrt | Dauerlauf folgt dem Stick; Fahrt führt einen vorgegebenen Winkel aus. |
| 3 | Vollschr | 48 / 100 / 200 / 400 | Physikalische Vollschritte pro Motorumdrehung, ohne Microstep-Faktor. |
| 4 | Mikro | TB: 1…32; A: 1…16 | TB: 1, 2, 4, 8, 16, 32. A: 1, 2, 4, 8, 16. TB-DIP manuell angleichen. |
| 5 | Max RPM | 3 / 5 / 10 / 15 / 20 / 30 / 45 / 60 / 90 / 120 / 180 / 240 | Obergrenze; zusätzlich gelten maximal 4000 STEP-Impulse/s. |
| 6 | Beschl | 10 / 20 / 40 / 60 / 90 / 120 / 180 / 240 / 360 rpm/s | Beschleunigungs- und Bremsrampe im normalen Fahrbetrieb. |
| 7 | Weg Grad | 15 / 30 / 45 / 90 / 180 / 360 / 720 / 1440 | Winkel an der Motorwelle, ohne automatische Getriebeumrechnung. |
| 8 | Halten | Ein / Aus | A4988: Leerlauf-Haltestrom solange ARM. TB nur mit geprüfter optionaler ENA-Leitung. |
| 9 | Richtung | Normal / Invertiert | Elektrische DIR-Polarität je Treiberprofil umkehren. |

TB-DIP und Menü müssen zusammenpassen. Die Winkel- und Drehzahlangaben beruhen auf STEP-Impulsen, nicht auf Encoder-Messung.
