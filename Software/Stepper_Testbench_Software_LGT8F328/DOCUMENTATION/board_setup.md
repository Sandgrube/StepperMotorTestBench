# Boardauswahl LGT8F328

Die Angaben des Nutzers enthalten bislang nur LGT8F328. P/D, Gehäuse, Platinenformat und Logikspannung sind noch offen. Nicht anhand der Softwareausgabe einen physischen Chip identifizieren: der serielle Status nennt das kompilierte Ziel, keine automatisch ausgelesene Chipidentität.

IDE: Zusatz-URL https://raw.githubusercontent.com/dbuezas/lgt8fx/master/package_lgt8fx_index.json; Paket lgt8fx 2.0.7; Board LGT8F328. Variant nach tatsächlichem Chipaufdruck wählen. LQFP32: acht Beinchen pro Chipseite, LQFP48: zwölf. SSOP20 wird von diesem Kabelplan nicht unterstützt. Bei unleserlichem Aufdruck Platinenfoto bzw. genaue Produktkennung zur Identifikation verwenden.

CPU 16 MHz: Internal 32MHz / Clock Divider 2. CPU 32 MHz: Internal 32MHz / Clock Divider 1. Uploadgeschwindigkeit hängt vom vorhandenen Bootloader ab, nicht vom seriellen Monitor (115200). CLI-Profile verwenden 57600; andere Bootloader können 115200 brauchen. Keine Bootloader-Neuprogrammierung erforderlich oder getestet.

Die vorliegende Verdrahtung ist für passende 5-V-Logik ausgelegt. Boardspannung prüfen. Die Uno-CAD-Montage ist nur bei passender Uno-Platinengeometrie gültig; LGT bedeutet nicht automatisch Uno-Format.
