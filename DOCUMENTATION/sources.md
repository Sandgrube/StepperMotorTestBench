# Technische Quellen und Herkunft

Abgerufen23.10.2026. Die Links dienen dem Herkunftsnachweis; die Bauanleitung selbst benötigt keine Internetverbindung. Es werden keine fremden Zeichnungsseiten oder fremden CAD-Körper als eigene Arbeit ausgegeben. Alle gelieferten Referenzkörper wurden im Python-Quelltext neu aufgebaut.

| Quelle | Verwendet / Einschränkung |
| --- | --- |
| [Arduino Uno R3, offizielles Datenblatt](https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf) | Überblick und mechanische Zeichnung; für vollständige Koordinaten das Boardfile verwendet. |
| [Arduino UNO-TH_Rev3e.zip, offizielles Eagle-Board](https://content.arduino.cc/assets/UNO-TH_Rev3e.zip) | Exakte Lochkoordinaten, Umriss und XY-Buchsenfootprints. Extrakt samt SHA256 in CAD/component_models/uno_official_interface_extract.json. |
| [Pololu A4988 1182](https://www.pololu.com/product/1182) | Versorgungs-Trennung, LC-Spitzen, lokaler Elektrolytkondensator, thermische Einschränkungen. |
| [Pololu Maßzeichnung 1182](https://www.pololu.com/file/0J1082/a4988-stepper-motor-driver-carrier-dimension-diagram.pdf) | 15,2/20,3 gerundet bzw.600/800mil, Raster2,54, Reihenabstand12,70; unbekannte Klone separat prüfen. |
| [Handson MDU1059 TB6600](https://www.handsontec.com/dataspecs/module/TB6600-Motor-Driver.pdf) | S.2 zeigt96 ×71 ×36, inklusive Klemmen; Datenliste nennt96 ×56 ×33. Bewusst größeres96 ×71 ×37-Referenzmaß, nicht als eigener Messwert. |
| [DFRobot DRI0043 Wiki](https://wiki.dfrobot.com/dri0043/) | 96 ×71 ×37 als weitere Referenzklasse; [Produktseite](https://www.dfrobot.com/product-1547.html) nennt abweichend96 ×56 ×33. Keine eindeutige Identifikation des eigenen Moduls. |
| [Handson I²C1602](https://www.handsontec.com/dataspecs/module/I2C_1602_LCD.pdf) | 80 ×36-PCB-Klasse, keine Freigabe eines bestimmten Backpack. |
| [Newhaven NHD-0216K1Z-FL-YBW](https://newhavendisplay.com/content/specs/NHD-0216K1Z-FL-YBW.pdf) | Referenz-Lochabstand75 ×31 und Bezel71,2 ×25,2. Herstellerlöcher sind dort2,5, nicht pauschalM3. Das eigene I²C-Modul ist NICHT als Newhaven identifiziert. |
| [Handson PS2-Joystick ASS-1056](https://www.handsontec.com/dataspecs/accessory/PS2-Joystick.pdf) | 34 ×26 ×32-Variantenklasse; Quelle nennt4 ×M4, liefert keine belastbare Koordinatentabelle. Unser20 ×26-Bohrbild ist deshalb ausdrücklich unbestätigt. |
| [Joy-IT COM-KY023JM](https://www.joy-it.net/en/products/COM-KY023JM) | Weitere Variante mit34 ×39 ×26. Belegt die Unzulässigkeit einer pauschalen KY-023-Passgarantie. |
| Firmware-README22.10.2026, vom Nutzer bereitgestellt | Pinzuordnung und vorhandener Bedienumfang. Keine zusätzlichen Bedienelemente oder Firmwareänderungen. |

Der Handson-Backpack ist als42 ×19-Reservekörper modelliert. Knopfprofil, Gimbal, Kabelstecker, Bauteilhöhen und TB-Klemmenpositionen sind gekennzeichnete technische Annahmen. Die Dokumentation unterscheidet Herkunftsdaten, gewählte Fertigungstoleranzen und noch offene Messwerte.
