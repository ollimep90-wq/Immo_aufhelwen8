# Excel-Prototyp der Masterarbeit: Auswertung

Datei: `20260126_Rosenbaum_Oliver_3172714_Masterthesis_Prototyp.xlsx`, Stand Januar 2026, gelesen am 10.10.2026.
Der Prototyp ist ein Entwurf, kein festes Regelwerk (Angabe des Nutzers).

## Aufbau

| Blatt | Inhalt | Übernommen in |
|---|---|---|
| Setting_Main_Person / _2ND_Person | Stammdaten, Gehalt, Kinder, Haustiere, Eigentum, KV, Kirchensteuer, Bundesland, Vermögen nach Anlageklassen, gesetzliche Rente laut Renteninformation | Ist-Aufnahme (S. 7–8) |
| Calculation_Employment_* | Brutto → Sozialabgaben, Hochrechnung bis Rentenbeginn mit 2,5 % p. a. | noch nicht |
| Tax_calculation | Einkommensteuer nach § 32a, Splitting, Kinderfreibetrag/Kindergeld-Vergleich, Soli, Kirchensteuer → Netto | noch nicht |
| Fix_Costs / Overview | Fixkosten nach Kategorie, monatlich/jährlich | Budget (S. 7) |
| Net_income_Overview | Netto − Fixkosten = Überschuss I, − Sparen = Überschuss II, jeweils in % vom Netto | Budget (S. 7) |
| Savings | Sparraten mit Typ, Laufzeit, Dynamik | Ist-Aufnahme |
| Wealth_calculation (verborgen) | Vermögensfortschreibung nach Anlageklasse, Rendite, Abgeltungsteuer | noch nicht |
| Insurances / Risk_assessment / Risk_Dashboard | Risiko-Fragebogen „Stell dir vor …“, 9 Blöcke, 78 Fragen, gewichtet je Versicherungsart, Ampel | neue S. 9 der Bedarfsanalyse |

## Was ich übernommen habe

1. **Budgetlogik:** Überschuss I und II mit Quote statt nur „frei verfügbar“.
2. **Risiko-Check:**
   - Methode, Blöcke, Antwortskala und Filter für Kinder, Tiere, Partner und Eigentum.
   - Ampelschwellen aus der bedingten Formatierung: ab 60 % rot, 30 bis unter 60 % gelb, unter 30 % grün, 0 % nicht bewertbar.
   - Ausdrücklich ergänzt: Das Ergebnis misst Betroffenheit, nicht Deckung. Die Bewertung macht Jan.

## Befunde im Prototyp

Geprüft per Python gegen die gespeicherten Werte und gegen Quellen. Nichts davon ist im Prototyp geändert.

### Rechenfehler

