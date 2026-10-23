# Maße, Koordinaten und Toleranzen

Alle Maße in Millimeter. X läuft von links nach rechts, Y von vorne nach hinten, Z nach oben. Z = 0 ist die Unterseite der Bodenschale. Der Parameter `height` bezeichnet die obere hintere Gehäusekante. Gummifüße und Joystick sind darin nicht enthalten.

Die Frontkoordinate t läuft auf der geneigten Fläche nach hinten; n zeigt senkrecht nach außen. Die Außenseite liegt bei n = 0. Für den Standardentwurf: Y = t cos(18°) − n sin(18°), Z = 35 + t sin(18°) + n cos(18°).

| Merkmal | Standard |
| --- | --- |
| Gehäuse / Front | 230 × 176 × 64.243; vorne 35.000; 18° zur Tischfläche |
| Materialstärken | Wände 2,4; Boden 3,0; Front und Deckel 3,0; äußere Eckradien 4,0 |
| Standfüße | 4 × Ø14 × 4; auf glatte Unterseite kleben; 4 mm Luft unter dem Boden |
| LCD-Mitte / Fenster | X 78; t 47,5; Fenster 66,8 × 17,8; rückseitige Tasche 72,4 × 26,4 |
| LCD-Anlage | PCB-Vorderseite n −9,6; Metallfront n −1,0; 75 × 31 Lochabstand |
| Joystick-Mitte / Durchbruch | X 180; t 47,5; Ø29,2; PCB-Vorderseite n −15,2 mit 2,0 Distanzringen |
| Joystick-Bohrbild | 20 × 26, ausdrücklich unbestätigte Referenz; vier Offsets ±10 / ±13 |
| TB6600 | X 124…220; Y 94…165; Z 10…47; 96 × 71 × 37 Gesamthülle |
| A4988-Lochraster | X 75…115; Y 107…167; PCB-Unterseite Z 10; 40 × 60 × 1,6 |
| A4988-Sockel | zwei Reihen 1×8; Raster 2,54; Reihenmittenabstand 12,70; Sockelhöhe 8,5 |
| Kondensatorreserve | Ø10 × 16 über Lochraster; Mittelpunkt X109 / Y143 |
| Hintere Werkzeugschlitze | TB: X135…209 / Y153…161; A4988: X77…113 / Y159…167 |
| Lüftung | Schlitzbreite 3,2; Deckelschlitze Länge 24; Raster 6; seitliche Schlitze mit Dachspitze |

## Uno-Montage: belegte Koordinaten

Die offiziellen Eagle-Koordinaten sind u/v, mit u längs der Platine und den Buchsen bei u ≈ 0. Einbau: X = 14 + v, Y = 169,5 − u. PCB-Unterseite Z = 10. Die drei verwendeten Schrauben sind M2,5; die vierte Stelle erhält nur einen Ø2,5 × 0,95-mm-Locator. Damit bleibt der sehr knappe Platz neben der Headerleiste frei. An der DC-Buchse keine große Unterlegscheibe verwenden. Schraubenkopf dort höchstens Ø4,5.

| Index | Offiziell u / v | Global X / Y | Befestigung |
| --- | --- | --- | --- |
| 0 | 66.04 / 35.56 | 49.56 / 103.46 | M2,5 × 8 |
| 1 | 66.04 / 7.62 | 21.62 / 103.46 | M2,5 × 8 |
| 2 | 15.24 / 50.80 | 64.80 / 154.26 | Locator |
| 3 | 13.97 / 2.54 | 16.54 / 155.53 | M2,5 × 8 |

Der Platinenumriss 68,58 × 53,34 und die vier Ø3,2-Montagelöcher stammen aus dem offiziellen Board. Kleine gerundete Platinen-Ecken sind im Referenzkörper als kurze Fasen angenähert. Die USB- und DC-XY-Hüllen stammen aus den offiziellen Footprints; deren Höhen und die Steckerumhüllungen sind Annahmen. Das STEP-Referenzmodell ersetzt keine Vermessung eines Uno-Klons.

## Funktionsbezogene FDM-Zugaben

| Schnittstelle | Geometrische Zugabe | Prüfung |
| --- | --- | --- |
| Deckel-Frontfuge und seitliche Führungen | 0,35 Abstand; keine Presspassung | Deckel soll ohne Vorspannen abheben. |
| M3-Durchgang | Ø3,4; Bügelschlitz 3,6 × 8 | Bohrung nicht gewaltsam freischrauben. |
| M3-Muttertasche | SW5,9; Höhe2,7 für SW5,5 / Höhe2,4 | Coupon mit SW5,7 / 5,9 / 6,1. |
| M3 in PETG | Ø2,6 Pilot, gerolltes Metallgewinde schneidet/formt Kunststoff | Coupon Ø2,45 / 2,55 / 2,65 / 2,75. |
| M2,5 in PETG | Ø2,15 Pilot; max. Ø4,5 Kopf | Nicht maschinell anziehen. |
| LCD-Bezel | Tasche jeweils 1,2 größer als Referenz-Bezel | 0,6 seitlich, keine geklemmte Metallfassung. |
| LCD-Fenster | +0,8 Breite / +1,8 Höhe zur Sichtfläche | Buchstaben dürfen nicht verdeckt werden. |
| Joystick | Knopf und Gehäuse separat; Referenzweg 22° + 1 mm Tastweg | Funktionscoupon mit echtem Modul. |
| TB-Bügel | 0,6 Luft über der Referenzhülle; weicher 1-mm-Schaum wird komprimiert | Kein starres Klemmen auf Kühlrippen. |
| Lochraster-Kantenhalter | 0,2 vertikale Luft; vordere Überdeckung 0,6 | Hinten lösen, 1 mm nach hinten schieben. |

Die Werte sind Konstruktionszugaben, keine gemessene Druckerfähigkeit. XY-Fluss und Elefantenfuß beeinflussen kleine Löcher; vor großen Teilen die Coupons mit dem gleichen Material drucken. Das gesamte Gehäuse nicht skalieren, um eine einzelne Bohrung zu korrigieren.
