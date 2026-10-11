# Gewerbe-Unterlagen: Stand

**Entwurf vom 11.10.2026.** Alle vier Prüfungen (Zahlen, Widersprüche, Außenwirkung, Recht) sind für 01–05 gelaufen und für die Ergänzungen zur Unterstützungskasse (06, Folien 7a/7b in 04) ein zweites Mal; die Befunde sind eingearbeitet. Nicht an Kunden geben, bevor die Punkte unter „Vor dem Versand“ erledigt sind.

| Dokument | Stand |
|---|---|
| 01 Bedarfsanalyse Gewerbe (intern) | Entwurf, du und Sie, mit Erlaubnisgrenzen und Werten 2026 |
| 02 Unser Weg mit deinem Unternehmen | Entwurf, du und Sie |
| 03 Betrieb absichern (Jan) | Entwurf, du und Sie |
| 04 Unternehmer: absichern und vorsorgen | Entwurf, du und Sie |
| 05 Mitarbeiter: bAV und bKV (Jan) | Entwurf, du und Sie. Rechtswerte 2026 aus der Prüfung vom 11.10.2026, Beträge in `zahlen.py` gerechnet |
| 06 Konzept pauschaldotierte Unterstützungskasse (intern) | Entwurf 11.10.2026, 7 Seiten, für Gesellschafter-Geschäftsführer und Neuordnung von Pensionszusagen (Entscheidung Oliver). Geprüft, Befunde eingearbeitet. |

Segmente (Entscheidung Oliver: alles abdecken, vorher abfragen): A Selbständige/Freiberufler, B GmbH mit Gesellschafter-Geschäftsführer, C Arbeitgeber. Keine Basisrente.

Bauen: `python3 build.py` (du und Sie), Zahlen nur aus `zahlen.py`.

## Offen aus der Rechtsprüfung vom 11.10.2026 (Arbeitgeber, GmbH)

- BRSG II: Opting-out per Betriebsvereinbarung und der dort genannte Zuschuss von 20 % nur aus Sekundärquellen. Nicht in den Unterlagen, bis am Gesetzestext (BGBl. 2026 I Nr. 14) geprüft.
- § 100 EStG ab 2027: neue Werte erst nach den Rechengrößen 2027 eintragen.
- bKV: BStBl-Fundstelle des BMF-Schreibens vom 15.03.2022 und spätere Schreiben prüfen (Steuerberater).
- BAG 3 AZR 807/11: Datum 20. oder 21.01.2014 unklar, deshalb nur Aktenzeichen und Jahr zitiert.
- BBG RV 2026 (101.400 €) über Sekundärquellen belegt, BMAS-Original noch abrufen.

## Aus der Rechtsprüfung Selbständige und Erlaubnisse (11.10.2026)

- Gewerbliche Darlehen: bis 19.11.2026 § 34c-Erlaubnis nötig, ab 20.11.2026 gestrichen (BGBl. 2026 I Nr. 139). Oliver hat die Erlaubnis nach § 34c Abs. 1 S. 1 Nr. 2 (Angabe Oliver 11.10.2026). Ob gewerbliche Darlehen angeboten werden, ist noch nicht entschieden. *Korrektur:* Vorher stand hier „Nicht angeboten, bis die IHK es bestätigt“, weil die Erlaubnis nicht bekannt war. Sie stand allerdings schon im Pitch (`Kooperation/pitch.html`, „§34c Nr. 2 Darlehen“) und wurde dort übersehen.
- § 4e StBerG seit 01.09.2026: Reichweite für Finanzberater ungeklärt.
- Altersvorsorgereformgesetz (BGBl. 2026 I Nr. 156): Selbständige förderberechtigt erst ab 01.01.2027.
- Korrektur in zahlen.py: Der ALV-Beitrag in der Gründungsphase ergab mit Gleitkomma 51,41 €, richtig kaufmännisch gerundet 51,42 € (51,415 €).


## Prüfung vom 11.10.2026: was geändert wurde

- **Zahlen:** Prozentsätze (4, 8, 15, 30, 2,6 %) kommen jetzt aus `zahlen.py`. § 100 EStG und die freiwilligen RV-Beiträge werden hergeleitet, mit Kontrolle gegen die belegten Werte. Rundung kaufmännisch über Decimal (vorher Pythons round(), das 338,5 auf 338 gerundet hätte; bisher ohne Auswirkung).
- **Recht:**
  - Erwerbsminderung: Wartezeit und Ausnahmen ergänzt, Überschrift „meist“.
  - Pflichtversicherung auf Antrag: unwiderruflich.
  - Arbeitslosenversicherung: Vorversicherungszeit und Kündigung erst nach fünf Jahren ergänzt; Beitragssatz 2,6 % jetzt mit Primärbeleg (BA-Weisungen § 28a, 01/2026).
  - bAV-Anspruch nur für rentenversicherungspflichtige Mitarbeiter. Geringverdienerförderung: Abzug von der Lohnsteuer, gilt nur für bestimmte Tarife. BRSG II nur noch „soll ab 2027“.
  - bKV: monatliche Zahlung, alle Sachbezüge zusammen.
  - D&O: Bedingungen, Ausschluss bei wissentlicher Pflichtverletzung, Mehrheitsgesellschafter.
  - Unterversicherung nach § 75 VVG genauer. Haftung bei Personengesellschaften und typische persönliche Haftung des GmbH-Geschäftsführers ergänzt.