1. **Einkommensteuer 2026: veraltete Tarifformel.**
   - Der Prototyp rechnet 2026 mit den Koeffizienten von 2025: 932,30 bzw. 176,64.
   - § 32a EStG ab 2026: Zone 2 (914,51·y + 1.400)·y; Zone 3 (173,10·z + 2.397)·z + 1.034,87.
   - Quellen: [gesetze-im-internet § 32a](https://www.gesetze-im-internet.de/estg/__32a.html), [finanz-tools 2026](https://www.finanz-tools.de/einkommensteuer/berechnung-formeln/2026).
   - Grundfreibetrag 12.348 € und Zonengrenzen sind richtig. Nur die Koeffizienten sind veraltet.
2. **Pflegeversicherung: Kinderabschlag ab dem ersten Kind.**
   - Der Prototyp zieht 0,25 Prozentpunkte je Kind unter 25 ab, also bei 2 Kindern 0,5 Punkte.
   - Nach § 55 Abs. 3 SGB XI gilt der Abschlag erst ab dem **zweiten** bis zum fünften Kind. Bei 2 Kindern sind es also 0,25 Punkte.
   - Im Beispiel macht das 174,38 € Beitrag im Jahr zu wenig (69.750 € × 0,25 %).
   - Quelle: [DRV, Beitragszuschlag/-abschlag](https://www.deutsche-rentenversicherung.de/DRV/DE/Experten/Arbeitgeber-und-Steuerberater/summa-summarum/Lexikon/B/beitragszuschlag_-abschlag_pflegeversicherung.html).
3. **Zu versteuerndes Einkommen vereinfacht.**
   - Vom Brutto werden die vollen Sozialabgaben abgezogen. Das deckt sich nicht mit der Vorsorgepauschale bzw. den abziehbaren Vorsorgeaufwendungen.
   - Im Ergebnis ist das Netto eine Näherung. So sollte es auch ausgewiesen werden.
4. **Splitting nur bei Ehe.**
   - Bei „verheiratet“ wird das Einkommen von Person 2 nur dann addiert, wenn die Status-ID MS_02 lautet.
   - Bei anderen Status fehlt Person 2 im Haushaltsnetto, ihr Einkommen fließt also gar nicht ein. Das ist zu prüfen.

### Vermögensrechnung (Wealth_calculation)

5. **Kirchensteuer auf Kapitalerträge fest 8 %.** Das gilt unabhängig von Bundesland und Kirchenmitgliedschaft; im Beispiel ist Hamburg mit 9 % eingestellt.
6. **Krypto mit Abgeltungsteuer.** Private Veräußerungen von Kryptowerten fallen unter § 23 EStG und sind nach einem Jahr Haltedauer steuerfrei. So wie gerechnet, ist es falsch.
7. **Fehlende Abzüge:** Sparer-Pauschbetrag und Teilfreistellung für Aktienfonds (30 %) fehlen in der Fortschreibung.
8. **Annahmen weichen von den Decks ab.**
   - Rendite: 7 % für Fonds und Krypto im Prototyp, 6 % vor Kosten in den Decks.
   - Inflation: 2,5 % im Prototyp, 2 % in den Decks.
   - Eine Quelle für die Annahmen sollte gewählt werden.
9. **Anlageklasse „Onda“ ist unklar.** Im Prototyp ist sie mit 0 % Rendite und 2 % Zins hinterlegt. Gemeint ist vermutlich Tagesgeld oder ein bestimmtes Produkt.

### Risiko-Fragebogen

10. **Gewichte in Block 4 „Haushalt, Familie, Verpflichtungen“ wirken verrutscht.**
    - Gewichtet sind Berufsunfähigkeit 2, Risikoleben 3, **Zahnzusatz 2, Rechtsschutz 2, Hausrat 1**.
    - Die Fragen dort betreffen Einkommensausfall und Kredite. Zahnzusatz, Rechtsschutz und Hausrat passen inhaltlich nicht.
    - In der Bedarfsanalyse habe ich für Block 4 nur Berufsunfähigkeit und Risikoleben aufgeführt. *Das ist eine Abweichung vom Prototyp*, bitte bestätigen.
11. **Zahnzusatz mit Gewicht 2 in Block 1** (körperliche Grenzen). Das ist fraglich.
12. **Es fehlen Privathaftpflicht, Pflege, Krankentagegeld und Kfz.** Die Privathaftpflicht ist in unserem Konzept Stufe 1. Sie braucht mindestens eine Frage oder bleibt im Absicherungs-Check.
13. **Skala passt nicht zu jeder Frage.** Manche Fragen sind Ja/Nein- oder Wie-viel-Fragen, etwa „Würdest du dein Recht durchsetzen, auch wenn es teuer wird?“ oder „Wie hoch schätzt du den Schaden ein?“. Die Antworten „existenzbedrohend … egal“ passen dort nicht. Vorschlag: diese Fragen umformulieren.
14. **Interner Hinweis im Fragentext.** Block 9 heißt „Selbstbild vs. Körperrealität (sehr wichtig für deine Argumentation)“. Der Zusatz darf nicht zum Kunden.
15. **Länge.** 78 Fragen sind für einen digitalen Vorab-Check von 10 bis 15 Minuten zu viel, siehe Frage an den Nutzer.

## Nächste Schritte

- Entscheidung zum digitalen Vorab-Check (Umfang, Form, Daten). Siehe Fragen an den Nutzer.
- Danach bauen:
  - Vorab-Check mit Netto-Näherung, Budget, Vermögen und Kurz-Risiko-Check.
  - Rechenkern in Python, gegen den Prototyp getestet, mit korrigierten Formeln.
