# Stepper Testbench Enclosure · R1

Vollständiger parametrischer Gehäuseentwurf für Uno R3, TB6600, A4988, XY-Joystick und1602-I²C-LCD. Standardmaß 230 ×176 ×64.24mm ohne Füße/Knopf. Die Front ist18° zur Tischfläche geneigt.

**Start:** DOCUMENTATION/assembly_guide.html im Browser öffnen. Bilder und Stil sind eingebettet; die Datei funktioniert offline. Vor vollständigem Druck measurement_checklist.md und die Coupons prüfen. Reale Modulvarianten wurden nicht vermessen; dies ist ein digital geprüfter Entwurf, keine physische Passgarantie.

- CAD/main_assembly.step: komplette Referenzbaugruppe mit nominalen Schrauben, Muttern, Haltern und den fünf Elektronikgruppen.
- CAD/printed_parts: alle druckbaren Teile einzeln als STEP in Einbaulage, zusätzlich Coupon-STEPs.
- CAD/editable_source und CAD/parameters: vollständig editierbarer CadQuery-Generator.
- PRINT:11 individuelle druckorientierte Haupt-STLs; vier davon sind identische Joystick-Distanzringe.5 Coupons und optionaler TPU-Fuß separat.
- DOCUMENTATION: vollständige Stückliste, Montage, Maßliste, Zugänge und Rohdaten der geometrischen Validierung.
- PREVIEWS: aus der tatsächlichen CAD-Geometrie erzeugte Ansichten, Explosionsbild und bemaßter Layoutplan.

Geprüft: gültige B-reps, geschlossene STL-Netze, STEP-Reimport, Schnittvolumen,170 Joystickstellungen,42 Zugangsprüfungen und diskrete Ausbauwege. Nicht durchgeführt: echter Druck, Slicerfreigabe, elektrischer oder thermischer Versuch. Kein3MF wird behauptet.

## Reproduktion

Getestet unter Python3.12 mit CadQuery2.7.0 und OpenCascade7.8.1.1.post1. Alle Kommandos vom Projektordner aus:

```bash
python -m pip install -r CAD/editable_source/requirements.txt
python CAD/editable_source/build_project.py
```

Nur CAD/Netze/Validierung: `python CAD/editable_source/generate.py`. Ein gewöhnliches STEP-CAD-Programm kann die Baugruppe öffnen; die parametrische Bearbeitung erfolgt im Python/JSON-Quelltext. Es gibt keine unerwähnten lokalen Assets oder absoluten Pfadabhängigkeiten.
