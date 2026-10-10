# Ganzheitliche Finanzberatung – Stand 09.10.2026 (nach Endprüfung)

Arbeitstitel, Name und Marke der gemeinsamen Gesellschaft stehen noch nicht fest.
Kein „Rosenbaum Finanzberatung“-Branding mehr.

## Dateien

| Datei | Inhalt |
|---|---|
| `Konzept_Ganzheitliche_Finanzberatung.pdf` | internes Konzept, 24 Seiten |
| `Kundenpraesentation_Ganzheitliche_Beratung.pdf` | Kundenpräsentation, 17 Folien (noch nicht versandfertig) |
| `Gespraechsleitfaden_Bedarfsanalyse.pdf` | Gesprächsleitfaden mit Erfassungsbogen, 14 Seiten |
| `leitfaden_interaktiv.html` | interaktiver Leitfaden, veröffentlicht unter https://claude.ai/artifact/8PEx1U7qHEJynfq8kDsrRW (privat) |
| `src/*.html`, `build.py`, `assets/` | Quellen; PDFs neu bauen mit `python3 build.py` |
| `../Kooperation/pitch.pdf` | Kooperations-Pitch für Jan |

## Getroffene Entscheidungen (Angaben Oliver)

- **Bild:** Haus der Finanzen. Fundament = Notreserve + Absicherung existenzbedrohender Risiken, Säulen = Altersvorsorge und Vermögensaufbau, Dach = persönliche Ziele.
- **Kerngeschäft:**
  - Versicherungen und Absicherungs-Check: Jan, §34d, Courtage.
  - Finanzanlagen: Oliver, §34h.
  - Immobilienkredite: Oliver, §34i. Vermittlung mit Bankprovision und Honorarberatung schließen sich aus (§34i Abs. 5). Ein Modell muss gewählt werden, die Entscheidung ist offen.
- **Produkte Finanzanlagen:**
  - Strategiedepot über WealthKonzept: eine Strategie je Risikoklasse, 1,0 % p. a. inklusive USt und WealthKonzept. Ab 50 €/Monat oder 1.000 € einmalig (bestätigt).
  - ETF-Standarddepot bei der FondsDepot Bank: 1–2 ETFs, 0,5 % flat.
  - Altersvorsorgedepot: Vergütung nie aus dem Depot.
  - Für alle Produkte: kein Mindestentgelt; Fonds- und Depotkosten kommen hinzu.
- **Finanzplan ohne Umsetzung:** Festpreis. Gegenüber Kunden keine Stundenabrechnung, 200 €/h nur als interne Untergrenze.
- **Add-ons:**
  - Edelmetalle: Jan, Aufteilung offen.
  - Immobilien-Abo: Basis 99 €, Light 349 €, Plus 599 € netto im Monat. Plus nur mit §34c Abs. 1 Nr. 1. Keine Gutachten.
  - Krypto: nur Hinweis auf Hardware-Wallet.
  - Einzelaktien über ein Haftungsdach: langfristig.
  - Immobilienverwaltung: langfristig.
- **Ausgeschlossen:** keine Basisrente. PUK läuft über Jan.

## Offene Punkte

1. **Vergütungsweg Strategiedepot:**
   - Wie hoch ist Olivers Anteil an den 1 % (WealthKonzept ca. 0,3 %?).
   - Wer zahlt ihn aus? Zahlung über WealthKonzept wäre eine Zuwendung Dritter, für §34h kritisch. Mit Anwalt klären.
2. **ETF-Standarddepot:** Ist die USt in den 0,5 % enthalten? Depotgebühr und Einzug des Serviceentgelts bei der FondsDepot Bank klären.
3. **§34i-Modell** wählen (Vermittlung oder Honorarberatung).
4. **Platzhalter:** Registernummern, IHK, Kontaktdaten Oliver, Höhe der Darlehensprovision.
5. **Edelmetalle:** Partnerhändler, Vergütung, Aufteilung Jan/Oliver.
6. **Name und Marke:** Marken-, Register- und Domainprüfung; IHK-Anfrage zur Firmierung.
7. **Feedback von Jan** zu Konzept, Präsentation und Leitfaden.
8. **Vor dem Start prüfen:** Anwalt (Vergütungsvereinbarung, Erstinformation, Abo-AGB), Steuerberater (USt), IHK.

## Rechenbasis

Sparplan 200 €/Monat, 30 Jahre, 6 % vor Kosten (Annahme), Zins (r − c)/12, nachschüssig.

| Variante | Kosten | Endwert |
|---|---|---|
| ETF ohne Beratung | 0,3 % | 189.753 € |
| ETF-Standarddepot | 0,8 % | 172.745 € |
| Strategiedepot | 1,3 % | 157.516 € |
| Beispielprodukt | 2,0 % | 138.810 € |

## Endprüfung 09.10.2026

- Zahlen mit Python nachgerechnet, keine Rechenfehler.
- Rechtsprüfung: keine Aussage falsch. Präzisiert wurden: §34i Abs. 5, Riester-Umstellung (ohne „unwiderruflich“), Silber (Differenzbesteuerung), GwG ab 10.07.2027.
- Nicht prüfbar ohne Gesetzestext: AVRG-Details (Mindesteigenbeitrag 120 €, 175 €, 6.840 €, 150 € Übertragungskosten, Auszahlplan bis 85, 30 % Kapital, Garantie 80/100 %). Gegen BGBl. 2026 I Nr. 156 prüfen.
- Steuerbelastung Einzelunternehmen 47,6 % (42 % ESt, Anrechnung §35 EStG, Soli, Hebesatz 515 %) nachgerechnet und bestätigt.
