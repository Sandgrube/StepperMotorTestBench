# Temperatur, Betrieb und Wartung

## Passive Kühlung

Der TB6600 hat7mm freien Abstand zwischen Kühlrippenspitzen und Boden. Schlitze im Boden, in der rechten Wand und im Deckel schaffen mögliche Konvektionswege. Vier4mm hohe Füße sind funktional erforderlich. Der Treiberdeckel liegt 14.24mm unter der ebenen Deckelunterseite; unter einer Versteifungsrippe verbleiben 9.24mm. Die Bügel liegen noch höher, sind aber ebenfalls kollisionsfrei. Der A4988-Kühlkörper hat zur ebenen Deckelunterseite 28.54mm Reserve.

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
