#!/usr/bin/env python3
"""Build the offline manual and Markdown engineering record from one source."""
import argparse,base64,html,json,math,re
from pathlib import Path
from enclosure.common import geometry,normalize_parameters

ROOT=Path(__file__).resolve().parents[2]

def table(headers,rows):
    return '| '+' | '.join(str(x) for x in headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(str(x) for x in row)+' |\n' for row in rows)

def inline(s):
    s=html.escape(s)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
    return s

def md_html(text):
    lines=text.strip().splitlines();out=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('```'):
            code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');i+=1;continue
        if line.startswith('#'):
            n=len(line)-len(line.lstrip('#'));out.append(f'<h{min(n+1,5)}>'+inline(line[n:].strip())+f'</h{min(n+1,5)}>');i+=1;continue
        if line.startswith('|') and i+1<len(lines) and re.match(r'^\|[\s:|\-]+\|$',lines[i+1]):
            headers=[x.strip() for x in line.strip('|').split('|')];out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(x)+'</th>' for x in headers)+'</tr></thead><tbody>');i+=2
            while i<len(lines) and lines[i].startswith('|'):
                vals=[x.strip() for x in lines[i].strip('|').split('|')];out.append('<tr>'+''.join('<td>'+inline(x)+'</td>' for x in vals)+'</tr>');i+=1
            out.append('</tbody></table></div>');continue
        if line.startswith('- ') or re.match(r'^\d+\. ',line):
            ordered=not line.startswith('- ');tag='ol' if ordered else 'ul';out.append('<'+tag+'>')
            while i<len(lines) and (re.match(r'^\d+\. ',lines[i]) if ordered else lines[i].startswith('- ')):
                out.append('<li>'+inline(re.sub(r'^(?:\d+\.|-) ', '',lines[i]))+'</li>');i+=1
            out.append('</'+tag+'>');continue
        block=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','- ','```')) and not re.match(r'^\d+\. ',lines[i]):block.append(lines[i]);i+=1
        out.append('<p>'+inline(' '.join(block))+'</p>')
    return '\n'.join(out)

def image_data(root,name):
    data=(root/'PREVIEWS'/name).read_bytes();return 'data:image/png;base64,'+base64.b64encode(data).decode()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--params',type=Path,default=ROOT/'CAD/parameters/default.json');ap.add_argument('--output',type=Path,default=ROOT)
    args=ap.parse_args();root=args.output.resolve();p=normalize_parameters(json.loads(args.params.read_text()));e=p['enclosure'];_,H,seat=geometry(p)
    r=json.loads((root/'DOCUMENTATION/validation_results.json').read_text())
    if r['failures']:raise RuntimeError('Refusing to issue a manual for failed geometry: '+str(r['failures']))
    docs={}
    docs['architecture.md']='''# Aufbau und Auswahl

Der Entwurf ist ein vollständig modellierter, passiv belüfteter Laboraufbau für die fünf vorgegebenen Module. Die Front trägt ausschließlich das vorhandene LCD und den Joystick. Alle Netzteile bleiben außerhalb. Drei Gehäuseteile: Bodenschale, fest verschraubte geneigte Front, separat abnehmbarer hinterer Deckel. Auf der Front sind keine Schraubenköpfe sichtbar; zwei Senkschrauben halten den Wartungsdeckel.

Verglichen wurden drei Verpackungsprinzipien. Nur Variante B wurde detailliert konstruiert und geometrisch geprüft. Die anderen Maße sind grobe Planungsabschätzungen, keine exportierten Alternativmodelle.

'''+table(['Variante','Planungsmaß / Quader','Bewertung'],[
        ['A: Treiber unter den Bedienelementen übereinander','ca. 180 × 176 × 85 mm / 2,69 l','Kleine Stellfläche; thermische Kopplung zum LCD; obere Module müssten zur Wartung heraus.'],
        ['B: Drei Funktionszonen nebeneinander; gewählt',f'{e["width"]:.0f} × {e["depth"]:.0f} × {H:.2f} mm / {e["width"]*e["depth"]*H/1e6:.2f} l','Gemeinsamer offener Wartungsraum; eigene Wärmewege; kurze direkte Heckanschlüsse.'],
        ['C: Alle Module hintereinander','ca. 150 × 230 × 72 mm / 2,48 l','Schmale, tiefe Stellfläche; mehr Leitungslänge und schlechtere seitliche Werkzeugzugänge.']])+'''
Die etwas größere Breite der gewählten Variante schafft reale Breite für Uno, 40-mm-Lochrasterplatine, TB6600 und deren Halter. Die vordere Zone enthält die Rückseiten von LCD und Joystick, vier Frontstützen sowie den Kabelbogen. Sie ist kein Platz für zusätzliche Elektronik.

Der TB6600 wird mit zwei verschiebbaren Bügeln und weichen Auflagepolstern gehalten. Originale Gehäuseschrauben und unbestätigte Modul-Bohrbilder werden nicht benutzt. Die Lochrasterplatine sitzt in Kantenhaltern und benötigt keine gebohrten Befestigungslöcher. Die Joystick-Montage verwendet vier 2-mm-Distanzringe; dünnere Ringe können einen kürzeren Knopf näher an die Außenseite bringen. Eine geänderte Bestückung ist erneut am Probestück zu prüfen.
'''
    u=p['uno'];l=p['lcd'];j=p['joystick'];q=p['a4988'];t=p['tb6600']
    docs['dimensions.md']=f'''# Maße, Koordinaten und Toleranzen

Alle Maße in Millimeter. X läuft von links nach rechts, Y von vorne nach hinten, Z nach oben. Z = 0 ist die Unterseite der Bodenschale. Der Parameter `height` bezeichnet die obere hintere Gehäusekante. Gummifüße und Joystick sind darin nicht enthalten.

Die Frontkoordinate t läuft auf der geneigten Fläche nach hinten; n zeigt senkrecht nach außen. Die Außenseite liegt bei n = 0. Für den Standardentwurf: Y = t cos(18°) − n sin(18°), Z = 35 + t sin(18°) + n cos(18°).

'''+table(['Merkmal','Standard'],[
    ['Gehäuse / Front',f'{e["width"]:.0f} × {e["depth"]:.0f} × {H:.3f}; vorne {e["front_height"]:.3f}; 18° zur Tischfläche'],
    ['Materialstärken','Wände 2,4; Boden 3,0; Front und Deckel 3,0; äußere Eckradien 4,0'],
    ['Standfüße','4 × Ø14 × 4; auf glatte Unterseite kleben; 4 mm Luft unter dem Boden'],
    ['LCD-Mitte / Fenster','X 78; t 47,5; Fenster 66,8 × 17,8; rückseitige Tasche 72,4 × 26,4'],
    ['LCD-Anlage','PCB-Vorderseite n −9,6; Metallfront n −1,0; 75 × 31 Lochabstand'],
    ['Joystick-Mitte / Durchbruch','X 180; t 47,5; Ø29,2; PCB-Vorderseite n −15,2 mit 2,0 Distanzringen'],
    ['Joystick-Bohrbild','20 × 26, ausdrücklich unbestätigte Referenz; vier Offsets ±10 / ±13'],
    ['TB6600','X 124…220; Y 94…165; Z 10…47; 96 × 71 × 37 Gesamthülle'],
    ['A4988-Lochraster','X 75…115; Y 107…167; PCB-Unterseite Z 10; 40 × 60 × 1,6'],
    ['A4988-Sockel','zwei Reihen 1×8; Raster 2,54; Reihenmittenabstand 12,70; Sockelhöhe 8,5'],
    ['Kondensatorreserve','Ø10 × 16 über Lochraster; Mittelpunkt X109 / Y143'],
    ['Hintere Werkzeugschlitze','TB: X135…209 / Y153…161; A4988: X77…113 / Y159…167'],
    ['Lüftung','Schlitzbreite 3,2; Deckelschlitze Länge 24; Raster 6; seitliche Schlitze mit Dachspitze']])+'''
## Uno-Montage: belegte Koordinaten

Die offiziellen Eagle-Koordinaten sind u/v, mit u längs der Platine und den Buchsen bei u ≈ 0. Einbau: X = 14 + v, Y = 169,5 − u. PCB-Unterseite Z = 10. Die drei verwendeten Schrauben sind M2,5; die vierte Stelle erhält nur einen Ø2,5 × 0,95-mm-Locator. Damit bleibt der sehr knappe Platz neben der Headerleiste frei. An der DC-Buchse keine große Unterlegscheibe verwenden. Schraubenkopf dort höchstens Ø4,5.

'''+table(['Index','Offiziell u / v','Global X / Y','Befestigung'],[(i,f'{uu:.2f} / {vv:.2f}',f'{u["origin_x"]+vv:.2f} / {u["rear_board_edge_y"]-uu:.2f}','Locator' if i==2 else 'M2,5 × 8') for i,(uu,vv) in enumerate(u['holes'])])+'''
Der Platinenumriss 68,58 × 53,34 und die vier Ø3,2-Montagelöcher stammen aus dem offiziellen Board. Kleine gerundete Platinen-Ecken sind im Referenzkörper als kurze Fasen angenähert. Die USB- und DC-XY-Hüllen stammen aus den offiziellen Footprints; deren Höhen und die Steckerumhüllungen sind Annahmen. Das STEP-Referenzmodell ersetzt keine Vermessung eines Uno-Klons.

## Funktionsbezogene FDM-Zugaben

'''+table(['Schnittstelle','Geometrische Zugabe','Prüfung'],[
    ['Deckel-Frontfuge und seitliche Führungen','0,35 Abstand; keine Presspassung','Deckel soll ohne Vorspannen abheben.'],
    ['M3-Durchgang','Ø3,4; Bügelschlitz 3,6 × 8','Bohrung nicht gewaltsam freischrauben.'],
    ['M3-Muttertasche','SW5,9; Höhe2,7 für SW5,5 / Höhe2,4','Coupon mit SW5,7 / 5,9 / 6,1.'],
    ['M3 in PETG','Ø2,6 Pilot, gerolltes Metallgewinde schneidet/formt Kunststoff','Coupon Ø2,45 / 2,55 / 2,65 / 2,75.'],
    ['M2,5 in PETG','Ø2,15 Pilot; max. Ø4,5 Kopf','Nicht maschinell anziehen.'],
    ['LCD-Bezel','Tasche jeweils 1,2 größer als Referenz-Bezel','0,6 seitlich, keine geklemmte Metallfassung.'],
    ['LCD-Fenster','+0,8 Breite / +1,8 Höhe zur Sichtfläche','Buchstaben dürfen nicht verdeckt werden.'],
    ['Joystick','Knopf und Gehäuse separat; Referenzweg 22° + 1 mm Tastweg','Funktionscoupon mit echtem Modul.'],
    ['TB-Bügel','0,6 Luft über der Referenzhülle; weicher 1-mm-Schaum wird komprimiert','Kein starres Klemmen auf Kühlrippen.'],
    ['Lochraster-Kantenhalter','0,2 vertikale Luft; vordere Überdeckung 0,6','Hinten lösen, 1 mm nach hinten schieben.']])+'''
Die Werte sind Konstruktionszugaben, keine gemessene Druckerfähigkeit. XY-Fluss und Elefantenfuß beeinflussen kleine Löcher; vor großen Teilen die Coupons mit dem gleichen Material drucken. Das gesamte Gehäuse nicht skalieren, um eine einzelne Bohrung zu korrigieren.
'''
    docs['measurement_checklist.md']='''# Messliste vor dem ersten vollständigen Druck

**Noch keine Druckfreigabe für unvermessenes Fremdmodul.** Mit Messschieber und Lineal am eigenen Aufbau prüfen. Eine Artikelbezeichnung wie „TB6600“, „1602“ oder „KY-023“ legt das Bohrbild nicht eindeutig fest. Alle Werte unten sind Defaultwerte des Modells; nur die ausdrücklich belegten Uno-Koordinaten und A4988-Rasterdaten sind verifizierte Herstellergeometrie.

'''+table(['Teil / Maß','Modellwert','Eigener Wert / Konsequenz'],[
    ['Uno PCB, vier Löcher','68,58 × 53,34; siehe dimensions.md','____ / Clone-Umriss und Metallbuchsen prüfen.'],
    ['Uno USB-Anschlusskante, Z-Höhe','u −6,34; 10,8 über PCB','____ / Gehäuseöffnung und echten USB-Stecker mit Coupon prüfen.'],
    ['Uno DC-Buchse und Stecker','11 hoch; rückseitiger Ø12-Steckerraum','____ / Besonders Kopf neben der Buchse prüfen.'],
    ['TB vollständige Hülle inkl. Klemmen und Laschen','96 × 71 × 37','____ / Alles außerhalb erfordert neue Parameter und erneute Prüfung.'],
    ['TB Körper ohne Klemmen','96 × 57; Unterseite gerippt','____ / Vier Auflagen müssen tatsächlich die Metallunterseite tragen.'],
    ['TB flache obere Kontaktstellen für Bügel','X130 und X214; Y111…131','____ / 8 × 20 große Pads müssen auf geschlossenem Deckel liegen, keine Klemmen/DIP blockieren.'],
    ['TB Klemmenschrauben und Kabeleintritt','Y157; Leitungshöhe Z38 eingebaut','____ / Toolschlitz und Heckfenster verschieben, falls abweichend.'],
    ['TB originale Befestigungslöcher','nicht verwendet','____ / Nur protokollieren; keine erfundenen Lochkoordinaten im CAD.'],
    ['LCD PCB / Lochabstände / Ø','80 × 36 / 75 × 31 / Referenz Ø2,8','____ / M2,5 muss ohne Kraft durch reale Löcher passen.'],
    ['LCD Bezel, Sichtfenster, Höhe über PCB','71,2 × 25,2; Sicht66 × 16; 8,6 Höhe','____ / Andere Fassungen ändern Tasche UND Montageabstand.'],
    ['LCD Backpack inkl. Jumper, Pot und Kabelstecker','42 × 19; Rückreserve bis n −32,5','____ / Alles inkl. eingesteckter Leitung messen.'],
    ['Joystick PCB / vier Lochkoordinaten','26 × 34; ±10 / ±13 relativ zur Mitte','____ / NICHT vom Modell auf den eigenen KY-023 schließen.'],
    ['Joystick Loch-Ø / Knopfmittelpunktversatz','Referenz3,3 / [0,0]','____ / Bei Ø4-Löchern passende Scheiben, Geometrie neu prüfen.'],
    ['Joystick Mechanik, Kragen und voller Knopfweg','Mechanikhülle18 × 20 × 14; 22°; 1 Tastweg','____ / Ohne Kraft alle Richtungen drücken; mindestens 0,5 reale Luft anstreben.'],
    ['Joystick Aufbauhöhe und Form der Kappenunterseite','Modell33,6 PCB-Unterseite bis Knopfspitze','____ / Quelle nennt eine 32-mm-Klasse; Varianten unterscheiden sich. Z-Abstand per Distanzring und Coupon einstellen.'],
    ['A4988 Pinraster / Reihenabstand','2,54 / 12,70; Modul15,24 × 20,32','____ / 16-poligen Carrier, nicht größeren 1183-Reglercarrier verwenden.'],
    ['A4988 Pot, IC, Kühlkörper, Steckrichtung','Pot X95/Y128 im Referenzmodell','____ / Aufdruck und Datenblatt, nicht Pot-Farbe oder Platinenfarbe entscheiden.'],
    ['Lochraster und Klemmen','40 × 60 ×1,6; 6 × 5,08; Tiefe8 / Höhe10','____ / Klemme ≤30,48 breit; freie 3,5-mm-Kanten für Haltefinger.'],
    ['Kondensator und bestückte Gesamthöhe','100µF ≥50V bei geeigneter niedriger VMOT; Ø≤10 / H≤16','____ / Nennspannung passend zur realen Versorgung, Kapazität lokal.']])+'''
1. Zuerst LCD- und Joystick-Coupons sowie Mutter-/Pilot-Coupon drucken. Die drei Muttertaschen sind von links nach rechts SW5,7 /5,9 /6,1 und öffnen seitlich zur hinteren langen Kante. Den Pilotcoupon mit M3 ×8 prüfen, längere Schrauben nicht bis zum Kopf hineinzwingen.
2. Am Joystick-Coupon alle vier Distanzringe einsetzen, Knopf gegebenenfalls vor Einsetzen abziehen und danach wieder aufsetzen. Voll auslenken und gleichzeitig drücken. Reale Kappenform ist entscheidend.
3. USB/DC-Coupon mit den tatsächlich verwendeten Kabeln prüfen; nicht nur leere Buchsen vergleichen.
4. LCD über das Fenster halten; Lochlage, Ränder und Lesbarkeit prüfen. Der flache LCD-Coupon prüft XY, nicht die Backpack-Tiefe.
5. Bei Abweichungen `default.json` ändern und alles neu generieren. Kein vollständiger Druck mit ungeklärten Pflichtmaßen.
'''
    docs['bill_of_materials.md']='''# Stückliste

## Vorgegebene Elektronik

'''+table(['Anzahl','Teil','Hinweis'],[[1,'Arduino Uno R3','Originaler TH-Formfaktor, kein Shield'],[1,'TB6600-Modul','96 × 71 × 37-Referenzklasse; vorab messen'],[1,'A4988-Carrier','16-polige 15,24 ×20,32-Klasse'],[1,'XY-Joystick mit integriertem Taster','26 ×34-Referenz-PCB; tatsächliches Bohrbild messen'],[1,'1602 LCD mit I²C-Backpack','80 ×36-Referenz-PCB']])+'''
## Erforderliche Schrauben und Muttern

Schwarz beschichteter Stahl oder normaler Stahl sind geeignet. Schraubenlängen sind Nennlängen, bei Senkköpfen einschließlich Kopf. Keine zusätzlichen großen Scheiben auf die Senkungen legen.

'''+table(['Anzahl','Spezifikation','Verwendung'],[
    [6,'M3 ×12, 90° Innensechskant-Senkkopf, DIN7991/ISO10642; Kopf ≤Ø6,4','4 Front von unten, 2 Deckel von oben'],
    [4,'M3 ×8, gleicher 90°-Senkkopf','TB-Bügelfüße; Köpfe müssen bündig sitzen'],
    [6,'M3 ×10, Zylinderkopf ISO4762/DIN912, Kopf ≤Ø5,5','4 Joystick, 2 A4988-Kantenclips'],
    [7,'M2,5 ×8, Zylinderkopf ISO4762/DIN912, Kopf ≤Ø4,5','4 LCD, 3 Uno; kleinere Köpfe wegen Anschlussnähe'],
    [6,'M3-Sechskantmutter DIN934/ISO4032, SW5,5, Höhe2,4','4 Frontstützen, 2 Deckeltürme'],
    [6,'M3-Scheibe ISO7089/DIN125, Ø3,2 / Ø6 / ca.0,5','4 unter Joystick-Schraubenköpfen, 2 unter A4988-Clipköpfen'],
    [4,'M2,5-Scheibe, Ø2,7 / Ø5 / ca.0,5','LCD; keine Scheiben an Uno-DC-Montage'],
    [4,'2-mm-Distanzring, Ø6 / LochØ3,4','Druckteile joystick_spacer_1…4; alternativ passende M3-Distanzscheiben oder je 4 ×0,5-mm-Scheiben']])+'''
Die Distanzringe werden standardmäßig gedruckt; dafür keine Metallteile zusätzlich kaufen. Als Einkaufsmengen sind kleine Schraubenpackungen mit Reserve sinnvoll. Wärmeinserts werden nicht benötigt. Für wiederholte Wartung sind die sechs Gehäusemuttern vorgesehen; die selten gelösten PCB-/Bügelschrauben greifen in PETG-Piloten.

## Erforderliches Montage- und Verdrahtungsmaterial

'''+table(['Menge','Spezifikation','Zweck'],[
    [1,'Unbestückte Lochrasterplatine 40 ×60 ×1,6, Raster2,54, frei wählbare Montagebohrungen','Mechanischer Träger für den gesockelten A4988'],
    [2,'Buchsenleiste 1×8, Raster2,54, Körper-/Aufbauhöhe8,5 oder CAD anpassen','Treiber austauschbar; NICHT verdreht einstecken'],
    [1,'Leiterplatten-Schraubklemme 6-polig, Raster5,08, Breite≤30,48, Tiefe≤8, Höhe≤10; alternativ 3 gekoppelte 2-polige','Getrennte A4988-Versorgung und vier Motoradern; kein Bulkhead nötig'],
    [1,'Elektrolytkondensator100µF, Spannungsfestigkeit passend zur VMOT, bevorzugt50V bei 12/24V-Aufbau, Ø≤10 × H≤16','Direkt bei VMOT/GND; nicht als entferntes Kabel-Ende montieren'],
    [1,'Passivkühlkörper für A4988, Hülle≤10 ×10 ×10 plus vorgesehener Kontaktlage','Elektrisch isoliert befestigen, keine benachbarten Pads überbrücken'],
    [2,'Silikonschaumstreifen 8 ×20 ×1, weich, temperaturgeeignet, selbstklebend oder sparsam fixiert','TB-Bügelpolster; etwa0,6-mm-komprimierte Höhe im Modell'],
    [4,'Selbstklebende Gummifüße Ø14 ×4','Lufteintritt unter dem Boden; alternativ 4 TPU-Füße plus geeignetes Klebeband'],
    ['ca.3m','Flexible isolierte Logiklitze 0,14…0,25mm², mehrere Farben','Frontkabel, Steuerleitungen, kurze lokale Masse-/5V-Verteilung'],
    ['ca.1m intern + externe Testleitungen','Motor-/Versorgungslitze ca.0,5…1,0mm², nach Strom/Klemmen auswählen','Keine Dupont-Leitung als Motorleistungsleitung verwenden'],
    ['ca.30 Kontaktpositionen','Passende Buchsen-/Stiftkontakte oder vorkonfektionierte Jumper für Logik','Steckerlängen müssen in die reservierte Hülle passen'],
    ['10','Kabelbinder2,5 ×100','Anker und Zugentlastung; nicht auf SMD-Bauteile spannen'],
    ['ca.0,3m','Schrumpfschlauch / flexible Kantenschutz-Isolation für Hecköffnungen','Lötstellen und Kabel gegen Scheuern schützen']])+'''
Die Mengen der Litzen sind Beschaffungsrichtwerte, keine Zuschnittliste. Auf dem Lochraster die Klemmen stabil verlöten; Strompfade mit ausreichend kräftiger Litze oder Kupferdraht verstärken, nicht über dünne beliebige Lötbrücken führen. Ein externer Gleichspannungs-Testaufbau und USB-Kabel sind Betriebsvoraussetzungen; es wird kein Netzteil im Gehäuse eingebaut.

## Druckteile und optionale Teile

'''+table(['Datei in PRINT','Anzahl','Ausrichtung bereits enthalten'],[
    ['main_chassis.stl',1,'Boden auf Druckbett'],['front_panel.stl',1,'Sichtfläche auf Druckbett; Stützen wachsen nach oben'],['top_cover.stl',1,'Außenfläche auf Druckbett'],['tb_clamp_left.stl / tb_clamp_right.stl','je1','Bügeloberseite auf Bett, Beine nach oben'],['a4988_edge_clip_1.stl / a4988_edge_clip_2.stl','je1','Große ebene Unterseite auf Bett'],['joystick_spacer_1…4.stl','je1','Ringe flach; gleiche Geometrie an vier Einbaupositionen'],['optional_parts/tpu_foot_print_4.stl','4 optional','TPU, mit Klebung; ersetzt gekaufte Füße']])+'''
Werkzeuge: Innensechskant2,0 und2,5mm, schmaler kleiner Schlitzschraubendreher für Klemmen, Messschieber, Zange, Lötkolben und Multimeter. Die geometrisch geprüften Zugangskorridore nehmen einen maximal Ø3-mm-Werkzeugschaft an. Ein dicker Schraubendreher-Bithalter passt nicht an die vorderen Bügelschrauben. Gewinde vorsichtig per Hand bilden; keine Akkuschrauber verwenden.
'''
    docs['print_settings.md']='''# Druckvorbereitung · Bambu Lab P2S

Alle STLs sind Millimeterdateien, geschlossene positiv orientierte Dreiecksnetze und bereits für den Druck ausgerichtet. STEP-Teile liegen dagegen in Einbaulage vor. STL und STEP daher nicht unbemerkt unterschiedlich skalieren. Maximales Baumaß des größten Teils: 230 ×176; mit 5-mm-Brim bleibt es innerhalb256 ×256.

'''+table(['Einstellung','Praktischer Startwert'],[
    ['Material','PETG, trocken; mattes Dunkelgrau/Schwarz. PLA nur für Passproben oder nach Temperaturprüfung.'],
    ['Düse / Schicht','0,4mm /0,20mm; für die kleinen Ringe bei Bedarf0,16mm'],
    ['Perimeter / Top-Bottom','4 Wände; 5 obere und5 untere Lagen; Bügel/Clips/Ringe5 Wände'],
    ['Infill','15…20% Gyroid für Schalen; 35…50% bei Bügeln; kleine Clips/Ringe praktisch massiv'],
    ['Stützen','Im Entwurf nicht erforderlich; Brückentest vor den großen Teilen.'],
    ['Brim','5mm bei Bodenschale/Front nach Haftung; kleine Bügel/Ringe ggf.3mm'],
    ['Oberfläche','Sichtseiten von Front/Deckel auf gleiche strukturierte Platte legen. Keine Ironing-Pflicht.'],
    ['Temperaturen / Geschwindigkeit','Das Profil des konkreten PETG verwenden, nicht unbekannte Temperaturen übernehmen. Außenwände für saubere Radien moderat drucken.'],
    ['Elefantenfuß','Mit Coupon einstellen; als Ausgangsversuch0,10…0,15mm Kompensation, nicht als geprüfter P2S-Wert.']])+'''
## Brücken und Überhänge

Die längste geplante horizontale Brücke am aufrechten Chassis ist das USB-Dach mit etwa12mm. Weitere Heckfenster haben gefaste obere Ecken; Muttertaschen überbrücken ungefähr6mm. Die Wandlüftung endet in45°-Dächern. Frontstützen stehen im Druck etwa18° gegen die Vertikale und benötigen keine separate Stütze. Kleine Piloten und Kabelbinderanker haben kurze Brücken. Die glatte Unterseite enthält keine großen überbrückten Fußtaschen.

Wenn der PETG-Brückentest am eigenen Material misslingt: zuerst Fluss/Kühlung und Brückengeschwindigkeit einstellen. Nur falls nötig lokale manuelle Stützen im USB-Dach setzen; keine flächigen Stützen an Sichtseiten. Diese optionale Maßnahme ist keine getestete Slicereinstellung.

## Reihenfolge

1. Mutter- und Pilotcoupon drucken, reale Muttern/Schrauben prüfen.
2. LCD-, Joystick- und Portcoupon drucken, echte Module und Kabel anlegen.
3. Vier Distanzringe und kleine Halter drucken; die Bügel am TB6600 prüfen.
4. Front und Schale erst nach Maßprüfung drucken; Deckel abschließend.

Es wurde kein Slicer ausgeführt, keine Platte im Bambu-Profil getestet und keine3MF-Datei vorbereitet. Druckzeit und Filamentverbrauch sind daher nicht als Slicerwerte angegeben. Die technischen Volumina in validation_results.json sind massive CAD-Volumina; Infill und reale Extrusionsbreiten verändern die Druckmasse. PLA nicht als Freigabe für hohe Treiberströme betrachten.
'''
    docs['mechanical_assembly.md']='''# Mechanische Montage

## 1 · Teile und Gewinde vorbereiten

Alle Teile abkühlen lassen und kleine Fäden entfernen. Maße gegen die Messliste prüfen. PETG-Piloten zunächst mit der später verwendeten Schraube und sehr wenig Druck von Hand formen. Zur Spanlösung gegebenenfalls kurz zurückdrehen. Ein deutliches Aufspreizen, Weißbruch oder ein abhebender Boss bedeutet: stoppen und Bohrungsparameter am Coupon korrigieren. Nicht mit einer längeren Schraube durch die Außenhaut stechen.

Vier M3-Muttern seitlich in die vier Frontstützen einsetzen. Zwei weitere M3-Muttern von der Innenseite in die hohen hinteren Schalentürme schieben. Einlegen, nicht einkleben und nicht mit Gewalt einpressen. Ein schmales Stück Klebeband darf eine lose Mutter beim Zusammenbau sichern, aber keine Tasche füllen.

## 2 · Front auf dem Tisch bestücken

LCD von hinten in die große Bezeltasche legen. Alle vier PCB-Ecken müssen auf den runden Supports liegen; die Metallfassung darf nicht gegen die Taschenkante verspannt werden. Mit4 × M2,5 ×8 und4 kleinen M2,5-Scheiben von hinten befestigen. Nur bis zum flächigen Sitz anziehen. Die unvermessene Backpack-Variante einschließlich Stecker von Hand gegen die reservierte Hülle prüfen.

Joystickknopf gegebenenfalls gerade abziehen. Vier 2-mm-Distanzringe zwischen Supports und PCB setzen. Modul von hinten ausrichten; den Knopf außen wieder aufsetzen. Mit4 × M3 ×10 und4 M3-Scheiben befestigen. Voll in alle Richtungen auslenken und jeweils drücken. Nichts darf am Rand streifen. Bei kürzerem Knopf zunächst am Coupon dünnere Distanzringe bzw. passende Scheiben prüfen; bei mehr als2mm Änderung die Parametrierung und Kollisionsprüfung erneut ausführen. Nicht einfach festziehen, um die Knopfhöhe zu verändern.

## 3 · Uno einsetzen

Der Uno liegt links, Buchsen nach hinten. Drei Löcher auf die Supports setzen, das vierte auf den kurzen Locator.3 × M2,5 ×8 einsetzen. An der DC-Buchse keine große Unterlegscheibe hinzufügen; Zylinderkopf maximalØ4,5. Einen echten USB- und einen gegebenenfalls benötigten DC-Stecker einstecken, Bewegungsfreiheit prüfen, danach für die restliche Montage wieder abziehen.

## 4 · A4988-Träger aufbauen

Auf die40 ×60-Lochrasterplatine zwei1×8-Buchsenleisten im2,54-Raster mit12,70 Reihenmittenabstand löten. Beide Reihen parallel ausrichten. Der Carrier ist eine einfache selbst verdrahtete Montageplatine, kein zusätzliches Steuergerät. Die 6-polige5,08-Klemme sitzt hinten, der Kondensator dicht neben VMOT/GND. Bestückungskoordinaten und Pinliste stehen in wiring_access.md. Die Treiberorientierung anhand seiner Beschriftung prüfen. Der Kühlkörper und die Potentiometerschraube dürfen sich nicht berühren.

Vor Einsetzen des A4988 mit dem Multimeter alle Anschlüsse und Kurzschlussfreiheit prüfen. RESET und SLEEP wie in der Firmware vorgesehen an VDD anbinden. Kondensatorpolarität kontrollieren. Erst dann den Carrier in die Buchsenleisten stecken.

Die vordere nackte PCB-Kante unter die beiden kurzen festen Überdeckungen schieben, die Platine auf vier Supports ablegen. Die beiden rückseitigen Kantenclips mit2 × M3 ×10 und2 M3-Scheiben montieren. Nur die schmalen Finger reichen über die freien PCB-Ecken. Das Halten erfolgt formschlüssig; nicht den Schraubklemmenkörper oder Lötpunkte niederdrücken.

## 5 · TB6600 einsetzen

Das reale Modul muss der freigegebenen Hüllklasse entsprechen. Mit gerippter Metallseite unten auf die vier kleinen Auflagen setzen, Klemmen nach hinten. DIP-Schalter dürfen nicht unter einem Bügel verschwinden. Das Modul nicht auf Kabel oder hervorstehende Lötteile legen.

Je einen8 ×20 ×1-mm-Silikonschaumstreifen unter die Querstege der beiden Bügel kleben, mittig über einer geschlossenen Moduldeckelfläche. Linken und rechten Bügel einsetzen.4 × M3 ×8-Senkschrauben in die Langlöcher setzen und gleichmäßig vorsichtig anziehen. Die Köpfe müssen bündig zur Fußoberseite liegen; so bleiben sie unter den Kühlrippen frei. Verschiebung in X ist begrenzt möglich. Der Schaum soll leicht komprimiert sein. Metallgehäuse nicht verformen und PETG nicht unter große Dauer-Vorspannung setzen.

## 6 · Leitungen ordnen

Logikleitungen am vorderen Bereich der Treiber entlang zu den mittigen Bodenankern führen. LCD und Joystick jeweils mit etwa60…80mm Reserve für das Anheben der Front anbinden. Die rückseitigen Motor- und DC-Adern kurz und direkt zu den zugehörigen Klemmenfenstern führen. Keine Motorspannung auf die Uno-5V-Verteilung legen. Kanten mit geeigneter flexibler Isolation schützen; Kabelbinder durch die vorgesehenen Lochpaare unter den Heckfenstern führen und um den isolierten Kabelmantel legen. Kein Binder darf einzelne Litzen quetschen oder das Modulgehäuse als elektrischen Anschluss belasten.

Unter dem Deckel bleibt ein freier Rand von mindestens5mm für Leitungen. Kabel nicht auf die Deckelauflage oder unter die Führungszungen legen. Die Lüftungsschlitze frei lassen. Diese Zugentlastung wurde nicht mit einer genormten Zugkraft getestet; bei fühlbarer Bewegung am Terminal nicht betreiben, sondern Kabelbefestigung korrigieren.

## 7 · Front und Deckel schließen

Bestückte Front senkrecht absenken, Kabelbogen im vorderen freien Raum belassen und Stützen auf die vier Bodenlöcher ausrichten. Gehäuse sicher abstützen und4 × M3 ×12-Senkschrauben von unten in die gefangenen Muttern eindrehen. Die Stützen, nicht die LCD-Fassung, tragen die Front. Die vier4-mm-Gummifüße auf der Unterseite bei X21/209 und Y20/156 ankleben.

Nach Kontrolle aller Leitungen den Deckel mit seinen vier Führungszungen innen an den Seitenwänden aufsetzen. Er muss ohne Kraft plan aufliegen.2 × M3 ×12 oben in die hinteren Muttern schrauben. Der Deckel braucht keinen Ausbau von LCD oder Joystick. Klemmen bleiben durch Heckfenster und obere Werkzeugschlitze erreichbar; für Umverdrahtung trotzdem vollständig stromlos schalten.
'''
    docs['wiring_access.md']='''# Elektrische Zugänge und Verdrahtung

## Drei getrennte Versorgungswege

USB bzw. der vorgesehene DC-Eingang versorgt den Uno. Der TB6600 hat seinen eigenen DC-Leistungseingang entsprechend dem Aufdruck des realen Moduls. Der A4988 bekommt VMOT separat von seiner5V-Logikversorgung. Die unterschiedlichen Motoreingänge sind mechanisch getrennt zugänglich. Es gibt keine automatische gemeinsame Spannungsanpassung und keine interne Netzspannung.

Für den Referenz-A4988 nennt Pololu8…35V an VMOT und3…5,5V an VDD. Das ist keine Freigabe für einen unbekannten Klon oder lange ungedämpfte Leitungen. Der lokale Elektrolytkondensator ist erforderlich; dieses Projekt sieht100µF vor. Bei anderer Versorgung muss auch seine Spannungsfestigkeit geprüft werden.

## Heck von außen gesehen

Von hinten betrachtet liegt der TB6600-Klemmenbereich links, die sechspolige A4988-Klemme mittig und die Uno-USB-/DC-Öffnung rechts. Die Positionen im CAD sind X-Koordinaten aus der Vorderansicht; bei Betrachtung von hinten ist die sichtbare Links-Rechts-Reihenfolge entsprechend gespiegelt. Versorgungskabel direkt mit TB bzw. A4988 und Polarität beschriften, bevor das Gerät eingeschaltet wird.

Von oben führen8mm breite Werkzeugfenster zu den Klemmschrauben. EinØ8-Loch über dem Referenz-Pot des A4988 dient ausschließlich dem spannungsfreien mechanischen Zugang. Für eine Vref-Messung vorzugsweise Deckel abnehmen und mit isoliertem Werkzeug arbeiten. Die Durchbrüche machen das Gehäuse weder staubdicht noch flüssigkeitsgeschützt.

## A4988-Träger: festgelegte Platzierung

'''+table(['Teil','Koordinaten im Gehäuse'],[
    ['Lochraster','X75…115 / Y107…167 / PCB-Unterseite Z10'],
    ['1×8-Sockel-Reihenmitten','X88,65 und X101,35; Pins in Y bei127,11 /129,65 /132,19 /134,73 /137,27 /139,81 /142,35 /144,89'],
    ['Treiber-PCB','Mitte X95 /Y136; PCB-Unterseite Z20,1'],
    ['6-polige Klemme','X79,76…110,24 /Y158…166; Schraubenlinie Y162'],
    ['Kondensator','Mitte X109 /Y143; maximalØ10 ×16'],
    ['Kühlkörper','10 ×10 ×10; Hülle X90…100 /Y134…144'],
    ['Pot-Referenz und Zugang','X95 /Y128; reale Klonposition zuerst kontrollieren']])+'''
Klemmenreihenfolge als eigene Beschriftung festlegen: VMOT+, GND,1A,1B,2A,2B. Die rote Platine in der Vorschau ist nur ein Referenzkörper. Verbindungsnetze nach den tatsächlichen A4988-Pinbezeichnungen löten; eine um180° gedrehte Platine kann zerstört werden. Keine Leiterbahnen oder elektrischen Netze sind im STEP elektrisch geprüft. Löten, Durchgangsprüfung, Polaritätsprüfung und Stromlimit-Einstellung bleiben notwendig.

## Verbindung zur vorhandenen Uno-Firmware

Die folgende Zuordnung wurde aus dem bereitgestellten Firmware-README vom22.10.2026 übernommen. Der Sketch wird durch dieses Gehäuseprojekt nicht verändert.

'''+table(['Uno','Ziel'],[
    ['A0 / A1 / D2','Joystick VRx / VRy / SW'],['A4 / A5','LCD SDA / SCL'],['5V / GND','LCD und Joystick; A4988 VDD und Logik-GND'],['D3 / D4','TB6600 PUL+ / DIR+'],['GND','TB6600 PUL− und DIR− im vorgesehenen Common-Cathode-Aufbau'],['D5','TB6600 ENA+ nur bei ausdrücklich geprüfter optionaler Enable-Verdrahtung; im Standard beide ENA offen'],['D6 / D7 / D8','A4988 STEP / DIR / ENABLE'],['D9 / D10 / D11','A4988 MS1 / MS2 / MS3'],['VDD lokal','A4988 RESET und SLEEP wie vorgesehen HIGH'],['Separates DC+ / DC−','A4988 VMOT / Motor-GND; Logik- und Motor-GND nach Carrier-Schaltbild verbinden']])+'''
TB6600-DIP-Schalter bleiben echte Hardware-Einstellungen. Der Firmware-Menüwert muss dazu passen. Nur der STEP-Ausgang wird softwareseitig ausgewählt; ein abgewählter Treiber ist dadurch nicht automatisch spannungsfrei. Die Leistungsausgänge beider Treiber niemals gleichzeitig auf denselben Motor legen. Beim Wechsel vollständig abschalten und anschließend umstecken. Strombegrenzungen vor der ersten Motorbewegung einstellen, nicht aus einer willkürlichen Vref-Formel für einen anderen Klon übernehmen.
'''
    docs['thermal_and_maintenance.md']=f'''# Temperatur, Betrieb und Wartung

## Passive Kühlung

Der TB6600 hat7mm freien Abstand zwischen Kühlrippenspitzen und Boden. Schlitze im Boden, in der rechten Wand und im Deckel schaffen mögliche Konvektionswege. Vier4mm hohe Füße sind funktional erforderlich. Der Treiberdeckel liegt {r['driver_clearances_mm']['TB_top_to_lid']:.2f}mm unter der ebenen Deckelunterseite; unter einer Versteifungsrippe verbleiben {r['driver_clearances_mm']['TB_top_to_lid_rib']:.2f}mm. Die Bügel liegen noch höher, sind aber ebenfalls kollisionsfrei. Der A4988-Kühlkörper hat zur ebenen Deckelunterseite {r['driver_clearances_mm']['A4988_sink_to_lid']:.2f}mm Reserve.

Diese Abstände sind Geometrie, keine nachgewiesene Kühlleistung. Es gibt keine gemessene Verlustleistung, keine Strömungssimulation und keine Dauerstromfreigabe für das geschlossene Gehäuse. Nicht aus einem beworbenen4A- oder2A-Modulwert auf die zulässige Dauerlast im gedruckten Gehäuse schließen.

Erstbetrieb bei niedrigem, zum Motor passendem Stromlimit, ohne mechanische Last. Gehäuse geschlossen prüfen und Temperaturen an beiden Treibern sowie an den PETG-Kontaktstellen über mehrere Zeitabstände bis zur erkennbaren Stabilisierung beobachten. Als konservative Inbetriebnahmegrenze dieses Projekts: bei50°C an einem PETG-Auflagepunkt bzw.40°C an einem PLA-Auflagepunkt abbrechen und Strom/Betriebsdauer verringern. Das sind gewählte Prüfgrenzen, keine garantierten Material- oder Bauteilgrenzwerte. Modul- und Materialherstellergrenzen gelten zusätzlich. Im Zweifel nicht unbeaufsichtigt betreiben.

## Elektrischer Umgang

Nur externe geeignete DC-Testversorgungen verwenden. Alle Umbauarbeiten vollständig stromlos ausführen, Energiespeicher entladen lassen. Motorstecker niemals bei eingeschaltetem Treiber lösen. Ein Joystick-Tastendruck ist eine Softwarefunktion und kein geprüfter Not-Halt. Unter Spannung stehende Klemmen durch die Wartungsöffnungen nicht berühren. Keine Flüssigkeiten oder losen Metallteile auf das Gerät legen.

## Ausbauen und warten

1. Alles abschalten, USB und Motorleitungen trennen. Zwei Deckelschrauben lösen und Deckel senkrecht nach oben abheben.
2. A4988-Carrier allein: gerade aus den beiden Buchsenleisten ziehen, Lochraster und andere Module bleiben eingebaut. Vollständiger Lochrasterträger: zwei hintere Clips abnehmen, Platine1mm nach hinten aus den vorderen Überdeckungen schieben, dann anheben.
3. TB6600: vier bündige Bügelschrauben lösen, beide Bügel abheben, Modul nach oben herausnehmen. Der vordere Schraubenkorridor liegt bewusst bei Y92 zwischen Front und Modul; dünnen2mm-Innensechskantschaft verwenden.
4. Uno: drei Schrauben lösen, Platine etwa1,1mm anheben, um den Locator zu räumen;8mm nach vorne schieben, damit USB-B aus der Rückwand frei wird; dann nach oben entnehmen. Nicht senkrecht gegen das USB-Dach zerren.
5. LCD oder Joystick: vier untere Frontschrauben lösen, Front wenige Zentimeter anheben, die beiden Front-Steckverbinder trennen. Jeweiliges Modul an seinen vier Schrauben lösen; das andere darf an der Front bleiben. Die hinteren Module müssen nicht ausgebaut werden.
6. Bei ausgeleiertem Kunststoffpilot nicht immer längere Schrauben einsetzen. Betroffenes kleines Teil neu drucken oder den vorgesehenen Boss parametrisch für eine andere Befestigung neu auslegen. Mutterbefestigungen des Gehäuses regulär wiederverwenden.

Kabelbinder auf Scheuerstellen prüfen und weiche TB-Bügelpolster auf bleibende Setzung kontrollieren. Ein entnehmbarer Deckel ist keine Abdichtung. Motor- und Versorgungskabel immer nach dem tatsächlichen Klemmenaufdruck verfolgen.
'''
    solidrows=[]
    for name,d in r['solids'].items():
        mesh=r['meshes'][name];solidrows.append([name,' × '.join(f'{v:.2f}' for v in mesh['bounds_mm']),f'{d["volume_cm3"]:.3f}','gültig / geschlossen'])
    docs['validation_report.md']=f'''# Validierungsbericht · R1

**Status: digitale Referenzgeometrie bestanden. Reale Passung noch nicht freigegeben.**

Geprüft mit CadQuery{r['cadquery_version']} / OpenCascade-B-rep. Basis: default.json, nicht vermessene Originalteile des Nutzers. Die Prüfungen werden von generate.py erneut ausgeführt. Maschinenlesbare Rohdaten: validation_results.json. Alle nachfolgenden Angaben betreffen die exportierten Referenzkörper.

'''+table(['Prüfung','Ergebnis'],[
    ['B-rep-Körper',f'{len(r["solids"])} druckbare Bauteile, jeder genau1 gültiger Solid'],
    ['Schnittvolumen',str(r['collision_pairs_checked'])+'; keine Überschneidung oberhalb0,005mm³'],
    ['Schraubenköpfe / Scheiben / Muttern','Nominale Körper zusätzlich geprüft; keine unzulässige Überschneidung. Schäfte überlappen Piloten/Gewindekern absichtlich.'],
    ['Joystick',f'{r["joystick_sweep"]["configurations"]} Abtaststellungen;22° maximal,1mm Tastweg; min. Modellabstand{r["joystick_sweep"]["minimum_model_gap_mm"]:.3f}mm'],
    ['Deckel','7 Hubstellungen bis60mm; Front und Module bleiben eingebaut.'],
    ['Komponentenausbau','Uno6, A4988-Träger5 und TB6600 4 diskrete Ausbaupositionen ohne Kollision nach Lösen der dokumentierten Halter.'],
    ['Werkzeug-/Kabelzugänge',f'{len(r["access_checks"])} korridorbezogene Prüfungen; Ø3-mm-Werkzeugschaft bzw. Kabelhülle, reale Stecker zusätzlich vermessen.'],
    ['STL-Netze',f'{len(r["meshes"])} Netze inkl. Coupons und optionalem Fuß: keine offenen/nichtmanifold Kanten, konsistente Orientierung, positives Volumen.'],
    ['Bauvolumen','Alle Teile ≤256mm je Achse; größte XY-Ausdehnung230 ×176.'],
    ['STEP-Einzelteile','Alle reimportiert; Volumenabweichung <10⁻⁶ relativ.'],
    ['STEP-Baugruppe',f'Reimport gültig;{r["main_assembly_roundtrip"]["solids"]} Solids; Volumenabweichung{r["main_assembly_roundtrip"]["volume_relative_error"]:.2e}.'],
    ['Exportvergleich','Alle Haupt-STL-Volumina <0,5% Abweichung gegenüber dem B-rep. Konkrete Fehlerwerte in JSON.']])+'''
## Druckkörper

'''+table(['Teil','Druck-Boundingbox mm','Massivvolumen cm³','Ergebnis'],solidrows)+'''
## Aussagegrenzen und verbleibende Risiken

Die A4988-/TB-/LCD-/Joystickmodelle sind bewusst vereinfachte Referenz- und Freiraumkörper. Elektronik-intern dürfen einzelne reservierte Hüllen überlappen; geprüft werden die Gehäuseschnittstellen und die verschiedenen Baugruppen gegeneinander. Die tatsächliche Kappenunterseite, Potposition, TB-Laschen, Steckerkörper und LCD-Backpack-Variante können abweichen. Das sind offene Passungsrisiken und werden nicht durch ein grünes CAD-Ergebnis aufgehoben.

Die Joystick- und Ausbauprüfungen sind diskrete geometrische Abtastungen, keine kontinuierliche zertifizierte Bewegungsraumprüfung. Kabelkorridore ersetzen keine Simulation verformbarer Kabel, keine Prüfung eines Biegeradius unter Zug und keinen genormten Zugentlastungsversuch. Schraubendrive-Rezess und Gewinde sind im STEP nicht detailliert modelliert. Für die gekaufte Hardware gelten die Kopfgrößen der Stückliste.

Keine physische Montage, kein echter FDM-Druck, keine Slicerplatte, kein Festigkeitsversuch, keine FEM, keine elektrische Durchgangsprüfung und keine thermische Dauerprüfung wurden durchgeführt. Der Generator beweist die Reproduzierbarkeit des digitalen Entwurfs; er beweist nicht, dass beliebige gleich bezeichnete Module passen. Maßliste und Funktions-Coupons sind vor dem großen Druck verbindliche lokale Prüfungen.
'''
    docs['parameters_guide.md']='''# Parametrierung und Reproduktion

Quelle: CAD/editable_source, Parameter: CAD/parameters/default.json. Reine Python-/CadQuery-B-reps, keine Mesh-Importe und kein proprietäres CAD-Projekt nötig. STEP ist in normaler Einbaulage, STL bereits in Drucklage. Die Datumseinheit ist Millimeter.

'''+table(['Gruppe','Wichtige Parameter / Abhängigkeit'],[
    ['enclosure','width, depth, height, front_angle_deg, panel_run, wall, floor, corner_radius, cover_clearance. Bei numerischem height wird front_height daraus abgeleitet; height=null erlaubt front_height als treibendes Maß.'],
    ['fasteners','M3-Clearance/Pilot/Kopf; Mutter-SW/Höhe; M2,5-Pilot. Nicht mit einem globalen Skalierungsfaktor ersetzen.'],
    ['uno','Board-XY-Transformation, PCB-Z, verifizierte vier Lochkoordinaten, USB/DC-Hüllen.'],
    ['lcd','center_x/center_t, PCB und Loch-Offsets, Bezel/Tasche/Fenster, Montage-n, Backpackreserve.'],
    ['joystick','center_x/center_t, hole_offsets, shaft_offset, pcb_front_n, mount_spacer, opening_diameter, Gimbal, Knopfprofil, Pivot, Winkel und Tastweg.'],
    ['tb6600','x/y/bottom_z, length/body_depth/overall_depth/height, fin_*, clamp_x, clamp_foot_screws, terminal_*. mounting_holes ist absichtlich leer.'],
    ['a4988','Lochraster, Sockelhöhe, Modulposition, Reihenraster, Kühlkörper, Kondensator, Pot und Terminal.'],
    ['vents / access','Schlitzbreite/-länge/-raster; konkrete X/Y/Z-Lage der Heck- und Werkzeugöffnungen.']])+'''
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
'''
    docs['sources.md']='''# Technische Quellen und Herkunft

Abgerufen23.10.2026. Die Links dienen dem Herkunftsnachweis; die Bauanleitung selbst benötigt keine Internetverbindung. Es werden keine fremden Zeichnungsseiten oder fremden CAD-Körper als eigene Arbeit ausgegeben. Alle gelieferten Referenzkörper wurden im Python-Quelltext neu aufgebaut.

'''+table(['Quelle','Verwendet / Einschränkung'],[
    ['[Arduino Uno R3, offizielles Datenblatt](https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf)','Überblick und mechanische Zeichnung; für vollständige Koordinaten das Boardfile verwendet.'],
    ['[Arduino UNO-TH_Rev3e.zip, offizielles Eagle-Board](https://content.arduino.cc/assets/UNO-TH_Rev3e.zip)','Exakte Lochkoordinaten, Umriss und XY-Buchsenfootprints. Extrakt samt SHA256 in CAD/component_models/uno_official_interface_extract.json.'],
    ['[Pololu A4988 1182](https://www.pololu.com/product/1182)','Versorgungs-Trennung, LC-Spitzen, lokaler Elektrolytkondensator, thermische Einschränkungen.'],
    ['[Pololu Maßzeichnung 1182](https://www.pololu.com/file/0J1082/a4988-stepper-motor-driver-carrier-dimension-diagram.pdf)','15,2/20,3 gerundet bzw.600/800mil, Raster2,54, Reihenabstand12,70; unbekannte Klone separat prüfen.'],
    ['[Handson MDU1059 TB6600](https://www.handsontec.com/dataspecs/module/TB6600-Motor-Driver.pdf)','S.2 zeigt96 ×71 ×36, inklusive Klemmen; Datenliste nennt96 ×56 ×33. Bewusst größeres96 ×71 ×37-Referenzmaß, nicht als eigener Messwert.'],
    ['[DFRobot DRI0043 Wiki](https://wiki.dfrobot.com/dri0043/)','96 ×71 ×37 als weitere Referenzklasse; [Produktseite](https://www.dfrobot.com/product-1547.html) nennt abweichend96 ×56 ×33. Keine eindeutige Identifikation des eigenen Moduls.'],
    ['[Handson I²C1602](https://www.handsontec.com/dataspecs/module/I2C_1602_LCD.pdf)','80 ×36-PCB-Klasse, keine Freigabe eines bestimmten Backpack.'],
    ['[Newhaven NHD-0216K1Z-FL-YBW](https://newhavendisplay.com/content/specs/NHD-0216K1Z-FL-YBW.pdf)','Referenz-Lochabstand75 ×31 und Bezel71,2 ×25,2. Herstellerlöcher sind dort2,5, nicht pauschalM3. Das eigene I²C-Modul ist NICHT als Newhaven identifiziert.'],
    ['[Handson PS2-Joystick ASS-1056](https://www.handsontec.com/dataspecs/accessory/PS2-Joystick.pdf)','34 ×26 ×32-Variantenklasse; Quelle nennt4 ×M4, liefert keine belastbare Koordinatentabelle. Unser20 ×26-Bohrbild ist deshalb ausdrücklich unbestätigt.'],
    ['[Joy-IT COM-KY023JM](https://www.joy-it.net/en/products/COM-KY023JM)','Weitere Variante mit34 ×39 ×26. Belegt die Unzulässigkeit einer pauschalen KY-023-Passgarantie.'],
    ['Firmware-README22.10.2026, vom Nutzer bereitgestellt','Pinzuordnung und vorhandener Bedienumfang. Keine zusätzlichen Bedienelemente oder Firmwareänderungen.']])+'''
Der Handson-Backpack ist als42 ×19-Reservekörper modelliert. Knopfprofil, Gimbal, Kabelstecker, Bauteilhöhen und TB-Klemmenpositionen sind gekennzeichnete technische Annahmen. Die Dokumentation unterscheidet Herkunftsdaten, gewählte Fertigungstoleranzen und noch offene Messwerte.
'''
    # Write canonical individual text files.
    for name,text in docs.items():(root/'DOCUMENTATION'/name).write_text(text.strip()+'\n',encoding='utf-8')
    (root/'PRINT/print_settings.md').write_text(docs['print_settings.md'].strip()+'\n',encoding='utf-8')
    (root/'CAD/component_models/README.md').write_text('''# Referenzkörper

Die STEP-Dateien enthalten selbst erzeugte vereinfachte B-reps in Einbaulage. Sie sind keine OEM-zertifizierten Produktmodelle. Lochkoordinaten und gesicherte Daten: siehe DOCUMENTATION/dimensions.md und sources.md. Die Datei uno_official_interface_extract.json enthält die Herkunft der Uno-XY-Schnittstellen. Keine fremden Polygonmodelle sind nötig, um die Baugruppe zu regenerieren.
''')
    (root/'README.md').write_text(f'''# Stepper Testbench Enclosure · R1

Vollständiger parametrischer Gehäuseentwurf für Uno R3, TB6600, A4988, XY-Joystick und1602-I²C-LCD. Standardmaß {e['width']:.0f} ×{e['depth']:.0f} ×{H:.2f}mm ohne Füße/Knopf. Die Front ist18° zur Tischfläche geneigt.

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
''',encoding='utf-8')
    chapters=[('overview','Projekt und Aufbau','architecture.md'),('measure','Maßprüfung zuerst','measurement_checklist.md'),('bom','Stückliste','bill_of_materials.md'),('print','Druckvorbereitung','print_settings.md'),('assembly','Montage','mechanical_assembly.md'),('wiring','Verdrahtung und Zugang','wiring_access.md'),('thermal','Betrieb und Wartung','thermal_and_maintenance.md'),('dimensions','Maße und Toleranzen','dimensions.md'),('validation','Prüfbericht','validation_report.md'),('params','Parametrierung','parameters_guide.md'),('sources','Quellen','sources.md')]
    nav=''.join(f'<a href="#{sid}">{i+1:02d} · {title}</a>' for i,(sid,title,_) in enumerate(chapters))
    sections=[]
    for sid,title,file in chapters:
        extra=''
        if sid=='overview':extra=f'<figure><img src="{image_data(root,"internal_layout.png")}" alt="Tatsächliche interne CAD-Anordnung ohne Front und Deckel"><figcaption>Links Uno, mittig gesockelter A4988, rechts TB6600. Kein zusätzliches Bediengerät.</figcaption></figure>'
        if sid=='assembly':extra=f'<figure><img src="{image_data(root,"exploded.png")}" alt="Explosionsdarstellung der konstruierten Baugruppe"><figcaption>Geometrische Explosionsansicht; Verschiebungen dienen der Sichtbarkeit, die Montagereihenfolge steht im Text.</figcaption></figure>'
        if sid=='wiring':extra=f'<figure><img src="{image_data(root,"front_rear_views.png")}" alt="Front- und Rückansicht der konstruierten Baugruppe"><figcaption>Die Zuordnung auf der Rückseite ist gegenüber der Vorderansicht gespiegelt.</figcaption></figure>'
        if sid=='dimensions':extra='<figure>'+ (root/'PREVIEWS/layout_dimensions.svg').read_text()+'<figcaption>Eigener Layoutplan. Kein ausgedruckter1:1-Bohrplan.</figcaption></figure>'
        sections.append(f'<section id="{sid}"><div class="section-no">{title}</div>'+extra+md_html(docs[file])+'</section>')
    css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#eef0f2;color:#222c34;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}main{max-width:1120px;margin:auto;background:white;padding:48px 58px 70px;margin-left:250px;border-left:1px solid #dde2e6}nav{position:fixed;left:0;top:0;bottom:0;width:250px;padding:30px 20px;overflow:auto;background:#f6f7f8}nav b{display:block;margin:0 8px 22px;font-size:14px;letter-spacing:.1em}nav a{display:block;color:#4b5863;text-decoration:none;font-size:13px;padding:8px;border-radius:4px}nav a:hover{background:#e3e9ed;color:#172d3a}.eyebrow,.section-no{color:#607681;text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:700}h1{font-size:46px;letter-spacing:-.045em;line-height:1.1;margin:14px 0 18px}h2{font-size:29px;letter-spacing:-.025em;line-height:1.25;margin:26px 0 18px}h3{font-size:20px;margin:28px 0 12px}p{margin:14px 0}section{padding-top:36px;margin-top:40px;border-top:1px solid #dbe1e6;scroll-margin-top:20px}.lead{font-size:18px;color:#53626d;max-width:760px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:18px 0;border-top:1px solid #dde2e6;border-bottom:1px solid #dde2e6;margin:26px 0}.metrics strong{display:block;font-size:23px;line-height:1.2}.metrics small{color:#61717d}.status{border-left:3px solid #7e919b;background:#f0f4f6;padding:16px 20px;font-size:14px}figure{margin:26px 0;background:#f3f4f5}figure img{display:block;width:100%;height:auto}figure svg{display:block;width:100%;max-height:720px}figcaption{font-size:12px;color:#64747f;padding:10px 14px;border-top:1px solid #e0e5e8}table{border-collapse:collapse;width:100%;font-size:13px;line-height:1.5;margin:18px 0}th{text-align:left;background:#edf1f4;color:#3c505e;font-size:12px;font-weight:700}td,th{padding:11px 12px;border-bottom:1px solid #dce3e8;vertical-align:top}td:first-child{font-weight:550}tr:nth-child(even) td{background:#fafbfc}.table-wrap{overflow-x:auto}code{font-size:.85em;background:#edf1f4;border-radius:3px;padding:2px 4px;overflow-wrap:anywhere}pre{background:#192730;color:#e8eef1;padding:18px;overflow:auto;font-size:13px}pre code{background:none;color:inherit;padding:0}li{margin:9px 0}a{color:#315e73}footer{margin-top:50px;font-size:12px;color:#687984}.hero img{max-height:600px;object-fit:contain}@media(min-width:1550px){main{margin-left:calc((100% - 1120px)/2);padding-left:64px;padding-right:64px}}@media(max-width:1000px){nav{display:none}main{margin:0;max-width:none;padding:28px 24px;border:0}h1{font-size:36px}h2{font-size:26px}table{font-size:12px}td,th{padding:8px}.metrics{gap:10px}.metrics strong{font-size:18px}}@media print{body{background:#fff;font-size:10pt}nav{display:none}main{margin:0;max-width:none;padding:0;border:0}h1{font-size:30pt}h2{font-size:18pt}h3{font-size:13pt}section{padding-top:12pt;margin-top:20pt}table{font-size:8pt}td,th{padding:6pt}figure{break-inside:avoid}figure img{max-height:215mm;object-fit:contain}.hero img{max-height:120mm}a{color:inherit;text-decoration:none}pre{white-space:pre-wrap}thead{display:table-header-group}tr{break-inside:avoid}footer{font-size:8pt}}'''
    manual=f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stepper Testbench · Montage und Fertigung · R1</title><style>{css}</style></head><body><nav><b>STEPPER / R1</b>{nav}</nav><main><header><div class="eyebrow">FDM Engineering · Uno / TB6600 / A4988</div><h1>Stepper Testbench<br>Montage und Fertigung.</h1><p class="lead">Ein schlichtes Desktop-Gehäuse mit geneigter Bedienfläche, getrennten Treiberanschlüssen und abnehmbarem Wartungsdeckel.</p><div class="metrics"><div><strong>{e['width']:.0f} × {e['depth']:.0f} mm</strong><small>Stellfläche</small></div><div><strong>18° / PETG</strong><small>Front / Zielmaterial</small></div><div><strong>3 Gehäuseteile</strong><small>plus funktionale Halter</small></div></div><figure class="hero"><img src="{image_data(root,'assembled.png')}" alt="Zusammengebautes CAD-Referenzmodell in Dunkelgrau"><figcaption>Vorschau aus der gelieferten Geometrie. Displaytext illustrativ; keine Fotografie und kein physischer Prototyp.</figcaption></figure><div class="status"><strong>Prüfstand:</strong> Referenz-CAD, Exporte und Kollisionsprüfungen bestanden. Modulmaße des eigenen Aufbaus noch nicht bestätigt. Vor dem vollständigen Druck die Messliste und Passproben abarbeiten. Keine physische, elektrische oder thermische Freigabe.</div></header>{''.join(sections)}<footer>Revision R1 · 23.10.2026 · Vollständig offline lesbar. Maß- und Prüfwerte gelten für die mitgelieferte Standardparametrierung.</footer></main></body></html>'''
    (root/'DOCUMENTATION/assembly_guide.html').write_text(manual,encoding='utf-8')
    print('Offline manual and engineering documents generated.',flush=True)

if __name__=='__main__':main()
