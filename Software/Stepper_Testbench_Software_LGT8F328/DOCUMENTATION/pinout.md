# Anschlussplan · Software 2.1

| Board / Versorgung | Ziel | Hinweis |
| --- | --- | --- |
| A0 | Joystick VRx | X: Richtung |
| A1 | Joystick VRy | Y: Geschwindigkeit in beiden Auslenkrichtungen |
| D2 | Joystick SW | Gegen GND schaltend; interner Pull-up |
| D3 | TB6600 PUL+ | STEP; PUL− an Board-GND |
| D4 | TB6600 DIR+ | DIR; DIR− an Board-GND |
| D5 | TB6600 ENA+ optional | Standard: ENA+ und ENA− beide offen lassen |
| D6 | A4988 STEP | Schrittimpulse |
| D7 | A4988 DIR | Drehrichtung |
| D8 | A4988 ENABLE | Aktiv LOW |
| D9 / D10 / D11 | A4988 MS1 / MS2 / MS3 | Microstepping durch die Firmware |
| A4 / A5 | LCD SDA / SCL | 100-kHz-I²C; Backpack automatisch erkannt |
| 5V | LCD VCC, Joystick VCC, A4988 VDD | Nur Logikversorgung |
| GND | LCD, Joystick, A4988 Logik-GND | Gemeinsame Logikmasse; TB-Signalminus wie oben |
| VDD lokal | A4988 RESET und SLEEP | Beide auf HIGH / 5V; nicht offen lassen |
| Separate DC-Versorgung | A4988 VMOT und Motor-GND | Motor-GND mit Logik-GND nach Carrier-Schaltbild verbinden |
| Separate DC-Versorgung | TB6600 VCC und Leistungs-GND | Spannung nach Aufdruck des konkreten Moduls |

Standard: TB6600 ENA+ und ENA− beide offen. PUL− und DIR− an Board-GND. Die Leistungsausgänge beider Treiber niemals gleichzeitig an denselben Motor anschließen.

A4988: RESET und SLEEP an VDD, 100 µF direkt zwischen VMOT und Motor-GND, passendes Stromlimit vor der ersten Fahrt. Motoren nur stromlos umstecken. Vollständige Inbetriebnahme und Grenzen: software_guide.html.
