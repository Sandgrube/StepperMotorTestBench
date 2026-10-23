# Elektrische Zugänge und Verdrahtung

## Drei getrennte Versorgungswege

USB bzw. der vorgesehene DC-Eingang versorgt den Uno. Der TB6600 hat seinen eigenen DC-Leistungseingang entsprechend dem Aufdruck des realen Moduls. Der A4988 bekommt VMOT separat von seiner5V-Logikversorgung. Die unterschiedlichen Motoreingänge sind mechanisch getrennt zugänglich. Es gibt keine automatische gemeinsame Spannungsanpassung und keine interne Netzspannung.

Für den Referenz-A4988 nennt Pololu8…35V an VMOT und3…5,5V an VDD. Das ist keine Freigabe für einen unbekannten Klon oder lange ungedämpfte Leitungen. Der lokale Elektrolytkondensator ist erforderlich; dieses Projekt sieht100µF vor. Bei anderer Versorgung muss auch seine Spannungsfestigkeit geprüft werden.

## Heck von außen gesehen

Von hinten betrachtet liegt der TB6600-Klemmenbereich links, die sechspolige A4988-Klemme mittig und die Uno-USB-/DC-Öffnung rechts. Die Positionen im CAD sind X-Koordinaten aus der Vorderansicht; bei Betrachtung von hinten ist die sichtbare Links-Rechts-Reihenfolge entsprechend gespiegelt. Versorgungskabel direkt mit TB bzw. A4988 und Polarität beschriften, bevor das Gerät eingeschaltet wird.

Von oben führen8mm breite Werkzeugfenster zu den Klemmschrauben. EinØ8-Loch über dem Referenz-Pot des A4988 dient ausschließlich dem spannungsfreien mechanischen Zugang. Für eine Vref-Messung vorzugsweise Deckel abnehmen und mit isoliertem Werkzeug arbeiten. Die Durchbrüche machen das Gehäuse weder staubdicht noch flüssigkeitsgeschützt.

## A4988-Träger: festgelegte Platzierung

| Teil | Koordinaten im Gehäuse |
| --- | --- |
| Lochraster | X75…115 / Y107…167 / PCB-Unterseite Z10 |
| 1×8-Sockel-Reihenmitten | X88,65 und X101,35; Pins in Y bei127,11 /129,65 /132,19 /134,73 /137,27 /139,81 /142,35 /144,89 |
| Treiber-PCB | Mitte X95 /Y136; PCB-Unterseite Z20,1 |
| 6-polige Klemme | X79,76…110,24 /Y158…166; Schraubenlinie Y162 |
| Kondensator | Mitte X109 /Y143; maximalØ10 ×16 |
| Kühlkörper | 10 ×10 ×10; Hülle X90…100 /Y134…144 |
| Pot-Referenz und Zugang | X95 /Y128; reale Klonposition zuerst kontrollieren |

Klemmenreihenfolge als eigene Beschriftung festlegen: VMOT+, GND,1A,1B,2A,2B. Die rote Platine in der Vorschau ist nur ein Referenzkörper. Verbindungsnetze nach den tatsächlichen A4988-Pinbezeichnungen löten; eine um180° gedrehte Platine kann zerstört werden. Keine Leiterbahnen oder elektrischen Netze sind im STEP elektrisch geprüft. Löten, Durchgangsprüfung, Polaritätsprüfung und Stromlimit-Einstellung bleiben notwendig.

## Verbindung zur vorhandenen Uno-Firmware

Die folgende Zuordnung wurde aus dem bereitgestellten Firmware-README vom22.10.2026 übernommen. Der Sketch wird durch dieses Gehäuseprojekt nicht verändert.

| Uno | Ziel |
| --- | --- |
| A0 / A1 / D2 | Joystick VRx / VRy / SW |
| A4 / A5 | LCD SDA / SCL |
| 5V / GND | LCD und Joystick; A4988 VDD und Logik-GND |
| D3 / D4 | TB6600 PUL+ / DIR+ |
| GND | TB6600 PUL− und DIR− im vorgesehenen Common-Cathode-Aufbau |
| D5 | TB6600 ENA+ nur bei ausdrücklich geprüfter optionaler Enable-Verdrahtung; im Standard beide ENA offen |
| D6 / D7 / D8 | A4988 STEP / DIR / ENABLE |
| D9 / D10 / D11 | A4988 MS1 / MS2 / MS3 |
| VDD lokal | A4988 RESET und SLEEP wie vorgesehen HIGH |
| Separates DC+ / DC− | A4988 VMOT / Motor-GND; Logik- und Motor-GND nach Carrier-Schaltbild verbinden |

TB6600-DIP-Schalter bleiben echte Hardware-Einstellungen. Der Firmware-Menüwert muss dazu passen. Nur der STEP-Ausgang wird softwareseitig ausgewählt; ein abgewählter Treiber ist dadurch nicht automatisch spannungsfrei. Die Leistungsausgänge beider Treiber niemals gleichzeitig auf denselben Motor legen. Beim Wechsel vollständig abschalten und anschließend umstecken. Strombegrenzungen vor der ersten Motorbewegung einstellen, nicht aus einer willkürlichen Vref-Formel für einen anderen Klon übernehmen.
