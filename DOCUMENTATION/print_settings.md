# Druckvorbereitung · Bambu Lab P2S

Alle STLs sind Millimeterdateien, geschlossene positiv orientierte Dreiecksnetze und bereits für den Druck ausgerichtet. STEP-Teile liegen dagegen in Einbaulage vor. STL und STEP daher nicht unbemerkt unterschiedlich skalieren. Maximales Baumaß des größten Teils: 230 ×176; mit 5-mm-Brim bleibt es innerhalb256 ×256.

| Einstellung | Praktischer Startwert |
| --- | --- |
| Material | PETG, trocken; mattes Dunkelgrau/Schwarz. PLA nur für Passproben oder nach Temperaturprüfung. |
| Düse / Schicht | 0,4mm /0,20mm; für die kleinen Ringe bei Bedarf0,16mm |
| Perimeter / Top-Bottom | 4 Wände; 5 obere und5 untere Lagen; Bügel/Clips/Ringe5 Wände |
| Infill | 15…20% Gyroid für Schalen; 35…50% bei Bügeln; kleine Clips/Ringe praktisch massiv |
| Stützen | Im Entwurf nicht erforderlich; Brückentest vor den großen Teilen. |
| Brim | 5mm bei Bodenschale/Front nach Haftung; kleine Bügel/Ringe ggf.3mm |
| Oberfläche | Sichtseiten von Front/Deckel auf gleiche strukturierte Platte legen. Keine Ironing-Pflicht. |
| Temperaturen / Geschwindigkeit | Das Profil des konkreten PETG verwenden, nicht unbekannte Temperaturen übernehmen. Außenwände für saubere Radien moderat drucken. |
| Elefantenfuß | Mit Coupon einstellen; als Ausgangsversuch0,10…0,15mm Kompensation, nicht als geprüfter P2S-Wert. |

## Brücken und Überhänge

Die längste geplante horizontale Brücke am aufrechten Chassis ist das USB-Dach mit etwa12mm. Weitere Heckfenster haben gefaste obere Ecken; Muttertaschen überbrücken ungefähr6mm. Die Wandlüftung endet in45°-Dächern. Frontstützen stehen im Druck etwa18° gegen die Vertikale und benötigen keine separate Stütze. Kleine Piloten und Kabelbinderanker haben kurze Brücken. Die glatte Unterseite enthält keine großen überbrückten Fußtaschen.

Wenn der PETG-Brückentest am eigenen Material misslingt: zuerst Fluss/Kühlung und Brückengeschwindigkeit einstellen. Nur falls nötig lokale manuelle Stützen im USB-Dach setzen; keine flächigen Stützen an Sichtseiten. Diese optionale Maßnahme ist keine getestete Slicereinstellung.

## Reihenfolge

1. Mutter- und Pilotcoupon drucken, reale Muttern/Schrauben prüfen.
2. LCD-, Joystick- und Portcoupon drucken, echte Module und Kabel anlegen.
3. Vier Distanzringe und kleine Halter drucken; die Bügel am TB6600 prüfen.
4. Front und Schale erst nach Maßprüfung drucken; Deckel abschließend.

Es wurde kein Slicer ausgeführt, keine Platte im Bambu-Profil getestet und keine3MF-Datei vorbereitet. Druckzeit und Filamentverbrauch sind daher nicht als Slicerwerte angegeben. Die technischen Volumina in validation_results.json sind massive CAD-Volumina; Infill und reale Extrusionsbreiten verändern die Druckmasse. PLA nicht als Freigabe für hohe Treiberströme betrachten.
