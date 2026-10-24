# LGT-Portierung: technische Entscheidungen

Version 2.1.0, Paket lgt8fx 2.0.7 aus dem Maintainer-Release; SHA256 des unveränderten Archivs in NOTICE.md.

- Der Core kompiliert mit -mmcu=atmega328p, definiert aber erst über pins_arduino.h die LGT-Makros __LGT8F__ und __LGT8FX8P__/__LGT8FX8E__. Deshalb ist allein __AVR_ATmega328P__ keine Boarderkennung. Diese Ausgabe fordert ausdrücklich den LGT-Core.
- Die CPU-Frequenz kommt aus F_OSC/F_DIV. Prescaler 8 und OCR1A=F_CPU/(8*10000)-1 ergeben 199/399 für 16/32 MHz. TC2XS1 in TCKSR (0xEC), Bit 1, wird gelöscht: Timer1 arbeitet mit dem Systemtakt, nicht dem separaten Hochgeschwindigkeitstakt. Timer0 bleibt unverändert. TCCR1A/B/C und gegebenenfalls TCCR1D werden initialisiert; ein ausstehendes Compare-Flag wird gelöscht.
- Beleg: LogicGreen LGT8FX8P Databook 1.0.5 English, PDF-Seiten 139–140 und 151–152; LGT8FX8D Programming Manual 1.0.5, PDF-Seiten 90–91 und 102. Dateien aus https://github.com/dbuezas/lgt8fx/tree/master/docs . Die englische D-Fassung ist eine im Repository mitgelieferte Übersetzung.
- analogReadResolution(10) und analogReference(DEFAULT) normalisieren den Joystickbereich auf 0…1023 relativ zur Board-Versorgung. Ohne passende Versorgung bleibt der analoge Bereich trotzdem hardwareabhängig.
- E2PROM/EEPROM des LGT-Cores verwenden. Der falsche Arduino-EEPROM-Header wird beim Kompilieren abgewiesen. 1 KB logische Emulation wird gesetzt; keine größere Flashreserve wird aktiviert. EEPROM.update begrenzt unnötige Schreibzugriffe. Zurücklesen, Bytevergleich und CRC prüfen jeden gespeicherten Datensatz. Die Maintainer-Warnung für die D-Emulation wird nicht unterdrückt.
- D2…D11, A0/A1 und A4/A5 werden beim Start gegen die erwarteten Portregister/Bitmasken geprüft. Eine abweichende Software-Pinmap bleibt LOCK mit Fehler 4. SSOP20 wird bereits beim Kompilieren gesperrt. Falsche physische Boardbeschriftungen werden dadurch nicht erkannt.
- Fehler 5 bezeichnet eine zu kleine oder fehlgeschlagene EEPROM-Schnittstelle. Kein Zugriff auf zusätzlichen DAC, PGA, LEDs, Taster oder sonstige Module.

Native Tests prüfen den Bewegungskern und beide Timerkonstanten. LGT-Builds prüfen Core-APIs und Ressourcen. Weder die Datenbuchprüfung noch der Compiler ersetzen Timing-/Flash-/Motorversuche am realen Board.
