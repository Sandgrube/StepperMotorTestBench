# Parametrierung und Reproduktion

Quelle: CAD/editable_source, Parameter: CAD/parameters/default.json. Reine Python-/CadQuery-B-reps, keine Mesh-Importe und kein proprietäres CAD-Projekt nötig. STEP ist in normaler Einbaulage, STL bereits in Drucklage. Die Datumseinheit ist Millimeter.

| Gruppe | Wichtige Parameter / Abhängigkeit |
| --- | --- |
| enclosure | width, depth, height, front_angle_deg, panel_run, wall, floor, corner_radius, cover_clearance. Bei numerischem height wird front_height daraus abgeleitet; height=null erlaubt front_height als treibendes Maß. |
| fasteners | M3-Clearance/Pilot/Kopf; Mutter-SW/Höhe; M2,5-Pilot. Nicht mit einem globalen Skalierungsfaktor ersetzen. |
| uno | Board-XY-Transformation, PCB-Z, verifizierte vier Lochkoordinaten, USB/DC-Hüllen. |
| lcd | center_x/center_t, PCB und Loch-Offsets, Bezel/Tasche/Fenster, Montage-n, Backpackreserve. |
| joystick | center_x/center_t, hole_offsets, shaft_offset, pcb_front_n, mount_spacer, opening_diameter, Gimbal, Knopfprofil, Pivot, Winkel und Tastweg. |
| tb6600 | x/y/bottom_z, length/body_depth/overall_depth/height, fin_*, clamp_x, clamp_foot_screws, terminal_*. mounting_holes ist absichtlich leer. |
| a4988 | Lochraster, Sockelhöhe, Modulposition, Reihenraster, Kühlkörper, Kondensator, Pot und Terminal. |
| vents / access | Schlitzbreite/-länge/-raster; konkrete X/Y/Z-Lage der Heck- und Werkzeugöffnungen. |

Ein Layout ist nicht automatisch optimiert. Bei einer Verschiebung des TB6600 auch seine Bügel und Fußschrauben verschieben. Bei anderem Stecker oder Klemmenblock Öffnung UND Werkzeugachse anpassen. Knopfprofil und PCB-Montage müssen die reale Geometrie gemeinsam beschreiben. Eine geringere mount_spacer-Dicke bei unveränderten Stützen hebt die reale Platine an; deshalb bei einer bleibenden Änderung auch pcb_front_n und die Knopf-/Gimbalreferenz aktualisieren. Die beschreibenden Koordinatentabellen gelten für die mitgelieferte R1-Standardbelegung. Nach Layoutänderungen diese Texte zusätzlich mit der neuen Geometrie abgleichen; der Generator ersetzt keine automatische Dokumentationsprüfung beliebiger Varianten.

## Getestete Software

Python3.12, CadQuery2.7.0, cadquery-ocp7.8.1.1.post1. Benötigte Pakete stehen in requirements.txt. Matplotlib/Pillow erzeugen nur Bilder; der Kollisionsnachweis läuft direkt im CAD-Kernel. Die Vorschaubilder werden mit einem z-gepufferten CPU-Renderer aus derselben Geometrie erzeugt.

```bash
python -m pip install -r CAD/editable_source/requirements.txt
python CAD/editable_source/build_project.py
```

Für nur STEP/STL plus Geometrieprüfungen:

```bash
python CAD/editable_source/generate.py
```

Nach Änderung des Standards vollständig neu erzeugen, das Log auf FAIL prüfen und den Bericht lesen. Alternative Parameterdatei: build_project.py --params PFAD. Die Skripte schreiben die Ergebnisse wieder ins Projekt. Ein FAIL führt zu einem Fehlercode; make_documents.py verweigert dann einen Freigabetext. Diese Quellen sind in einem normalen Texteditor oder CQ-Editor editierbar. Es wird keine FreeCAD-FCStd-Datei behauptet.
