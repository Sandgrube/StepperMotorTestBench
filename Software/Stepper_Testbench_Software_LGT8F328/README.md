# Stepper Testbench · LGT8F328 · Firmware 2.1.0

Für LGT8F328P/D, TB6600, A4988, XY-Joystick mit Drucktaster und 16×2-I²C-LCD. Die Zuordnung D2…D11, A0/A1 und A4/A5 bleibt erhalten. Die bisherige Uno-Auswahl ist für diese Ausgabe ausdrücklich gesperrt.

## Installation

1. In den Arduino-IDE-Voreinstellungen diese zusätzliche Boardverwalter-URL eintragen:
   `https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json`
2. **lgt8fx 2.0.7** installieren; **hd44780 1.3.2 von Bill Perry** installieren.
3. `Stepper_Testbench_LGT8F328/Stepper_Testbench_LGT8F328.ino` mit allen Begleitdateien öffnen. Alternativ die eigenständige Datei aus `single_file` verwenden.
4. Board **LGT8fx Boards → LGT8F328** wählen. Tatsächliche P/D- und Gehäusevariante auswählen. Für 16 MHz: **Clock Source Internal 32MHz, Clock Divider 2**. Divider 1 ergibt 32 MHz. Richtigen Port und Bootloader-Uploadgeschwindigkeit wählen.
5. Zuerst ohne Motorversorgung über USB hochladen; Joystick beim Booten zentrieren. Serieller Monitor 115200 Baud.
6. `DOCUMENTATION/software_guide.html` lesen: kompletter Anschlussplan, Modul-Stromlimit, Menü und Ersttest. Mit 5 RPM / 15° ohne Last beginnen.

**Die genaue Variante ist noch offen.** LGT8F328 allein bezeichnet weder P/D noch Bauform oder Logikspannung. P/LQFP32 ist eine häufige Bauform und die Voreinstellung des Buildskripts, wurde aber nicht als dein Board bestätigt. SSOP20 wird wegen der abweichenden Pinbelegung gesperrt. Die bisherige CAD-Platinenhalterung gilt nur bei tatsächlicher Uno-Geometrie; eine Nano-Bauform benötigt eine andere Aufnahme.

## Funktion

X wählt die Drehrichtung; beide Y-Auslenkrichtungen bestimmen den Geschwindigkeitsbetrag. Dauerlauf mit Rampen oder eine vorgegebene Winkelfahrt; zur nächsten Fahrt muss X nach dem Ende wieder zentriert sein. Zentriert 1,1 s drücken und loslassen: ARM. Einmal drücken: Software-Stopp/LOCK. Doppelklick: Menü; Y = Seite, X = Wert, Druck = speichern und LOCK.

Getrennte Profile je Treiber: Vollschritte/U, Microsteps, RPM, Beschleunigung, Fahrtwinkel, Modus, Halten und Richtungsinversion. TB-Microstepping bleibt eine manuelle DIP-Einstellung. A4988-MS-Pins werden automatisch gesetzt. 4000 STEP-Impulse/s, Timer1 exklusiv.

## Verdrahtung

Pinout in DOCUMENTATION/pinout.md. Standardmäßig beide TB-ENA-Klemmen offen; der TB kann auch bei LOCK Haltestrom führen. A4988 RESET/SLEEP an VDD und 100 µF direkt an VMOT/GND. Getrennte, zum jeweiligen Treiber passende Motorversorgung; keine Motorleistung über den Board-5V-Pin. Den Motor nie gleichzeitig mit beiden Treiberausgängen verbinden und nur stromlos umstecken. Der vorhandene Anschlussplan setzt passende 5-V-Logik voraus; eine 3,3-V-Platine nicht ungeprüft gleich verdrahten.

## Dateien und Build

- `Stepper_Testbench_LGT8F328`: modulare Quellen, elektrische Optionen in Config.h.
- `single_file`: unabhängig kompilierbarer Sketch; Bibliothek und Core weiterhin erforderlich.
- `board_profiles.json`: p16/p32, d16/d32, p48_16/p48_32 mit eindeutigen Board- und Taktparametern.
- `firmware/PROFIL`: jeweilige Anwendung als HEX/ELF ohne Bootloader. Keine universelle HEX-Datei für alle Profile.
- `validation`: tatsächliche Buildlogs, native Tests und Ergebnis-JSON.
- `DOCUMENTATION`: eigenständige HTML-Anleitung, Pinout, Bedienung, Portierungsnotizen und Prüfbericht.
- `third_party`: unveränderte geprüfte Quellarchive; Herkunft/Prüfsummen in NOTICE.md.

```bash
arduino-cli core update-index --additional-urls https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json
arduino-cli core install arduino:avr@1.8.6
arduino-cli core install lgt8fx:avr@2.0.7 --additional-urls https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json
arduino-cli lib install "hd44780@1.3.2"
python tools/build.py --profile p16
python tools/make_single_file.py
python tools/build.py --profile p16 --single-file
python tools/run_tests.py
python tools/make_docs.py
```

Die Arduino-AVR-Plattform liefert bei Bedarf die Compilerwerkzeuge; das gewählte Ziel bleibt LGT8F328. Native Tests benötigen g++ mit ASan/UBSan, etwa unter Linux/WSL. Im restriktiven Container: `ASAN_OPTIONS=detect_leaks=0 python tools/run_tests.py`.

## Prüfstand und Grenzen

P/D und P-LQFP48 mit je 16/32 MHz sowie zwei P-Ein-Datei-Ausgaben wurden mit dem echten LGT-Core kompiliert. Portabler Bewegungskern automatisiert getestet. Kein realer Upload, Motor-, EEPROM-Retentions-, Oszilloskop- oder thermischer Test. Die D-EEPROM-Implementierung trägt zudem eine Warnung des Core-Autors zur fehlenden Hardwareerprobung. LGT-EEPROM ist Flash-emuliert und kann durch einen Upload gelöscht werden; danach Einstellungen kontrollieren. Speicherfehler sperren nach fehlgeschlagenem Zurücklesen. Winkel und RPM sind Impulsrechnungen ohne Encoder-Rückmeldung.
