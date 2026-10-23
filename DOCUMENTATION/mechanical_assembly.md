# Mechanische Montage

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
