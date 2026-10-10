# Beratungskonzept — Stand

Stand: 10.10.2026. Arbeitstitel „Ganzheitliche Finanzberatung“. Der endgültige Name ist noch offen.

## Was es gibt (Privatkunden)

| Datei | Für wen | Inhalt |
|---|---|---|
| `Privat/01_Bedarfsanalyse_Privat.pdf` | intern, A4 | Gesprächsleitfaden: Ablauf in 5 Schritten, Vorab-Check, Wunschleben, Ist-Aufnahme, Risikoprofil, Ampel-Regeln, Konstrukt, Ergebnisbogen |
| `Privat/02_Kennenlernen_Unser_Weg.pdf` | Kunde | Erstgespräch: Haltung, Rollen, 5 Schritte, Haus der Finanzen, Vergütung |
| `Privat/03_Risikoabsicherung.pdf` | Kunde, präsentiert von Jan | Risiken nach Stufen, Arbeitskraft, Notreserve, Absicherungs-Check, §19 VVG |
| `Privat/04_Vermoegensaufbau.pdf` | Kunde | Ziele, Zinseszins, Anlageklassen, Strategiedepot und ETF-Standarddepot, Kosten, Verhalten |
| `Privat/05_Altersvorsorge.pdf` | Kunde | drei Säulen, Rentenlücke, Kapitalbedarf, Altersvorsorgedepot, Riester-Hinweis, bAV über Jan |
| `Privat/06_Immobilien_und_Finanzierung.pdf` | Kunde | Eigenheim und Kapitalanlage, Nebenkosten, Beispielfinanzierung, Tilgung, Ablauf, Unterlagen |

## Wie gebaut wird

- Rechenwerte stehen nur in `Privat/zahlen.py`. Die Quellen verwenden `⟦Z:key⟧`.
- Bauen: `cd Beratung/Privat && python3 build.py` für alle Dokumente, `python3 build.py alter` für ein einzelnes.
- Marke, Kontakt und Pflichtangaben kommen aus `shared/brand.py`. Die Finanzanlagen-Dokumente nutzen dieselbe Quelle.

## Annahmen in den Rechenbeispielen

Alle Werte sind gekennzeichnet und gelten als Beispiel, nicht als Prognose.

- **Rendite:** 6 % vor Kosten, Kosten 1,3 %, Inflation 2 %. Die Entnahmephase rechnet real mit 1 %.
- **Rentenlücke:** 3.000 € netto, Ziel 80 %. Die gesetzliche Rente von 1.300 € netto ist eine Annahme.
- **Finanzierung:**
  - Kaufpreis 450.000 €, Nebenkosten NRW 12,07 %.
  - Die Nebenkosten setzen sich zusammen aus Grunderwerbsteuer 6,5 %, Makler 3,57 % und Notar/Grundbuch rund 2 % (Erfahrungswert).
  - Darlehen 400.000 € zu 3,8 % Zins und 2 % Tilgung.
- **Kapitalanlage:** Kaufpreis 300.000 €, Kaltmiete 1.250 €.

## Offen

1. **Excel-Prototyp:** am 10.10.2026 erhalten und ausgewertet, siehe `Prototyp_Analyse.md`. Budgetlogik und Risiko-Check sind in der Bedarfsanalyse übernommen (S. 7 und 9). Der Vorab-Check ist offen, siehe Punkt 2.
2. **Vorab-Check:** Das Formular ist gebaut (`Privat/07_Vorab-Check.html`, Quellen in `Privat/vorab-check/`). Vor dem Livegang fehlen noch:
   - Empfangsdienst für die Übermittlung (`VERSAND.url`) und ein AVV mit diesem Dienst.
   - Datenschutzerklärung und Impressum.
   - Hosting.
   - Rechtliche Prüfung der Einwilligung.
3. Den gleichen Satz für **Gewerbe und Unternehmen** erstellen.
4. **§34i-Modell wählen:** Provision oder Honorar.
   - Nach § 34i Abs. 5 GewO schließen sich Vermittlung und Honorarberatung aus, eine Wahl je Kunde ist nicht möglich.
   - *Korrektur 10.10.2026:* Die Decks sagten vorher „Provision der Bank oder, als Honorarberater, ein Honorar von dir, nie beides“. Das klang wie eine Wahl je Kunde und war deshalb falsch.
   - Jetzt steht dort der gelbe Platzhalter „[eine Provision der Bank]“, bis du entschieden hast.
5. **Platzhalter:** Register-Nummern, IHK, Kontaktdaten.
6. **Name und Marke.**
7. **DIN 77230:** Der Normtext lag nicht vor. Die Dokumente sagen deshalb „angelehnt“ und behaupten keine Konformität.
8. **Alte Sie-Fassungen:** Kundenpräsentation und Gesprächsleitfaden in `Finanzanlagen/` sind teilweise durch die neuen Decks ersetzt. Zu entscheiden ist, ob sie bleiben.
9. **Jans Rückmeldung** zu `03_Risikoabsicherung` und zu seiner Rolle in den anderen Decks.
10. **Masterarbeit:** Die Kapitel 3–7 sind noch „XXX“, Anhang A ist leer, und das Literaturverzeichnis enthält fremde Einträge (RFID, Industrie 4.0). Das ist für die Arbeit selbst wichtig, nicht für die Decks.
11. **Vor Kundeneinsatz anwaltlich klären** (Fachanwalt Bank- und Kapitalmarktrecht):
    - **§ 17 PAngV** bei den Zinsbeispielen in `06_Immobilien`. Effektivzins, Nettodarlehensbetrag und der Hinweis auf die Grundschuld sind ergänzt. Ob ein repräsentatives Beispiel nötig ist, ist offen.
    - **§ 34h Abs. 3 GewO:** Entgeltfluss beim Strategiedepot mit WealthKonzept und Erlaubnisumfang für die Vermittlung der Vermögensverwaltung.
12. **Altersvorsorgedepot, noch an Primärquellen prüfen:**
    - Stichtag für den Bonus von 200 €.
    - Teilkapital 30 %.
    - Verrechnung der Kinderzulage.
    - Mindesteigenbeitrag (laut Prüfung 120 €/Jahr, nicht übernommen).
    - Umstellung der Riester-Verträge (Fundstelle im EStG n. F.).
    - Förderberechtigung Selbständiger.
13. **USt beim ETF-Standarddepot:** „jeweils inkl. USt“ wurde am 10.10.2026 aus dem Pflichthinweis entfernt, weil es für die 0,5 % noch offen ist.
14. **Gemeinsamer Auftritt:**
    - Die Namen sind aus der Unterzeile entfernt, die Fußzeilen lauten „… in Kooperation mit …“.
    - Die gemeinsame Marke bleibt. Klären: Risiko einer Außen-GbR (siehe Pitch).
