# Software 2.1.0 · 24.10.2026 · LGT8F328

- Auf den tatsächlich genannten LGT8F328 portiert; LGT8fx-Core erforderlich, Uno-Core ausdrücklich gesperrt.
- Getrennte Buildprofile für P/LQFP32, D/LQFP32 und P/LQFP48 mit je 16/32 MHz; Ein-Datei-Ausgaben mit dem LGT-Core kompiliert.
- Timer1-Vergleichswert aus F_CPU berechnet; separate LGT-Hochgeschwindigkeitsquelle für Timer1 deaktiviert. Timer0 bleibt unverändert.
- Joystick-ADC ausdrücklich auf 10 Bit / VCC-Referenz gesetzt.
- LGT-E2PROM mit 1 KB logischer Kapazität, Kapazitätskontrolle und Zurücklesen der gespeicherten Daten. Fehler sperren bis zum Reset.
- Abweichende Software-Pinzuordnung beim Start erkannt; SSOP20 und nicht freigegebene CPU-Takte beim Build gesperrt.
- Boardauswahl, Uploadgeschwindigkeit, mögliche Löschung der Flash-emulierten Einstellungen und weiterhin offene Platinen-/Gehäusepassung dokumentiert.

Die exakte P/D- und Platinenvariante ist vom Nutzer noch nicht angegeben. Die Profile sind kompilierte Referenzziele, kein physischer Boardnachweis. Kein realer Upload oder Motor-/EEPROM-Retentionsversuch.

## Vorherige Version 2.0.0

- Pinbelegung kompatibel zur Firmware v1 und zum Gehäuse R1.
- Für den ATmega328P tatsächlich kompiliert; unabhängige native Verhaltenstests mit Sanitizern ergänzt.
- Timer-Pulsengine modularisiert: endliche Blöcke, laufenden HIGH-Impuls beim Stoppen beenden, kein Wiederanlauf nach dem letzten Impuls.
- Timer-Lease sperrt bei blockiertem Hauptablauf; erkannte LCD-/I²C-Fehler sperren die Bewegung bis zum Reset.
- Stabilitätsprüfung der Startkalibrierung; während der gesamten Freigabe zentriert halten; danach Taster loslassen.
- Keine gespeicherte Wiederholfahrt nach zwischenzeitlicher X-Zentrierung während einer Journey.
- Richtungswechsel über Stillstand; explizite DIR-/Freigabewartezeit.
- Anlauf auch bei kleinen Pulsraten und niedriger Beschleunigung: Bruchteile der Rampenschritte bleiben erhalten.
- Physikalisch passende Skalierung beider Y-Hälften bei außermittigem Joystick.
- Neunter Menüpunkt für getrennte Richtungsinversion der Treiber; Diagonalgesten verändern nur die Menüseite.
- EEPROM-v1-Profile werden mit CRC-/Bereichsprüfung nach v2 übernommen.
- Eigenständig kompilierbare Ein-Datei-Ausgabe, reproduzierbarer Build, HTML-Anleitung und Quellarchive der geprüften Abhängigkeiten.

Keine reale Hardware- oder thermische Erprobung. Einzelheiten und tatsächliche Logs in DOCUMENTATION/validation_report.md und validation/.
