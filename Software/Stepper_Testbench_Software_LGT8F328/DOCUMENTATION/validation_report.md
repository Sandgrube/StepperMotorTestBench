# Validierung · Firmware 2.1.0 / LGT8F328

Stand: 24.10.2026. Die genaue P/D- und Platinenvariante des Nutzers ist noch nicht identifiziert.

| Buildprofil | Flash | Statischer RAM | Ergebnis |
| --- | --- | --- | --- |
| p16 | 22494 / 29696 Byte | 1274 / 2048 Byte | Kompiliert |
| p16_single | 22576 / 29696 Byte | 1274 / 2048 Byte | Kompiliert |
| p32 | 22480 / 29696 Byte | 1274 / 2048 Byte | Kompiliert |
| p32_single | 22562 / 29696 Byte | 1274 / 2048 Byte | Kompiliert |
| d16 | 22200 / 29696 Byte | 1275 / 2048 Byte | Kompiliert |
| d32 | 22186 / 29696 Byte | 1275 / 2048 Byte | Kompiliert |
| p48_16 | 22524 / 29696 Byte | 1274 / 2048 Byte | Kompiliert |
| p48_32 | 22510 / 29696 Byte | 1274 / 2048 Byte | Kompiliert |

Toolchain: Arduino CLI 1.5.1; lgt8fx-Paket 2.0.7; AVR-GCC 7.3.0-atmel3.6.1-arduino7; hd44780 1.3.2. D-Core-Warnungen zur ungetesteten EEPROM-Emulation wurden beibehalten und nicht als eigener Hardwaretest ausgegeben.

Die Timer-Konfiguration ist F_CPU-abhängig: Prescaler 8, OCR1A 199/399 für 16/32 MHz, TC2XS1 gelöscht. Nominal 10 kHz in beiden Fällen. ADC ausdrücklich 10 Bit bei VCC-Referenz. Direkte Portzuordnung der verwendeten digitalen und analogen Pins wird beim Start geprüft. EEPROM-Schreibdaten werden zurückgelesen und mit CRC geprüft; das ist noch kein tatsächlicher Flash-Lebensdauertest.

Native Tests: C++11, -O2, -Wall -Wextra -Werror -pedantic, AddressSanitizer und UndefinedBehaviorSanitizer. LeakSanitizer im Container ausgeschaltet. 48,102,230 Assertions einschließlich wiederholter Scheduler-Invarianten; keine Anzahl unabhängiger Szenarien. Geprüft: Timerwerte, alle Raten 1…4000 PPS, endliche Impulsblöcke, letzter HIGH-Impuls, kein Wiederholstart, Lease, Tastergesten, millis-Überlauf, Fahrtrampen/Umkehr, minimale und maximale Fahrt, Anlaufmatrix, CRC/Migration und alle fünf Fehleranzeigen. Logs in validation.

Offen: tatsächliches Board/Versorgung/Bootloader, Upload, EEPROM-Retention auf diesem Board, Oszilloskop-Timing/Jitter, Motorlast, Stromlimit und thermischer Dauerlauf. Der native Hardwareadapter ist ein Modell. Die LGT-internen RC-Oszillatoren wurden nicht vermessen. Kompilieren bestätigt die Ziel-Core-Schnittstelle und den Speicherbedarf, keine physische Kompatibilität einer unbekannten Platine.
