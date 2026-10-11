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
| Kirchensteuer | 8 % in Bayern und Baden-Württemberg, sonst 9 % | Kirchensteuergesetze der Länder (nicht einzeln nachgeschlagen) | Recherche |
| Entlastungsbetrag Alleinerziehende | 4.260 € (§ 24b EStG) | BMF-Programmablaufplan 2026, S. 22 | Beleg |
| Gesamtabgleich | alle Werte oben | [BMF-Programmablaufplan Lohnsteuer 2026, Anlage 1](https://www.ihk-muenchen.de/ihk/documents/Recht-Steuern/Steuerrecht/Einkommensteuer/2025-11-12-PAP-2026-anlage-1.pdf); die Prüfung vom 10.10.2026 fand keine Abweichung | Beleg |

## Gegenprobe

- **Zwei unabhängige Umsetzungen:** `rechenkern.js` und `test_rechenkern.py` stimmen in 330 Fällen auf 1 Cent überein.
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
- Bei Ehepaaren, bei denen eine Person brutto und die andere netto angibt: Hier wird ohne Splitting gerechnet. Das Formular weist darauf hin.
- PKV: Nur der Basisanteil zählt. Das Formular fragt danach; ob die Angabe stimmt, liegt beim Kunden.
- Günstigerprüfung Kinderfreibetrag gegen Kindergeld: nicht gerechnet, nur als Hinweis.
- Übergangsbereich und Minijob: nicht abgebildet. Unter 24.000 € Jahresbrutto erscheint ein Hinweis.
- **Jährlich neu:** Werte für 2027 nach dem neuen Programmablaufplan (erscheint üblicherweise im November).

## Netto-Rente (Beratungs-App, Tab „Vermögen & Vorsorge“)

Stand 11.10.2026. Die Rechtsprüfung der Werte läuft, Ergebnis wird hier nachgetragen.

- KV der Rentner: 14,6 % + Zusatzbeitrag, davon trägt der Rentner die Hälfte (§ 247, § 249a SGB V).
- PV: voller Satz 3,6 % trägt der Rentner, kinderlos +0,6 Punkte (§ 59 Abs. 1, § 55 SGB XI). Kinderabschläge gelten nur für Kinder unter 25 und sind deshalb nicht angesetzt (Annahme: bei Rentenbeginn keine Kinder unter 25).
- PKV: Zuschuss der Rentenversicherung (§ 106 SGB VI), steuerfrei (§ 3 Nr. 14 EStG). Den PKV-Beitrag im Alter trägt der Berater ein.
- Besteuerungsanteil: 82,5 % bei Rentenbeginn 2023, +0,5 Punkte je Jahr, 100 % ab 2058 (§ 22 Nr. 1 S. 3 a aa EStG i. d. F. Wachstumschancengesetz).
- Werbungskosten-Pauschbetrag 102 € (§ 9a S. 1 Nr. 3 EStG), Sonderausgaben-Pauschbetrag 36 € (§ 10c EStG), KV/PV als Vorsorgeaufwendungen (§ 10 Abs. 1 Nr. 3 EStG).
- **Vereinfachungen (Annahmen):**
  - Tarif 2026 auf Beträge in heutiger Kaufkraft.
  - Besteuerungsanteil auf die ganze Rente, obwohl der Rentenfreibetrag in Euro festgeschrieben wird.
  - Keine weiteren Einkünfte im Alter.
  - Verheiratet ohne Angabe der Partnerrente: gleich hohe Einkünfte beider.
