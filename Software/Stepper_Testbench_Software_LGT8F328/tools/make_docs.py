#!/usr/bin/env python3
"""Generate the self-contained German HTML manual using only the standard library."""
from pathlib import Path
import html,json,hashlib

root=Path(__file__).resolve().parents[1]
docs=root/'DOCUMENTATION';docs.mkdir(exist_ok=True)
results=json.loads((root/'validation/results.json').read_text())
esc=html.escape
def table(headers,rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def mdtable(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(row)+' |\n' for row in rows)

pins=[
 ('A0','Joystick VRx','X: Richtung'),('A1','Joystick VRy','Y: Geschwindigkeit in beiden Auslenkrichtungen'),
 ('D2','Joystick SW','Gegen GND schaltend; interner Pull-up'),('D3','TB6600 PUL+','STEP; PUL− an Board-GND'),
 ('D4','TB6600 DIR+','DIR; DIR− an Board-GND'),('D5','TB6600 ENA+ optional','Standard: ENA+ und ENA− beide offen lassen'),
 ('D6','A4988 STEP','Schrittimpulse'),('D7','A4988 DIR','Drehrichtung'),('D8','A4988 ENABLE','Aktiv LOW'),
 ('D9 / D10 / D11','A4988 MS1 / MS2 / MS3','Microstepping durch die Firmware'),
 ('A4 / A5','LCD SDA / SCL','100-kHz-I²C; Backpack automatisch erkannt'),
 ('5V','LCD VCC, Joystick VCC, A4988 VDD','Nur Logikversorgung'),
 ('GND','LCD, Joystick, A4988 Logik-GND','Gemeinsame Logikmasse; TB-Signalminus wie oben'),
 ('VDD lokal','A4988 RESET und SLEEP','Beide auf HIGH / 5V; nicht offen lassen'),
 ('Separate DC-Versorgung','A4988 VMOT und Motor-GND','Motor-GND mit Logik-GND nach Carrier-Schaltbild verbinden'),
 ('Separate DC-Versorgung','TB6600 VCC und Leistungs-GND','Spannung nach Aufdruck des konkreten Moduls')]

menus=[
 ('1','Treiber','TB6600 / A4988','Wählt den STEP-Ausgang. Keine elektrische Umschaltung des Motors.'),
 ('2','Modus','Dauerlauf / Fahrt','Dauerlauf folgt dem Stick; Fahrt führt einen vorgegebenen Winkel aus.'),
 ('3','Vollschr','48 / 100 / 200 / 400','Physikalische Vollschritte pro Motorumdrehung, ohne Microstep-Faktor.'),
 ('4','Mikro','TB: 1…32; A: 1…16','TB: 1, 2, 4, 8, 16, 32. A: 1, 2, 4, 8, 16. TB-DIP manuell angleichen.'),
 ('5','Max RPM','3 / 5 / 10 / 15 / 20 / 30 / 45 / 60 / 90 / 120 / 180 / 240','Obergrenze; zusätzlich gelten maximal 4000 STEP-Impulse/s.'),
 ('6','Beschl','10 / 20 / 40 / 60 / 90 / 120 / 180 / 240 / 360 rpm/s','Beschleunigungs- und Bremsrampe im normalen Fahrbetrieb.'),
 ('7','Weg Grad','15 / 30 / 45 / 90 / 180 / 360 / 720 / 1440','Winkel an der Motorwelle, ohne automatische Getriebeumrechnung.'),
 ('8','Halten','Ein / Aus','A4988: Leerlauf-Haltestrom solange ARM. TB nur mit geprüfter optionaler ENA-Leitung.'),
 ('9','Richtung','Normal / Invertiert','Elektrische DIR-Polarität je Treiberprofil umkehren.')]

operation=[
 ('Einschalten','Stick zentriert lassen','Kalibrierung; anschließend LOCK. Es startet keine Fahrt.'),
 ('Freigeben','Zentriert 1,1 s drücken; dann loslassen','ARM. Der Stick muss während der gesamten Haltezeit zentriert bleiben.'),
 ('Richtung / Tempo','X links/rechts und Y auf/ab','X wählt die Richtung. Der Betrag der Y-Auslenkung bestimmt die Geschwindigkeit.'),
 ('Dauerlauf beenden','X oder Y in die Mitte','Der Sollwert fährt über die Bremsrampe auf null.'),
 ('Fahrt starten','Im Modus Fahrt beide Achsen auslenken','Eine Fahrt wird mit dem dabei gewählten Tempo gestartet; danach läuft sie unabhängig vom Stick zu Ende.'),
 ('Weitere Fahrt','X nach Fahrtende zentrieren, dann erneut auslenken','Keine vorab gespeicherte Wiederholung. Zentrieren während einer laufenden Fahrt bricht sie nicht ab.'),
 ('Stoppen / Sperren','Einmal kurz drücken','Neue STEP-Flanken werden gestoppt; ein bereits laufender Impuls endet. LOCK.'),
 ('Menü öffnen','Zweimal kurz drücken','Abstand der entprellten Druckereignisse unter 350 ms. Die erste Betätigung stoppt bereits.'),
 ('Menü bedienen','Y: Seite; X: Wert','Längeres Halten wiederholt. Bei diagonaler Eingabe wird nur die Seite gewechselt.'),
 ('Speichern / verlassen','Im Menü einmal drücken','EEPROM speichern, Ausgänge konfigurieren, zurück zu LOCK.')]

sections=[]
def section(id,title,body):sections.append((id,title,body))
section('start','1. LGT8F328 einrichten', """
<p>Diese Ausgabe 2.1 ist für <strong>LGT8F328P und LGT8F328D</strong> mit 16 oder 32 MHz angepasst. Die alte Auswahl „Arduino Uno“ ist hier gesperrt. Treiber, LCD, Joystick und Bedienung bleiben gleich.</p>
<div class="note"><strong>Die genaue Variante ist noch unbekannt.</strong> „LGT8F328“ allein legt weder P/D noch Bauform oder Versorgungsspannung fest. Die Profile sind geprüfte Buildziele; keines wurde als dein konkretes Board identifiziert. Nicht allein wegen eines passenden Namens eine beliebige HEX-Datei hochladen.</div>
<ol><li>In der Arduino IDE unter Datei → Voreinstellungen die zusätzliche Boardverwalter-URL eintragen:<pre>https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json</pre></li>
<li>In der Boardverwaltung <strong>lgt8fx 2.0.7</strong> installieren. Falls die Toolchain fehlt, zusätzlich Arduino AVR Boards installieren; als Ziel trotzdem LGT8F328 wählen.</li>
<li>Bibliothek <strong>hd44780 1.3.2 von Bill Perry</strong> installieren. Die unveränderte Bibliotheks-ZIP liegt auch in third_party. Nicht LiquidCrystal_I2C verwenden.</li>
<li>ZIP entpacken und <strong>Stepper_Testbench_LGT8F328/Stepper_Testbench_LGT8F328.ino</strong> öffnen. Die Begleitdateien im Sketchordner belassen. Alternativ die Ein-Datei-Ausgabe unter single_file öffnen.</li>
<li>Werkzeuge → Board → LGT8fx Boards → <strong>LGT8F328</strong>. Unter Variant die tatsächliche P/D- und Gehäuseausführung wählen. Für den anfänglichen 16-MHz-Betrieb: <strong>Clock Source = Internal 32MHz</strong>, <strong>Clock Divider = 2</strong>. Divider 1 entspricht 32 MHz. Nur diese beiden CPU-Takte sind freigegeben.</li>
<li>Den realen seriellen Port wählen. Upload speed zunächst nach vorhandenem Bootloader wählen; die bereitgestellten CLI-Profile verwenden 57600. Bei Verbindungsfehler kann ein anderer Bootloader 115200 verlangen. Es wird kein neuer Bootloader gebrannt.</li>
<li>Für den ersten Upload beide Motorversorgungen ausschalten; nur die passende Board-/USB-Logikversorgung betreiben. Joystick beim Start zentriert lassen. Serieller Monitor: <strong>115200 Baud</strong>, unabhängig von der Uploadgeschwindigkeit.</li>
<li>Stromlos verdrahten, Stromlimits und echte Microstep-DIP-Einstellung prüfen. Ersttest 5 RPM / 15° ohne mechanische Last.</li></ol>
"""+table(['Profil','Chip / Gehäuse','CPU-Takt','IDE-Variant / Divider'],[
('p16','LGT8F328P · LQFP32','16 MHz','328P-LQFP32 / 2'),('p32','LGT8F328P · LQFP32','32 MHz','328P-LQFP32 / 1'),('d16 / d32','LGT8F328D · LQFP32','16 / 32 MHz','328D / 2 bzw. 1'),('p48_16 / p48_32','LGT8F328P · LQFP48','16 / 32 MHz','328P-LQFP48 / 2 bzw. 1')])+"""
<p>Bei LQFP32 liegen acht Beinchen an jeder der vier Chipseiten, bei LQFP48 zwölf. P oder D muss vom Chipaufdruck bzw. einer verlässlichen Boardangabe kommen. Die zweireihige SSOP20-Variante wird wegen der anderen Pinbelegung von dieser Verdrahtung ausdrücklich abgewiesen.</p>
<p><strong>Versorgung:</strong> Der bisherige Anschlussplan setzt ein Board mit passender 5-V-Logik voraus. Eine vorhandene 3,3-V-Variante ist damit nicht automatisch elektrisch kompatibel zu LCD-Backpack und TB-Eingängen. Boardspannung vorher prüfen. Die Firmware hebt keine Spannung an.</p>
<p><strong>Gehäuse:</strong> Die bisherige CAD-Halterung entspricht dem Uno-R3-Format. Ein LGT-Chip kann auf Uno-, Nano- oder anderen Platinen sitzen. Nur bei tatsächlich passender Platinenkontur, Bohrungslage und USB-Position gilt diese Halterung weiter. Aus dem Chipnamen wird keine neue mechanische Passung abgeleitet.</p>
""")
section('bedienung','2. Bedienung',table(['Situation','Eingabe','Verhalten'],operation)+'''
<p>Der Knopf ist ein Software-Stopp mit 25-ms-Entprellung und zusätzlicher Laufzeit des Hauptablaufs; eine reale Reaktionszeit wurde nicht gemessen. Ein kurzer Stopp bremst nicht über die normale Rampe; die Mechanik kann nachlaufen oder Schritte verlieren. Nach jedem Stopp, Menübesuch und Neustart muss erneut freigegeben werden. Während der Freigabetaster noch gehalten wird, beginnen keine Pulse.</p>
<div class="lcd-label">Beispielanzeige · C = Dauerlauf, J = Fahrt</div><div class="lcd"><div>TB6600 C LOCK&nbsp;&nbsp;&nbsp;</div><div>Halt1.1s 2xMenue</div></div>
<p>ARM bedeutet freigegeben, RUN bedeutet laufender Pulsbefehl. RPM ist aus der ausgegebenen Pulsrate berechnet; es gibt keine gemessene Motordrehzahl. Bei einer Fahrt zeigt die zweite Zeile die verbleibenden STEP-Impulse.</p>
''')
section('menue','3. Profile und Einstellungen',table(['Nr.','Anzeige','Werte','Bedeutung'],menus)+'''
<p>Die beiden Treiber besitzen unabhängige Profile. Neue Standardwerte: 200 Vollschritte/U, 1/8 Microstepping, 15 RPM, 60 RPM/s, 180°, Dauerlauf, Halten aus, Richtung normal. Gültige vorhandene v1/v2-Daten werden erkannt. Beim LGT ist EEPROM jedoch Flash-emuliert; ein Firmwareupload kann diese Daten löschen. Nach jedem Upload die Profile kontrollieren.</p>
<p>Speichern erfolgt beim Verlassen des Menüs. CRC und Bereichsprüfungen verwerfen unvollständige oder ungültige EEPROM-Daten; dann gelten die Standardwerte. Die Firmware speichert nicht laufend während der Bewegung. Die LGT-E2PROM-Bibliothek wird mit 1 KB logischer Kapazität verwendet; der Flashbedarf ist in der Boardgrenze berücksichtigt. Jeder Speichervorgang wird zurückgelesen und mit CRC geprüft. Bei Fehler bleibt LOCK. Für den D-Chip kennzeichnet der Core seine EEPROM-Unterstützung selbst als ungetestet; der erfolgreiche Build ersetzt diese Hardwareprüfung nicht.</p>
''')
section('anschluss','4. Vollständiger Anschlussplan',table(['Board / Versorgung','Ziel','Funktion'],pins)+'''
<p>Die TB-Signale sind als <strong>Common Cathode</strong> vorgesehen: PUL− und DIR− an Board-GND, PUL+ und DIR+ direkt an D3 und D4. Das reale Modul muss für 5-V-Ansteuerung und den verfügbaren Pin-Ausgangsstrom geeignet sein. Modulbezeichnung allein beweist das nicht.</p>
<p>A4988-Motorwicklungen: eine Wicklung an 1A/1B, die andere an 2A/2B. TB6600: entsprechend A+/A− und B+/B−. Wicklungspaare vorab am stromlosen Motor identifizieren. Die Leistungsanschlüsse beider Treiber niemals gleichzeitig an denselben Motor legen. Für einen gemeinsamen Testmotor beide Treiberversorgungen ausschalten, dann manuell umstecken.</p>
<p>Keine Motorversorgung an den Board-5V-Pin anschließen. TB6600- und A4988-Spannung werden nicht automatisch angepasst; ihre zulässigen Spannungen können verschieden sein. USB versorgt hier die Logik. Ein externer Board-Versorgungseingang darf nur nach dem tatsächlichen Platinenaufbau verwendet werden; ein Nano-artiges LGT-Board besitzt nicht automatisch die Uno-DC-Buchse.</p>
''')
section('strom','5. Leistungsteil und Strombegrenzung','''
<p>Am A4988 einen <strong>100-µF-Elektrolytkondensator</strong> unmittelbar zwischen VMOT und Motor-GND montieren, richtige Polarität und passende Spannungsfestigkeit beachten. Für den im Gehäuse vorgesehenen 12/24-V-Aufbau ist ein geeigneter 50-V-Typ vorgesehen. Der Pololu-Referenzcarrier nennt 8–35 V Motorversorgung; das ist keine Freigabe für einen unbekannten Klon oder Spannungsspitzen.</p>
<p>Das A4988-Stromlimit wird am vorhandenen Potentiometer eingestellt. Die Beziehung des ICs lautet <code>Imax = Vref / (8 · Rsense)</code>. Erst die tatsächlich bestückten Messwiderstände und Carrier-Schaltung prüfen; keinen pauschalen Vref-Faktor für alle roten Platinen verwenden. TB6600-Stromlimit und Schrittauflösung werden an dessen DIP-Schaltern eingestellt.</p>
<p>Motorkabel und Treibermodule nur bei ausgeschalteter Versorgung umstecken. Lüftung und Kühlkörper freihalten. Die Firmware misst weder Temperatur noch Motorstrom und hat keine thermische Abschaltfunktion. Beim ersten Dauerlauf die Temperatur extern kontrollieren und das Stromlimit entsprechend anpassen.</p>
<p>Reset und Bootloader laufen vor der Firmware. Soll auch in dieser Zeit ein definierter A4988-Logikzustand bestehen, sind ein 10-kΩ-Pull-up von ENABLE zu VDD und ein 10-kΩ-Pull-down von STEP zu GND auf dem Träger sinnvoll. Software allein legt die Pins während Reset nicht fest.</p>
''')
section('tb-ena','6. TB6600: Microstepping und optionales ENA','''
<p><strong>Standard: beide ENA-Klemmen offen.</strong> Dann stoppt die Firmware die TB-Pulse, kann aber dessen Haltestrom nicht abschalten. Das gilt auch bei LOCK und wenn A4988 ausgewählt ist. Das Menü zeigt deshalb „TB ENA offen“.</p>
<p>Der TB-Menüwert für Microstepping ist eine Rechengröße. Er verstellt keine DIP-Schalter. Der eingestellte DIP-Teiler muss dazu passen; eine universelle DIP-ON/OFF-Tabelle wäre bei den unterschiedlichen Modulen unzuverlässig.</p>
<p>Optional: Nur bei überprüftem Modul ENA− an Board-GND und ENA+ an D5 anschließen. In Config.h <code>TB_ENABLE_WIRED 1</code> setzen und <code>TB_DISABLE_LEVEL</code> auf den gemessenen Offline-Pegel einstellen: 1 für HIGH = offline, 0 für LOW = offline. Vor dem ersten Fahrversuch ohne Last verifizieren. Die zusätzliche Variante wurde kompiliert; ihre elektrische Polarität wurde nicht an deinem Modul gemessen.</p>
''')
section('grenzen','7. Pulsrate, Rampen und Positionsgrenzen','''
<p>Timer1 verwendet ausdrücklich den CPU-Takt, nicht den LGT-Hochgeschwindigkeitstakt. OCR1A wird aus F_CPU berechnet: 199 bei 16 MHz und 399 bei 32 MHz, jeweils mit Prescaler 8. Damit ist der nominale Takt in beiden Profilen 10 kHz. Die Genauigkeit folgt dem realen Oszillator und wurde nicht gemessen. Maximal sind <strong>4000 STEP-Impulse/s</strong> vorgesehen. Der Scheduler plant nominal 100 µs HIGH und mindestens 100 µs LOW; die reale Flankenzeit und der Interrupt-Jitter wurden nicht am Oszilloskop gemessen. Timer1 darf nicht gleichzeitig von Servo- oder anderen Timer1-Bibliotheken benutzt werden. D9/D10 dienen ausschließlich als digitale Microstep-Signale.</p>
<pre>Pulse/U = Vollschritte/U × Microstep-Teiler
Fahrtpulse = rund(Winkel × Pulse/U / 360)
Maximal-RPM durch Pulslimit = 4000 × 60 / Pulse/U</pre>
'''+table(['200 Vollschritte/U','Pulse/U','RPM-Obergrenze'],[('1/8','1600','150'),('1/16','3200','75'),('1/32 · TB','6400','37,5')])+'''
<p>Beispiel: 200 Vollschritte/U und 1/8 ergeben 1600 Pulse/U; 90° entsprechen 400 Pulsen. Gewünschte Drehzahlen oberhalb des Pulslimits werden begrenzt. Der Weg wird auf ganze Mikrostep-Impulse gerundet. Ohne Encoder können tatsächlicher Winkel, Schrittverluste, Spiel und Bewegung bei abgeschaltetem Haltestrom nicht erkannt werden.</p>
<p>Normale Richtungswechsel bremsen zunächst auf null; danach warten DIR und Treiberfreigabe mindestens nominal 5 ms vor dem Anlauf. Endliche Fahrten verwenden eine abgetastete Beschleunigungs-/Bremsrampe und werden im Timer exakt nach der vorgegebenen Impulszahl beendet. Dies ist keine Garantie, dass ein überlasteter Motor allen Pulsen folgt.</p>
''')
section('fehler','8. Fehler und Diagnose',table(['Anzeige / Problem','Bedeutung und Vorgehen'],[
 ('FEHLER LCD/I2C · Code 1','Display wurde nicht initialisiert oder ein I²C-Zugriff schlug fehl. SDA/SCL, 5V, Masse, Backpack und Lötstellen prüfen; danach Reset.'),
 ('FEHLER Joystick · Code 2','Startkalibrierung unplausibel: Mittelwerte außerhalb 350…674 oder Streuung über 40 ADC-Schritte. Stick freigeben, Belegung prüfen, Reset.'),
 ('FEHLER Boardpins · Code 4','Der gewählte Core-/Varianten-Pinplan passt nicht zu den erwarteten Portleitungen. Boardvariante prüfen; keine Motorfahrt freigeben.'),
 ('FEHLER Speicher · Code 5','EEPROM-Kapazität oder Zurücklesen der gespeicherten Daten ist fehlerhaft. E2PROM des LGT-Cores verwenden und Versorgung prüfen; danach Reset.'),
 ('FEHLER Loop-Zeit · Code 3','Der Hauptablauf hat den Timer länger als etwa 100 ms nicht bedient. Pulsfreigabe bleibt gesperrt; Ursache beseitigen, Reset.'),
 ('LCD hell, keine lesbaren Zeichen','Backpack-Kontrast mit dem vorhandenen Potentiometer einstellen. Bei LCD/I²C-Fehler bleiben Fahrten gesperrt.'),
 ('ARM, aber keine Bewegung','Taster loslassen, X und Y auslenken; richtigen Treiber und Motorversorgung prüfen. Nach Fahrtende X erneut zentrieren.'),
 ('Drehrichtung vertauscht','Menüpunkt Richtung für das betroffene Profil ändern. Nur bei vertauschter Stickachse X_RIGHT_IS_HIGH ändern.'),
 ('Menü Y läuft verkehrt','Y_UP_IS_LOW in Config.h umschalten. Beide Y-Richtungen bleiben im Fahrbetrieb Geschwindigkeitsbeträge.'),
 ('TB hält trotz LOCK','Bei offenen ENA-Klemmen erwartetes Verhalten. LOCK verhindert Pulse und trennt keine Versorgung.'),
 ('Fahrtwinkel stimmt nicht','Vollschritte, tatsächliches DIP-/MS-Microstepping, mögliche Untersetzung, Schrittverluste und Haltestrom prüfen.'),
 ('Upload fehlgeschlagen','LGT8F328, richtige Variante und tatsächlichen Port wählen; seriellen Monitor schließen, Daten-USB-Kabel prüfen. Upload wurde hier nicht an realer Hardware getestet.')])+'''
<p>Serieller Monitor: 115200 Baud. <code>?</code> gibt Firmwareversion, kompiliertes Chipziel, CPU-Takt, Treiber, Sperrzustand, Fehlercode, rohe ADC-Werte, kalibrierte Mitte, Pulsrate und Restpulse aus. <code>s</code> stoppt und sperrt. Es gibt keinen seriellen Startbefehl.</p>
<p>Die Timer-Lease unterbindet bei einem blockierten Hauptablauf neue Pulse und deaktiviert A4988 sowie optional TB-ENA. Sie ist softwarebasiert und funktioniert nur bei weiterlaufendem Timer-Interrupt. Sie ersetzt keine Stromtrennung. Joystick-Kabelbruch und mechanisches Nachlaufen werden nicht zuverlässig erkannt.</p>
''')
section('build','9. Reproduzierbarer LGT-Build', """
<p>Für normale Nutzung genügt die Arduino IDE. Die folgende CLI-Installation verwendet den geprüften Core. Die Arduino-AVR-Plattform liefert gegebenenfalls die AVR-Toolchain; das eigentliche Buildziel bleibt lgt8fx.</p>
<pre>arduino-cli core update-index --additional-urls https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json
arduino-cli core install arduino:avr@1.8.6
arduino-cli core install lgt8fx:avr@2.0.7 --additional-urls https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json
arduino-cli lib install "hd44780@1.3.2"
python tools/build.py --profile p16</pre>
<p>Das Profil p16 ist die Bauvorgabe für P/LQFP32 bei 16 MHz, keine automatische Erkennung deiner Hardware. Bei abweichender Chipausführung entsprechend d16, d32, p32, p48_16 oder p48_32 wählen. Die vollständigen FQBNs stehen in board_profiles.json. HEX/ELF liegen getrennt in firmware/PROFIL; es gibt keine universelle Binärdatei für alle Takte.</p>
<pre>python tools/make_single_file.py
python tools/build.py --profile p16 --single-file
python tools/run_tests.py
python tools/make_docs.py</pre>
<p>Für einen manuellen CLI-Upload die passende FQBN und genau die zugehörige HEX-Datei verwenden. COM5 ist nur ein Beispiel:</p>
<pre>arduino-cli upload --fqbn lgt8fx:avr:328:variant=modelP,clock_source=internal,clock_div=2,upload_speed=57600 -p COM5 --input-file firmware/p16/Stepper_Testbench_LGT8F328.hex</pre>
<p>Die HEX-Dateien enthalten die Anwendung ohne Bootloader. Für den normalen IDE-Upload müssen sie nicht separat geöffnet werden. Die nativen Verhaltenstests benötigen g++ mit AddressSanitizer/UndefinedBehaviorSanitizer, etwa unter Linux/WSL. Im verwendeten Container war nur LeakSanitizer wegen /proc-Einschränkungen ausgeschaltet.</p>
""")
buildrows=[]
for key,r in results['builds'].items():
    buildrows.append((key,f"{r['flash_bytes']} / {r['flash_limit']} Byte",f"{r['static_ram_bytes']} / 2048 Byte",'Kompiliert'))
section('validierung','10. Prüfstatus',table(['Ausgabe','Flash','Statischer RAM','Ergebnis'],buildrows)+'''
<p>Toolchain: Arduino CLI 1.5.1, lgt8fx-Paket 2.0.7, AVR-GCC 7.3.0-atmel3.6.1-arduino7 und hd44780 1.3.2. Alle sechs Board-/Taktprofile sowie zwei P-Ein-Datei-Ausgaben wurden kompiliert. Build-Logs liegen in validation. Statischer Speicherbedarf und verbleibender SRAM sind keine gemessene Stackreserve. Die D-Builds enthalten die dokumentierte Warnung des Core-Herstellers zur nicht physisch getesteten D-EEPROM-Emulation.</p>
<ul><li>Die Timer-Vergleichswerte für 16/32 MHz und alle ganzzahligen Raten 1…4000 PPS über jeweils 10.000 Scheduler-Takte: Pulszahl und Mindestabstand geprüft.</li><li>Endliche Blöcke, laufenden HIGH-Impuls beenden, letzte Flanke, kein Wiederanlauf nach Fahrtende, Timer-Lease.</li><li>Tasterentprellung, Doppelklick, kontinuierlich zentrierte Freigabe, Loslasssperre, millis()-Überlauf.</li><li>Richtungswechsel erst bei Stillstand, Freigabe-/DIR-Wartezeiten, getrennte Treiberausgänge, Menü, Halten und Fehlersperren.</li><li>Alle Fahrtwinkel-Presets, kleinste Fahrt mit 2 und größte Fahrt mit 51.200 Impulsen, CRC/EEPROM-Migration und 16-Zeichen-Anzeigepuffer.</li></ul>
<div class="note"><strong>Offen:</strong> Kein realer Upload, elektrischer Versuch, Oszilloskop-Timing, Motorlastversuch oder thermischer Dauertest. Die nativen Tests verwenden denselben C++-Kern, aber einen modellierten Hardwareadapter. Sie simulieren weder die vollständige AVR-Interruptpriorität noch tatsächliche Optokoppler, LCD-Verkabelung oder Motorbewegung.</div>
''')
section('checkliste','11. Ersttest zum Abhaken','''
<ul class="checklist"><li>Pinbelegung und Modulorientierung bei ausgeschalteten Versorgungen geprüft.</li><li>A4988-VMOT-Kondensator, Polarität und Stromlimit kontrolliert.</li><li>TB-DIP-Strom und Microstep-Teiler kontrolliert; ENA im Standard offen.</li><li>USB-Upload funktioniert; Display zeigt LOCK; ADC-Mitten im seriellen Status plausibel.</li><li>Kurzer Tastendruck sperrt; Doppelklick öffnet Menü; Speichern führt zu LOCK.</li><li>Beide Profile stimmen mit den tatsächlich angeschlossenen Motoren überein.</li><li>Ersttest 5 RPM / 15° ohne Last; Richtung und Winkel geprüft.</li><li>Joystickzentrierung im Dauerlauf bremst; kurzer Tastendruck stoppt auch eine Fahrt.</li><li>Keine wiederholte Fahrt ohne X-Mittelstellung nach Fahrtende.</li><li>Bei langsamem, lastfreiem Versuch mit Steuerspannung einen LCD-Verbindungsfehler prüfen: Pulse müssen nach erkanntem Fehler gesperrt bleiben. Leistungsteil dabei nicht umverdrahten.</li><li>Erst danach Drehzahl, Beschleunigung, Strom und Versuchsdauer schrittweise erhöhen.</li></ul>
''')
section('quellen','12. Quellen und Projektdateien','''
<p>Die Paketquellen wurden auf die genannten Versionen festgelegt. Die LGT-Portierung wurde zusätzlich mit den LogicGreen-Datenbüchern P 1.0.5 und D 1.0.5 abgeglichen; Registerdetails stehen in lgt_port_notes.md. hd44780 und lgt8fx liegen als unveränderte Quellarchive unter third_party; ihre Prüfsummen und Herkunft stehen in NOTICE.md. Der eigene Firmwarecode steht unter GPL-3.0, Fremdcode behält seine enthaltenen Hinweise.</p>
<ul><li><a href="https://github.com/duinoWitchery/hd44780/tree/1.3.2">hd44780 von Bill Perry</a> – Backpack-Erkennung und LCD-API.</li><li><a href="https://github.com/dbuezas/lgt8fx/tree/v2.0.7">lgt8fx 2.0.7</a> – Boardprofile, ADC, Wire und E2PROM.</li><li><a href="https://docs.arduino.cc/arduino-cli/commands-reference/arduino-cli_compile">Arduino CLI</a> – Build und Boardauswahl.</li><li><a href="https://www.pololu.com/product/1182">Pololu A4988 Carrier</a> und <a href="https://www.pololu.com/file/0J450/a4988_DMOS_microstepping_driver_with_translator.pdf">Allegro A4988</a> – Referenzanschluss, Microstep-Tabelle und Stromlimit.</li><li><a href="https://www.handsontec.com/dataspecs/module/TB6600-Motor-Driver.pdf">Handson TB6600-Modul</a> – Beispiel für ein 5-V-Optokopplermodul; kein universelles Klon-Datenblatt.</li></ul>
<p>Die Anleitung funktioniert vollständig offline. Die Links dienen der Quellenangabe; keine externen Schriftarten, Bilder, Skripte oder Styles werden nachgeladen.</p>
''')

nav=''.join('<a href="#'+id+'">'+esc(title)+'</a>' for id,title,_ in sections)
body=''.join('<section id="'+id+'"><h2>'+esc(title)+'</h2>'+content+'</section>' for id,title,content in sections)
css='''
:root{--ink:#20282c;--muted:#5b666b;--line:#dce2e4;--accent:#215d54;--paper:#fff;--bg:#f3f5f5}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,-apple-system,Segoe UI,Arial,sans-serif}a{color:var(--accent)}.layout{display:grid;grid-template-columns:240px minmax(0,1fr);max-width:1320px;margin:auto}aside{position:sticky;top:0;align-self:start;height:100vh;padding:34px 22px;background:#e9eeee;border-right:1px solid var(--line);overflow:auto}aside strong{font-size:14px;letter-spacing:.1em}nav{display:grid;gap:5px;margin-top:26px}nav a{text-decoration:none;color:#3b4b4e;font-size:13px;line-height:1.35;padding:8px 0}nav a:hover{text-decoration:underline}main{min-width:0;padding:44px 48px 68px;background:var(--paper)}header{padding:0 0 32px;border-bottom:2px solid var(--ink)}.eyebrow{font-size:12px;letter-spacing:.16em;font-weight:700;color:var(--accent);text-transform:uppercase}h1{font-size:42px;line-height:1.12;letter-spacing:-.035em;margin:14px 0}header p{max-width:720px;color:var(--muted);font-size:18px}.meta{display:flex;gap:12px;flex-wrap:wrap;font-size:12px;color:var(--muted)}.meta span{border:1px solid var(--line);padding:4px 9px;border-radius:3px}section{padding-top:28px;margin-top:18px;border-bottom:1px solid var(--line);padding-bottom:24px}h2{font-size:24px;line-height:1.25;letter-spacing:-.02em;margin:10px 0 22px}p{margin:15px 0}li{margin:9px 0}ol,ul{padding-left:24px}.table-wrap{overflow:auto;margin:18px 0}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.5}th{text-align:left;background:#edf2f1;font-size:12px;color:#3c5050}td,th{padding:12px 13px;border-bottom:1px solid var(--line);vertical-align:top}td:first-child{font-weight:600;min-width:72px}tr:last-child td{border-bottom:1px solid #c4cecd}.note{background:#eff5f3;border-left:3px solid var(--accent);padding:16px 20px;margin:22px 0;font-size:14px}.lcd-label{font-size:12px;color:var(--muted);margin-top:26px}.lcd{display:inline-block;background:#c7d3ae;border:9px solid #343d38;border-radius:3px;padding:12px 20px;margin:7px 0 14px;color:#28372c;font:20px/1.45 ui-monospace,Consolas,monospace;white-space:pre;box-shadow:inset 0 1px 4px #0003}code,pre{font-family:ui-monospace,Consolas,monospace;font-size:.88em}code{background:#edf1f1;padding:2px 4px;border-radius:2px}pre{background:#eef2f2;padding:20px;line-height:1.7;overflow:auto;border:1px solid var(--line)}.checklist{list-style:none;padding:0}.checklist li{position:relative;padding-left:28px}.checklist li:before{content:"";position:absolute;left:1px;top:7px;width:13px;height:13px;border:1px solid #78928b}footer{font-size:12px;color:var(--muted);padding-top:28px}button{background:#fff;border:1px solid #b8c5c1;border-radius:3px;padding:8px 12px;font:inherit;font-size:12px;cursor:pointer;margin-top:20px}@media(max-width:900px){.layout{display:block}aside{position:static;height:auto;padding:22px}nav{grid-template-columns:repeat(2,minmax(0,1fr));margin-top:12px}main{padding:28px 24px}h1{font-size:34px}}@media print{body{background:white;font:10pt/1.45 Arial,sans-serif}.layout{display:block}aside,button{display:none}main{padding:0}header{padding-bottom:16px}h1{font-size:28pt}h2{font-size:16pt;break-after:avoid}section{padding:12px 0;margin:12px 0;break-inside:auto}tr,.note,.lcd{break-inside:avoid}td,th{padding:7px 8px;font-size:9pt}a{color:#20282c;text-decoration:none}pre{white-space:pre-wrap;font-size:8pt}.table-wrap{overflow:visible}@page{size:A4;margin:17mm}}
'''
page='<!DOCTYPE html>\n<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stepper Testbench · Software 2.1</title><style>'+css+'</style></head><body><div class="layout"><aside><strong>STEPPER<br>TESTBENCH</strong><nav>'+nav+'</nav><button onclick="window.print()">Drucken / als PDF speichern</button></aside><main><header><div class="eyebrow">Firmware &amp; Inbetriebnahme</div><h1>Der Teststand.<br>Die Software.</h1><p>LGT8F328 · TB6600 · A4988 · XY-Joystick · 16×2-LCD</p><div class="meta"><span>Version 2.1.0</span><span>24.10.2026</span><span>Pinbelegung Gehäuse R1</span><span>AVR-Build geprüft</span></div></header>'+body+'<footer>Stepper Testbench · Software 2.1.0 · Digitale Prüfung abgeschlossen; reale Hardware-Inbetriebnahme steht aus.</footer></main></div></body></html>'
(docs/'software_guide.html').write_text(page)

(docs/'pinout.md').write_text('# Anschlussplan · Software 2.1\n\n'+mdtable(['Board / Versorgung','Ziel','Hinweis'],pins)+'\nStandard: TB6600 ENA+ und ENA− beide offen. PUL− und DIR− an Board-GND. Die Leistungsausgänge beider Treiber niemals gleichzeitig an denselben Motor anschließen.\n\nA4988: RESET und SLEEP an VDD, 100 µF direkt zwischen VMOT und Motor-GND, passendes Stromlimit vor der ersten Fahrt. Motoren nur stromlos umstecken. Vollständige Inbetriebnahme und Grenzen: software_guide.html.\n')
(docs/'operation.md').write_text('# Bedienung · Software 2.1\n\n'+mdtable(['Situation','Eingabe','Verhalten'],operation)+'\n## Menü\n\n'+mdtable(['Nr.','Anzeige','Werte','Bedeutung'],menus)+'\nTB-DIP und Menü müssen zusammenpassen. Die Winkel- und Drehzahlangaben beruhen auf STEP-Impulsen, nicht auf Encoder-Messung.\n')
(docs/'validation_report.md').write_text(f"""# Validierung · Firmware 2.1.0 / LGT8F328

Stand: 24.10.2026. Die genaue P/D- und Platinenvariante des Nutzers ist noch nicht identifiziert.

{mdtable(['Buildprofil','Flash','Statischer RAM','Ergebnis'],buildrows)}
Toolchain: Arduino CLI 1.5.1; lgt8fx-Paket 2.0.7; AVR-GCC 7.3.0-atmel3.6.1-arduino7; hd44780 1.3.2. D-Core-Warnungen zur ungetesteten EEPROM-Emulation wurden beibehalten und nicht als eigener Hardwaretest ausgegeben.

Die Timer-Konfiguration ist F_CPU-abhängig: Prescaler 8, OCR1A 199/399 für 16/32 MHz, TC2XS1 gelöscht. Nominal 10 kHz in beiden Fällen. ADC ausdrücklich 10 Bit bei VCC-Referenz. Direkte Portzuordnung der verwendeten digitalen und analogen Pins wird beim Start geprüft. EEPROM-Schreibdaten werden zurückgelesen und mit CRC geprüft; das ist noch kein tatsächlicher Flash-Lebensdauertest.

Native Tests: C++11, -O2, -Wall -Wextra -Werror -pedantic, AddressSanitizer und UndefinedBehaviorSanitizer. LeakSanitizer im Container ausgeschaltet. {results['tests']['assertions']:,} Assertions einschließlich wiederholter Scheduler-Invarianten; keine Anzahl unabhängiger Szenarien. Geprüft: Timerwerte, alle Raten 1…4000 PPS, endliche Impulsblöcke, letzter HIGH-Impuls, kein Wiederholstart, Lease, Tastergesten, millis-Überlauf, Fahrtrampen/Umkehr, minimale und maximale Fahrt, Anlaufmatrix, CRC/Migration und alle fünf Fehleranzeigen. Logs in validation.

Offen: tatsächliches Board/Versorgung/Bootloader, Upload, EEPROM-Retention auf diesem Board, Oszilloskop-Timing/Jitter, Motorlast, Stromlimit und thermischer Dauerlauf. Der native Hardwareadapter ist ein Modell. Die LGT-internen RC-Oszillatoren wurden nicht vermessen. Kompilieren bestätigt die Ziel-Core-Schnittstelle und den Speicherbedarf, keine physische Kompatibilität einer unbekannten Platine.
""")
(root/'README.md').write_text("""# Stepper Testbench · LGT8F328 · Firmware 2.1.0

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
""")
(docs/'board_setup.md').write_text("""# Boardauswahl LGT8F328

Die Angaben des Nutzers enthalten bislang nur LGT8F328. P/D, Gehäuse, Platinenformat und Logikspannung sind noch offen. Nicht anhand der Softwareausgabe einen physischen Chip identifizieren: der serielle Status nennt das kompilierte Ziel, keine automatisch ausgelesene Chipidentität.

IDE: Zusatz-URL https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json; Paket lgt8fx 2.0.7; Board LGT8F328. Variant nach tatsächlichem Chipaufdruck wählen. LQFP32: acht Beinchen pro Chipseite, LQFP48: zwölf. SSOP20 wird von diesem Kabelplan nicht unterstützt. Bei unleserlichem Aufdruck Platinenfoto bzw. genaue Produktkennung zur Identifikation verwenden.

CPU 16 MHz: Internal 32MHz / Clock Divider 2. CPU 32 MHz: Internal 32MHz / Clock Divider 1. Uploadgeschwindigkeit hängt vom vorhandenen Bootloader ab, nicht vom seriellen Monitor (115200). CLI-Profile verwenden 57600; andere Bootloader können 115200 brauchen. Keine Bootloader-Neuprogrammierung erforderlich oder getestet.

Die vorliegende Verdrahtung ist für passende 5-V-Logik ausgelegt. Boardspannung prüfen. Die Uno-CAD-Montage ist nur bei passender Uno-Platinengeometrie gültig; LGT bedeutet nicht automatisch Uno-Format.
""")
(docs/'lgt_port_notes.md').write_text("""# LGT-Portierung: technische Entscheidungen

Version 2.1.0, Paket lgt8fx 2.0.7 aus dem Maintainer-Release; SHA256 des unveränderten Archivs in NOTICE.md.

- Der Core kompiliert mit -mmcu=atmega328p, definiert aber erst über pins_arduino.h die LGT-Makros __LGT8F__ und __LGT8FX8P__/__LGT8FX8E__. Deshalb ist allein __AVR_ATmega328P__ keine Boarderkennung. Diese Ausgabe fordert ausdrücklich den LGT-Core.
- Die CPU-Frequenz kommt aus F_OSC/F_DIV. Prescaler 8 und OCR1A=F_CPU/(8*10000)-1 ergeben 199/399 für 16/32 MHz. TC2XS1 in TCKSR (0xEC), Bit 1, wird gelöscht: Timer1 arbeitet mit dem Systemtakt, nicht dem separaten Hochgeschwindigkeitstakt. Timer0 bleibt unverändert. TCCR1A/B/C und gegebenenfalls TCCR1D werden initialisiert; ein ausstehendes Compare-Flag wird gelöscht.
- Beleg: LogicGreen LGT8FX8P Databook 1.0.5 English, PDF-Seiten 139–140 und 151–152; LGT8FX8D Programming Manual 1.0.5, PDF-Seiten 90–91 und 102. Dateien aus https://github.com/dbuezas/lgt8fx/tree/master/docs . Die englische D-Fassung ist eine im Repository mitgelieferte Übersetzung.
- analogReadResolution(10) und analogReference(DEFAULT) normalisieren den Joystickbereich auf 0…1023 relativ zur Board-Versorgung. Ohne passende Versorgung bleibt der analoge Bereich trotzdem hardwareabhängig.
- E2PROM/EEPROM des LGT-Cores verwenden. Der falsche Arduino-EEPROM-Header wird beim Kompilieren abgewiesen. 1 KB logische Emulation wird gesetzt; keine größere Flashreserve wird aktiviert. EEPROM.update begrenzt unnötige Schreibzugriffe. Zurücklesen, Bytevergleich und CRC prüfen jeden gespeicherten Datensatz. Die Maintainer-Warnung für die D-Emulation wird nicht unterdrückt.
- D2…D11, A0/A1 und A4/A5 werden beim Start gegen die erwarteten Portregister/Bitmasken geprüft. Eine abweichende Software-Pinmap bleibt LOCK mit Fehler 4. SSOP20 wird bereits beim Kompilieren gesperrt. Falsche physische Boardbeschriftungen werden dadurch nicht erkannt.
- Fehler 5 bezeichnet eine zu kleine oder fehlgeschlagene EEPROM-Schnittstelle. Kein Zugriff auf zusätzlichen DAC, PGA, LEDs, Taster oder sonstige Module.

Native Tests prüfen den Bewegungskern und beide Timerkonstanten. LGT-Builds prüfen Core-APIs und Ressourcen. Weder die Datenbuchprüfung noch der Compiler ersetzen Timing-/Flash-/Motorversuche am realen Board.
""")
notices=['# Herkunft und Lizenzen\n\nEigene Firmwarequellen dieses Pakets: GPL-3.0. Volltext in LICENSE.txt. Drittquellen behalten ihre eingebetteten Lizenz- und Urheberhinweise.\n\nDie kompilierten Anwendungen verwenden hd44780 von Bill Perry und den LGT8fx-Core. Die unveränderten Quellarchive liegen bei. Der Compiler ist nicht im Paket enthalten.\n']
deps=json.loads((root/'third_party/dependencies.json').read_text()) if (root/'third_party/dependencies.json').exists() else []
for path in sorted((root/'third_party').glob('*')):
    if path.suffix=='.json':continue
    notices.append(f'\n## {path.name}\n\nSHA256: `{hashlib.sha256(path.read_bytes()).hexdigest()}`\n')
    if path.name.startswith('hd44780'):notices.append('\nQuelle: https://github.com/duinoWitchery/hd44780/tree/1.3.2\n')
    else:notices.append('\nQuelle: https://github.com/dbuezas/lgt8fx/tree/v2.0.7\n')
(root/'NOTICE.md').write_text(''.join(notices))
print('Generated HTML manual, README, pinout, operation and validation report.')

