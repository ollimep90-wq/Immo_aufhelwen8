# Vorab-Check: Rechengrößen und Quellen

Stand 10.10.2026. Alle Werte stehen in `rechenkern.js` (`P2026`) und, unabhängig davon abgeschrieben, in `test_rechenkern.py`.

| Wert | 2026 | Quelle | Klasse |
|---|---|---|---|
| Tarif § 32a EStG | Grundfreibetrag 12.348 €; Zone 2 (914,51·y + 1.400)·y; Zone 3 (173,10·z + 2.397)·z + 1.034,87; 0,42·x − 11.135,63; 0,45·x − 19.470,38 | [gesetze-im-internet § 32a](https://www.gesetze-im-internet.de/estg/__32a.html), [finanz-tools](https://www.finanz-tools.de/einkommensteuer/berechnung-formeln/2026) | Beleg |
| Kinderfreibetrag | 9.756 € je Kind (zusammen) | [Steuerberater Schürmann](https://www.steuerberater-berlin-schuermann.de/steuernews_mandanten/dezember_2025/steuertarif_2026/) | Recherche |
| Kindergeld | 259 € | [KPMG GMS Jan. 2026](https://assets.kpmg.com/content/dam/kpmgsites/de/pdf/newsletter/global-mobility-services-news/gms-nl-januar-2026-lohnsteuer.pdf) | Recherche |
| Soli-Freigrenze | 20.350 € / 40.700 €, Milderungszone 11,9 % | [Steuerberater Schürmann](https://www.steuerberater-berlin-schuermann.de/steuernews_mandanten/dezember_2025/steuertarif_2026/) | Recherche |
| BBG KV/PV, RV/AV | 69.750 € / 101.400 € | [AOK SV-Werte 2026](https://www.aok.de/fk/fileadmin/user_upload/medien-seminare/medien/dft2026/sv-werte-2026-hb.pdf), [KSK](https://www.kuenstlersozialkasse.de/fileadmin/Dokumente/Mediencenter_K%C3%BCnstler_Publizisten/Allg._Infos_u._Anmeldeunterlagen/Aktuelle_Werte_in_der_SV_2026_bf.pdf) | Beleg |
| Beitragssätze | KV 14,6 %; Ø Zusatzbeitrag 2,9 %; PV 3,6 %; Kinderlosenzuschlag 0,6 %; RV 18,6 %; AV 2,6 % | [HWK Konstanz](https://www.hwk-konstanz.de/wp-content/uploads/rechengroessen-sozialversicherung_12-2025.pdf), [HWK Lübeck](https://www.hwk-luebeck.de/_Resources/Persistent/c/f/d/8/cfd8b65d97aa4ff846c00d4073aa3973f95fec98/rs9125_Anlage_Rechengr_SozVers_2026.pdf) | Beleg |
| PV-Kinderabschlag | 0,25 Punkte je Kind vom 2. bis 5. Kind unter 25 | [DRV](https://www.deutsche-rentenversicherung.de/DRV/DE/Experten/Arbeitgeber-und-Steuerberater/summa-summarum/Lexikon/B/beitragszuschlag_-abschlag_pflegeversicherung.html) | Beleg |
| Vorsorgepauschale 2026 | neuer AV-Teilbetrag im Rahmen von 1.900 €, keine Mindestvorsorgepauschale mehr | [Haufe](https://www.haufe.de/steuern/finanzverwaltung/vorsorgepauschale-im-lohnsteuerabzugsverfahren-ab-2026_164_658714.html), [IHK Gera](https://www.ihk.de/gera/recht-und-steuern/aktuelles-rechtundsteuern/vorsorgepauschale-ab-2026-6714522) | Recherche |
| Kirchensteuer | 8 % in Bayern und Baden-Württemberg, sonst 9 % | wie im Excel-Prototyp | Annahme, zu prüfen |

## Gegenprobe

- **Zwei unabhängige Umsetzungen:** `rechenkern.js` und `test_rechenkern.py` stimmen in 312 Fällen auf 1 Cent überein.
- **Externer Vergleich:**
  - Fall: 4.000 € brutto im Monat, Steuerklasse I, kinderlos, 36 Jahre, gesetzlich versichert mit 2,9 % Zusatzbeitrag, ohne Kirchensteuer.
  - Veröffentlichte Rechner: 2.605,50 € netto, Lohnsteuer 524,50 €.
  - Rechenkern: dieselben Werte.
  - Quellen: [rechner-portal](https://rechner-portal.de/finanzen/gehalt/4000-euro-brutto-in-netto), [test.de](https://www.test.de/Brutto-Netto-Rechner-So-viel-Netto-bleibt-uebrig-5557780-0/).

## Grenzen der Näherung

Der Rechenkern betrachtet nur das ganze Jahr. Er bildet nicht ab:

- Steuerklassen III/V und Faktorverfahren. Er rechnet mit der Jahressteuer, also so, als käme es zur Veranlagung.
- Freibeträge auf der Lohnsteuerkarte, geldwerte Vorteile und Minijobs.
- Beamte und Selbstständige; diese tragen ihr Netto direkt ein.
- Bei Ehepaaren, bei denen eine Person brutto und die andere netto angibt: Hier wird ohne Splitting gerechnet.
