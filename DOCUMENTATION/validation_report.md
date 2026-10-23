# Validierungsbericht · R1

**Status: digitale Referenzgeometrie bestanden. Reale Passung noch nicht freigegeben.**

Geprüft mit CadQuery2.7.0 / OpenCascade-B-rep. Basis: default.json, nicht vermessene Originalteile des Nutzers. Die Prüfungen werden von generate.py erneut ausgeführt. Maschinenlesbare Rohdaten: validation_results.json. Alle nachfolgenden Angaben betreffen die exportierten Referenzkörper.

| Prüfung | Ergebnis |
| --- | --- |
| B-rep-Körper | 11 druckbare Bauteile, jeder genau1 gültiger Solid |
| Schnittvolumen | {'printed_printed': 55, 'printed_component': 385, 'component_cross_group': 502}; keine Überschneidung oberhalb0,005mm³ |
| Schraubenköpfe / Scheiben / Muttern | Nominale Körper zusätzlich geprüft; keine unzulässige Überschneidung. Schäfte überlappen Piloten/Gewindekern absichtlich. |
| Joystick | 170 Abtaststellungen;22° maximal,1mm Tastweg; min. Modellabstand1.056mm |
| Deckel | 7 Hubstellungen bis60mm; Front und Module bleiben eingebaut. |
| Komponentenausbau | Uno6, A4988-Träger5 und TB6600 4 diskrete Ausbaupositionen ohne Kollision nach Lösen der dokumentierten Halter. |
| Werkzeug-/Kabelzugänge | 42 korridorbezogene Prüfungen; Ø3-mm-Werkzeugschaft bzw. Kabelhülle, reale Stecker zusätzlich vermessen. |
| STL-Netze | 17 Netze inkl. Coupons und optionalem Fuß: keine offenen/nichtmanifold Kanten, konsistente Orientierung, positives Volumen. |
| Bauvolumen | Alle Teile ≤256mm je Achse; größte XY-Ausdehnung230 ×176. |
| STEP-Einzelteile | Alle reimportiert; Volumenabweichung <10⁻⁶ relativ. |
| STEP-Baugruppe | Reimport gültig;108 Solids; Volumenabweichung2.23e-13. |
| Exportvergleich | Alle Haupt-STL-Volumina <0,5% Abweichung gegenüber dem B-rep. Konkrete Fehlerwerte in JSON. |

## Druckkörper

| Teil | Druck-Boundingbox mm | Massivvolumen cm³ | Ergebnis |
| --- | --- | --- | --- |
| main_chassis | 230.00 × 176.00 × 61.24 | 217.341 | gültig / geschlossen |
| front_panel | 230.00 × 97.86 × 56.08 | 75.783 | gültig / geschlossen |
| top_cover | 230.00 × 85.65 × 8.00 | 59.576 | gültig / geschlossen |
| tb_clamp_left | 22.00 × 86.70 × 45.20 | 5.929 | gültig / geschlossen |
| tb_clamp_right | 22.00 × 86.70 × 45.20 | 5.929 | gültig / geschlossen |
| a4988_edge_clip_1 | 8.00 × 7.70 × 4.40 | 0.149 | gültig / geschlossen |
| a4988_edge_clip_2 | 8.00 × 7.70 × 4.40 | 0.149 | gültig / geschlossen |
| joystick_spacer_1 | 6.00 × 6.00 × 2.00 | 0.038 | gültig / geschlossen |
| joystick_spacer_2 | 6.00 × 6.00 × 2.00 | 0.038 | gültig / geschlossen |
| joystick_spacer_3 | 6.00 × 6.00 × 2.00 | 0.038 | gültig / geschlossen |
| joystick_spacer_4 | 6.00 × 6.00 × 2.00 | 0.038 | gültig / geschlossen |

## Aussagegrenzen und verbleibende Risiken

Die A4988-/TB-/LCD-/Joystickmodelle sind bewusst vereinfachte Referenz- und Freiraumkörper. Elektronik-intern dürfen einzelne reservierte Hüllen überlappen; geprüft werden die Gehäuseschnittstellen und die verschiedenen Baugruppen gegeneinander. Die tatsächliche Kappenunterseite, Potposition, TB-Laschen, Steckerkörper und LCD-Backpack-Variante können abweichen. Das sind offene Passungsrisiken und werden nicht durch ein grünes CAD-Ergebnis aufgehoben.

Die Joystick- und Ausbauprüfungen sind diskrete geometrische Abtastungen, keine kontinuierliche zertifizierte Bewegungsraumprüfung. Kabelkorridore ersetzen keine Simulation verformbarer Kabel, keine Prüfung eines Biegeradius unter Zug und keinen genormten Zugentlastungsversuch. Schraubendrive-Rezess und Gewinde sind im STEP nicht detailliert modelliert. Für die gekaufte Hardware gelten die Kopfgrößen der Stückliste.

Keine physische Montage, kein echter FDM-Druck, keine Slicerplatte, kein Festigkeitsversuch, keine FEM, keine elektrische Durchgangsprüfung und keine thermische Dauerprüfung wurden durchgeführt. Der Generator beweist die Reproduzierbarkeit des digitalen Entwurfs; er beweist nicht, dass beliebige gleich bezeichnete Module passen. Maßliste und Funktions-Coupons sind vor dem großen Druck verbindliche lokale Prüfungen.