- **Außenwirkung:**
  - Keine angedeutete Haftungsentlastung des Arbeitgebers mehr.
  - Risikohinweis Fonds/ETFs.
  - „Finanzierung“ heißt jetzt „Finanzierung der privaten Immobilie“.
  - Firmenvermögen nur Oliver, nur Fonds/ETFs; Vergütung dafür gesondert.
  - Ergänzt: WealthKonzept-Hinweis, „Kein Mindestentgelt“, Datenschutzsatz.
  - Festpreis nur für den Finanzplan.
  - Kein Versprechen einer Notfallordner-Vorlage.
  - Direktzusage und Unterstützungskasse beim Steuerberater bzw. Rentenberater. Versorgungsregelung prüft Anwalt oder Steuerberater.
- **Widersprüche:**
  - Notreserve-Ampel wie Privat (rot unter 1, grün ab 6).
  - „Acht Bereiche“ statt „Sieben“.
  - Altersvorsorgedepot wie im Privat-Deck benannt, Gesetz vom 26.05.2026.
  - Lohnfortzahlung beim GmbH-Geschäftsführer.
  - GwG-Pflichten für B und C im Ablauf.
  - Jans Honorarberatung als „nicht vorgesehen“ markiert.
  - PDF-Autor der Jan-Decks.

## Vor dem Versand

1. Platzhalter in den Pflichtangaben füllen (Register-Nummern, IHK, Kontakt Oliver), `shared/brand.py`.
2. ~~§ 34c-Erlaubnis Oliver?~~ *Erledigt 11.10.2026:* vorhanden (Abs. 1 S. 1 Nr. 2). Offen: Werden gewerbliche Darlehen angeboten? Rechtslage ab 20.11.2026 von der zuständigen IHK bestätigen lassen.
3. Rentenberater/DRV: Pflichtversicherung auf Antrag, GGF-Status, Nachweis des Erwerbsminderungsschutzes.
4. Steuerberater: bKV (Fundstelle BMF 15.03.2022, jährliche Zahlung), Unterstützungskasse/Direktzusage, § 4e StBerG.
5. BRSG II am Gesetzestext (BGBl. 2026 I Nr. 14) prüfen.
6. Vergütung für Firmenvermögen festlegen; Entgeltfluss § 34h Abs. 3 (STATUS Punkt 11).
7. Jans Rückmeldung zu 03 und 05 sowie zu seiner Rolle bei Rückdeckung und Pensionsfonds (04, Folien 7, 7a, 7b).
8. Deck 04, Folien 7a/7b: erst einsetzen, wenn Erlaubnis und Rolle zur Unterstützungskasse geklärt sind (Konzept 06, Seite 7).

## Pauschaldotierte Unterstützungskasse (Wunsch Oliver, 11.10.2026)

- Olivers Einschätzung: bAV im Versicherungsmantel ist nicht sinnvoll und die schlechteste Wahl, die pauschaldotierte Unterstützungskasse flexibel und gut. Entscheidungen dazu: Zielgruppe Gesellschafter-Geschäftsführer und Neuordnung von Pensionszusagen, sachlicher Vergleich beim Kunden, Rolle erst rechtlich klären.
- Rechtsprüfung 11.10.2026: Vorteile bei Liquidität, Flexibilität und Kosten sind belegt. Die pauschale These „schlechteste Wahl“ ist nicht belegt. Beim beherrschenden GGF gibt es keinen PSV-Schutz, mit Darlehen hängt die Versorgung an der GmbH. Erdiente Anwartschaften lassen sich nicht in einem Schritt in die pauschaldotierte Kasse übertragen.
- Umgesetzt: Konzept 06 (intern), zwei Folien in Deck 04 (Wege über die GmbH, Pensionszusage neu ordnen), Fragen und Erlaubnisgrenze in der Bedarfsanalyse.
- Offen: Erlaubnis und Vergütung, Kooperationspartner (Rentenberater/Kassen-Anbieter, Gutachter), Absicherungsmodell für den beherrschenden GGF.
- Zweite Prüfung 11.10.2026, eingearbeitet:
  - Neu als Prüfpunkte: KStDV (Kasse nur für Gesellschafter gefährdet ihre Steuerfreiheit, Gruppenkasse prüfen), BFH I R 50/22 (Entgeltumwandlung ohne Insolvenzsicherung beim GGF als vGA, zur Direktzusage, Übertragbarkeit offen), Mischfall § 9 Abs. 3, Darlehensvermittlung, Anlage des Kassenvermögens (§ 34h).
  - Präzisiert: PSV nur für unverfallbare Anwartschaften, R 5.4 KStR (Herauslösung statt automatischer Verlust), Abfindung (§ 17 Abs. 3, BGH II ZR 6/16, BRSG-II-Bezug gestrichen), Begriff „beherrschend“, § 10 RDG, Pensionsfonds-Auslagerung, Tabelle auf zwei Seiten.
  - Kundenfolien: kein „wir empfehlen“ und kein „wir rechnen“ mehr, Kosten der Kasse und Insolvenzschutz des Versicherungswegs genannt, Brücke zum eigenen Vermögen neben dem Betrieb, Jan bei Rückdeckung und Pensionsfonds.
  - Korrektur: In Folie 7b stand, auch die rückgedeckte Kasse halte Liquidität im Betrieb. Das gilt nur für die pauschaldotierte.
