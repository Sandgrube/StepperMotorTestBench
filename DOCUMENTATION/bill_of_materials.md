# Stückliste

## Vorgegebene Elektronik

| Anzahl | Teil | Hinweis |
| --- | --- | --- |
| 1 | Arduino Uno R3 | Originaler TH-Formfaktor, kein Shield |
| 1 | TB6600-Modul | 96 × 71 × 37-Referenzklasse; vorab messen |
| 1 | A4988-Carrier | 16-polige 15,24 ×20,32-Klasse |
| 1 | XY-Joystick mit integriertem Taster | 26 ×34-Referenz-PCB; tatsächliches Bohrbild messen |
| 1 | 1602 LCD mit I²C-Backpack | 80 ×36-Referenz-PCB |

## Erforderliche Schrauben und Muttern

Schwarz beschichteter Stahl oder normaler Stahl sind geeignet. Schraubenlängen sind Nennlängen, bei Senkköpfen einschließlich Kopf. Keine zusätzlichen großen Scheiben auf die Senkungen legen.

| Anzahl | Spezifikation | Verwendung |
| --- | --- | --- |
| 6 | M3 ×12, 90° Innensechskant-Senkkopf, DIN7991/ISO10642; Kopf ≤Ø6,4 | 4 Front von unten, 2 Deckel von oben |
| 4 | M3 ×8, gleicher 90°-Senkkopf | TB-Bügelfüße; Köpfe müssen bündig sitzen |
| 6 | M3 ×10, Zylinderkopf ISO4762/DIN912, Kopf ≤Ø5,5 | 4 Joystick, 2 A4988-Kantenclips |
| 7 | M2,5 ×8, Zylinderkopf ISO4762/DIN912, Kopf ≤Ø4,5 | 4 LCD, 3 Uno; kleinere Köpfe wegen Anschlussnähe |
| 6 | M3-Sechskantmutter DIN934/ISO4032, SW5,5, Höhe2,4 | 4 Frontstützen, 2 Deckeltürme |
| 6 | M3-Scheibe ISO7089/DIN125, Ø3,2 / Ø6 / ca.0,5 | 4 unter Joystick-Schraubenköpfen, 2 unter A4988-Clipköpfen |
| 4 | M2,5-Scheibe, Ø2,7 / Ø5 / ca.0,5 | LCD; keine Scheiben an Uno-DC-Montage |
| 4 | 2-mm-Distanzring, Ø6 / LochØ3,4 | Druckteile joystick_spacer_1…4; alternativ passende M3-Distanzscheiben oder je 4 ×0,5-mm-Scheiben |

Die Distanzringe werden standardmäßig gedruckt; dafür keine Metallteile zusätzlich kaufen. Als Einkaufsmengen sind kleine Schraubenpackungen mit Reserve sinnvoll. Wärmeinserts werden nicht benötigt. Für wiederholte Wartung sind die sechs Gehäusemuttern vorgesehen; die selten gelösten PCB-/Bügelschrauben greifen in PETG-Piloten.

## Erforderliches Montage- und Verdrahtungsmaterial

| Menge | Spezifikation | Zweck |
| --- | --- | --- |
| 1 | Unbestückte Lochrasterplatine 40 ×60 ×1,6, Raster2,54, frei wählbare Montagebohrungen | Mechanischer Träger für den gesockelten A4988 |
| 2 | Buchsenleiste 1×8, Raster2,54, Körper-/Aufbauhöhe8,5 oder CAD anpassen | Treiber austauschbar; NICHT verdreht einstecken |
| 1 | Leiterplatten-Schraubklemme 6-polig, Raster5,08, Breite≤30,48, Tiefe≤8, Höhe≤10; alternativ 3 gekoppelte 2-polige | Getrennte A4988-Versorgung und vier Motoradern; kein Bulkhead nötig |
| 1 | Elektrolytkondensator100µF, Spannungsfestigkeit passend zur VMOT, bevorzugt50V bei 12/24V-Aufbau, Ø≤10 × H≤16 | Direkt bei VMOT/GND; nicht als entferntes Kabel-Ende montieren |
| 1 | Passivkühlkörper für A4988, Hülle≤10 ×10 ×10 plus vorgesehener Kontaktlage | Elektrisch isoliert befestigen, keine benachbarten Pads überbrücken |
| 2 | Silikonschaumstreifen 8 ×20 ×1, weich, temperaturgeeignet, selbstklebend oder sparsam fixiert | TB-Bügelpolster; etwa0,6-mm-komprimierte Höhe im Modell |
| 4 | Selbstklebende Gummifüße Ø14 ×4 | Lufteintritt unter dem Boden; alternativ 4 TPU-Füße plus geeignetes Klebeband |
| ca.3m | Flexible isolierte Logiklitze 0,14…0,25mm², mehrere Farben | Frontkabel, Steuerleitungen, kurze lokale Masse-/5V-Verteilung |
| ca.1m intern + externe Testleitungen | Motor-/Versorgungslitze ca.0,5…1,0mm², nach Strom/Klemmen auswählen | Keine Dupont-Leitung als Motorleistungsleitung verwenden |
| ca.30 Kontaktpositionen | Passende Buchsen-/Stiftkontakte oder vorkonfektionierte Jumper für Logik | Steckerlängen müssen in die reservierte Hülle passen |
| 10 | Kabelbinder2,5 ×100 | Anker und Zugentlastung; nicht auf SMD-Bauteile spannen |
| ca.0,3m | Schrumpfschlauch / flexible Kantenschutz-Isolation für Hecköffnungen | Lötstellen und Kabel gegen Scheuern schützen |

Die Mengen der Litzen sind Beschaffungsrichtwerte, keine Zuschnittliste. Auf dem Lochraster die Klemmen stabil verlöten; Strompfade mit ausreichend kräftiger Litze oder Kupferdraht verstärken, nicht über dünne beliebige Lötbrücken führen. Ein externer Gleichspannungs-Testaufbau und USB-Kabel sind Betriebsvoraussetzungen; es wird kein Netzteil im Gehäuse eingebaut.

## Druckteile und optionale Teile

| Datei in PRINT | Anzahl | Ausrichtung bereits enthalten |
| --- | --- | --- |
| main_chassis.stl | 1 | Boden auf Druckbett |
| front_panel.stl | 1 | Sichtfläche auf Druckbett; Stützen wachsen nach oben |
| top_cover.stl | 1 | Außenfläche auf Druckbett |
| tb_clamp_left.stl / tb_clamp_right.stl | je1 | Bügeloberseite auf Bett, Beine nach oben |
| a4988_edge_clip_1.stl / a4988_edge_clip_2.stl | je1 | Große ebene Unterseite auf Bett |
| joystick_spacer_1…4.stl | je1 | Ringe flach; gleiche Geometrie an vier Einbaupositionen |
| optional_parts/tpu_foot_print_4.stl | 4 optional | TPU, mit Klebung; ersetzt gekaufte Füße |

Werkzeuge: Innensechskant2,0 und2,5mm, schmaler kleiner Schlitzschraubendreher für Klemmen, Messschieber, Zange, Lötkolben und Multimeter. Die geometrisch geprüften Zugangskorridore nehmen einen maximal Ø3-mm-Werkzeugschaft an. Ein dicker Schraubendreher-Bithalter passt nicht an die vorderen Bügelschrauben. Gewinde vorsichtig per Hand bilden; keine Akkuschrauber verwenden.
