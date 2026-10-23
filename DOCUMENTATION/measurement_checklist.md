# Messliste vor dem ersten vollständigen Druck

**Noch keine Druckfreigabe für unvermessenes Fremdmodul.** Mit Messschieber und Lineal am eigenen Aufbau prüfen. Eine Artikelbezeichnung wie „TB6600“, „1602“ oder „KY-023“ legt das Bohrbild nicht eindeutig fest. Alle Werte unten sind Defaultwerte des Modells; nur die ausdrücklich belegten Uno-Koordinaten und A4988-Rasterdaten sind verifizierte Herstellergeometrie.

| Teil / Maß | Modellwert | Eigener Wert / Konsequenz |
| --- | --- | --- |
| Uno PCB, vier Löcher | 68,58 × 53,34; siehe dimensions.md | ____ / Clone-Umriss und Metallbuchsen prüfen. |
| Uno USB-Anschlusskante, Z-Höhe | u −6,34; 10,8 über PCB | ____ / Gehäuseöffnung und echten USB-Stecker mit Coupon prüfen. |
| Uno DC-Buchse und Stecker | 11 hoch; rückseitiger Ø12-Steckerraum | ____ / Besonders Kopf neben der Buchse prüfen. |
| TB vollständige Hülle inkl. Klemmen und Laschen | 96 × 71 × 37 | ____ / Alles außerhalb erfordert neue Parameter und erneute Prüfung. |
| TB Körper ohne Klemmen | 96 × 57; Unterseite gerippt | ____ / Vier Auflagen müssen tatsächlich die Metallunterseite tragen. |
| TB flache obere Kontaktstellen für Bügel | X130 und X214; Y111…131 | ____ / 8 × 20 große Pads müssen auf geschlossenem Deckel liegen, keine Klemmen/DIP blockieren. |
| TB Klemmenschrauben und Kabeleintritt | Y157; Leitungshöhe Z38 eingebaut | ____ / Toolschlitz und Heckfenster verschieben, falls abweichend. |
| TB originale Befestigungslöcher | nicht verwendet | ____ / Nur protokollieren; keine erfundenen Lochkoordinaten im CAD. |
| LCD PCB / Lochabstände / Ø | 80 × 36 / 75 × 31 / Referenz Ø2,8 | ____ / M2,5 muss ohne Kraft durch reale Löcher passen. |
| LCD Bezel, Sichtfenster, Höhe über PCB | 71,2 × 25,2; Sicht66 × 16; 8,6 Höhe | ____ / Andere Fassungen ändern Tasche UND Montageabstand. |
| LCD Backpack inkl. Jumper, Pot und Kabelstecker | 42 × 19; Rückreserve bis n −32,5 | ____ / Alles inkl. eingesteckter Leitung messen. |
| Joystick PCB / vier Lochkoordinaten | 26 × 34; ±10 / ±13 relativ zur Mitte | ____ / NICHT vom Modell auf den eigenen KY-023 schließen. |
| Joystick Loch-Ø / Knopfmittelpunktversatz | Referenz3,3 / [0,0] | ____ / Bei Ø4-Löchern passende Scheiben, Geometrie neu prüfen. |
| Joystick Mechanik, Kragen und voller Knopfweg | Mechanikhülle18 × 20 × 14; 22°; 1 Tastweg | ____ / Ohne Kraft alle Richtungen drücken; mindestens 0,5 reale Luft anstreben. |
| Joystick Aufbauhöhe und Form der Kappenunterseite | Modell33,6 PCB-Unterseite bis Knopfspitze | ____ / Quelle nennt eine 32-mm-Klasse; Varianten unterscheiden sich. Z-Abstand per Distanzring und Coupon einstellen. |
| A4988 Pinraster / Reihenabstand | 2,54 / 12,70; Modul15,24 × 20,32 | ____ / 16-poligen Carrier, nicht größeren 1183-Reglercarrier verwenden. |
| A4988 Pot, IC, Kühlkörper, Steckrichtung | Pot X95/Y128 im Referenzmodell | ____ / Aufdruck und Datenblatt, nicht Pot-Farbe oder Platinenfarbe entscheiden. |
| Lochraster und Klemmen | 40 × 60 ×1,6; 6 × 5,08; Tiefe8 / Höhe10 | ____ / Klemme ≤30,48 breit; freie 3,5-mm-Kanten für Haltefinger. |
| Kondensator und bestückte Gesamthöhe | 100µF ≥50V bei geeigneter niedriger VMOT; Ø≤10 / H≤16 | ____ / Nennspannung passend zur realen Versorgung, Kapazität lokal. |

1. Zuerst LCD- und Joystick-Coupons sowie Mutter-/Pilot-Coupon drucken. Die drei Muttertaschen sind von links nach rechts SW5,7 /5,9 /6,1 und öffnen seitlich zur hinteren langen Kante. Den Pilotcoupon mit M3 ×8 prüfen, längere Schrauben nicht bis zum Kopf hineinzwingen.
2. Am Joystick-Coupon alle vier Distanzringe einsetzen, Knopf gegebenenfalls vor Einsetzen abziehen und danach wieder aufsetzen. Voll auslenken und gleichzeitig drücken. Reale Kappenform ist entscheidend.
3. USB/DC-Coupon mit den tatsächlich verwendeten Kabeln prüfen; nicht nur leere Buchsen vergleichen.
4. LCD über das Fenster halten; Lochlage, Ränder und Lesbarkeit prüfen. Der flache LCD-Coupon prüft XY, nicht die Backpack-Tiefe.
5. Bei Abweichungen `default.json` ändern und alles neu generieren. Kein vollständiger Druck mit ungeklärten Pflichtmaßen.
