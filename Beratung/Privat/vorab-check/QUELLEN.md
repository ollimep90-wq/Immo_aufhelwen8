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

Stand 11.10.2026. Geprüft mit dem Prüfagenten für Recht und Förderung am 11.10.2026: Alle Werte stimmen. Normtexte über dejure.org, weil gesetze-im-internet.de nicht erreichbar war; vor Verwendung am amtlichen Text prüfen.

- Der PV-Satz von 3,6 % beruht auf der Pflegeversicherungsbeitragssatz-Anpassungsverordnung 2025 (BGBl. 2024 I Nr. 446) nach § 55 Abs. 1 S. 2, Abs. 1a SGB XI. Der Gesetzestext selbst nennt noch 3,4 %.
- Der durchschnittliche Zusatzbeitrag 2026 von 2,9 % ist festgelegt nach § 242a SGB V (BAnz AT 10.11.2025 B7). Für Rentner gilt aber der Satz der eigenen Kasse. Die App nimmt ihn aus dem Tab Haushalt.
- **Beobachten:** Der Referentenentwurf zum Pflegeneuordnungsgesetz vom 5.6.2026 sieht vor, den Kinderlosenzuschlag ab 2027 auf 0,7 Punkte zu erhöhen. Stand Juli 2026 ist das nicht beschlossen.
- **Grenzen:**
  - Gerechnet wird die Pflichtversicherung in der KVdR. Wer die Vorversicherungszeit nicht erfüllt, ist freiwillig versichert und zahlt anders.
  - Betriebsrenten und Versorgungsbezüge sind nicht enthalten.
  - Die Nettorente gilt für den Rentenbeginn. Später ist sie etwas zu hoch, weil der Rentenfreibetrag in Euro festgeschrieben ist.
  - Die Renteninformation rechnet bis zur Regelaltersgrenze. Bei früherem Beginn fehlen Entgeltpunkte, und es gilt ein Abschlag von 0,3 % je Monat (§ 77 SGB VI). Seit 11.10.2026 rechnet die App das selbst, wenn beide Werte der Renteninformation eingetragen sind:
    - Rente aus den bisherigen Beiträgen plus gleichmäßiger Zuwachs bis zum gewünschten Beginn. Das ist dieselbe Annahme, die die Renteninformation für die Hochrechnung trifft.
    - Danach ein Abschlag von 0,3 % je Monat vor 67, höchstens 14,4 %. Mit 45 Versicherungsjahren entfällt er ab 65 (§ 38 SGB VI).
    - Nur für Jahrgänge ab 1964 (Regelaltersgrenze 67). Für ältere Jahrgänge gibt die App einen Hinweis aus.

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

## Weitere Einkünfte (Beratungs-App, Tab „Weitere Einkünfte“)

Stand 11.10.2026. Geprüft mit dem Prüfagenten für Recht und Förderung, Wortlaute über buzer.de (nicht amtlich). Vor Verwendung am amtlichen Text prüfen.

- **Vermietung (§ 21 EStG):** Der Überschuss aus Einnahmen minus Werbungskosten geht in den Tarif. Die Tilgung ist nicht absetzbar.
  - **Pauschal** (Entscheidung Oliver, 11.10.2026): Überschuss nach laufenden Kosten und Bankrate. Er gilt vereinfachend auch als steuerlicher Gewinn.
  - **EÜR:** Für die Steuer zählen Miete minus Kosten, Zinsen und AfA. Für das Budget zählen Miete minus Kosten, Zinsen und Tilgung.
- **Kapitalerträge:**
  - Abgeltungsteuer 25 % (§ 32d Abs. 1). Bei Kirchensteuer gilt (e − 4q)/(4 + k). Darauf kommt der Soli ohne Freigrenze.
  - Sparer-Pauschbetrag 1.000 €, verheiratet 2.000 € (§ 20 Abs. 9).
  - Teilfreistellung (§ 20 InvStG): Aktienfonds 30 %, Mischfonds 15 %, Immobilienfonds 60 %, Immobilienfonds Ausland 80 %.
  - **Günstigerprüfung** (§ 32d Abs. 6, Entscheidung Oliver, 11.10.2026): Die App nimmt automatisch den niedrigeren Wert aus Abgeltungsteuer und persönlichem Satz.
  - Nicht berücksichtigt: ausländische Quellensteuer.
- **Betriebsrente** (Direktversicherung, Pensionskasse, Pensionsfonds):
  - Steuer: voll steuerpflichtig (§ 22 Nr. 5 EStG).
  - Krankenversicherung: 14,6 % plus Zusatzbeitrag über dem Freibetrag von 197,75 €/Monat (§ 226 Abs. 2, § 248 SGB V).
  - Pflegeversicherung: voller Satz auf den ganzen Betrag ab der Freigrenze von 197,75 €.
  - Die 197,75 € sind 1/20 der Bezugsgröße 2026 von 3.955 €. Belegt ist das nur über Sekundärquellen.
  - Nicht gerechnet: Direktzusage und Unterstützungskasse (§ 19 EStG, Versorgungsfreibetrag).
- **Private Rente:** Besteuert wird der Ertragsanteil nach § 22 Nr. 1 S. 3 a bb EStG. Die Tabelle für 55 bis 70 Jahre ist geprüft, außerhalb dieses Bereichs wird der Wert von Hand eingetragen. In der KVdR ist sie beitragsfrei.
- **KVdR:** Miete, Kapitalerträge und private Renten sind beitragsfrei (§ 237 SGB V). Freiwillig Versicherte, zum Beispiel hauptberuflich Selbständige (§ 5 Abs. 5 SGB V), zahlen auf alles (§ 240). Das rechnet die App nicht, sie gibt einen Hinweis.
- **Fremdwährung** (Entscheidung Oliver, 11.10.2026: aktueller Kurs):
  - Umgerechnet wird mit dem EZB-Referenzkurs des Tages. Der Server ruft ihn bei der EZB ab und speichert ihn 6 Stunden zwischen; Kundendaten werden dabei nicht übertragen. Der Berater kann den Kurs überschreiben.
  - Steuerlich wird vereinfacht so gerechnet, als wären die Einkünfte in Deutschland voll steuerpflichtig. Die App weist auf das DBA, auf den Progressionsvorbehalt (Drittstaaten ja, EU/EWR nein, § 32b Abs. 1 S. 2 Nr. 3) und auf die Anrechnung hin.
- **Offen für Steuerberater:**
  - Soli-Freigrenze bei Veranlagung nach § 32d Abs. 4.
  - Quellensteuer bei Fonds.
  - Steuerliche Umrechnungskurse.
