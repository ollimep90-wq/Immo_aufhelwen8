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

1. Excel-Prototyp und Fragenkatalog (folgt vom Nutzer) in die Bedarfsanalyse und den Vorab-Check einarbeiten.
2. Der Vorab-Check als digitales Formular ist noch nicht gebaut. Das interaktive Werkzeug muss angepasst werden.
3. Den gleichen Satz für **Gewerbe und Unternehmen** erstellen.
4. **§34i-Modell wählen:** Provision oder Honorar. Die Decks nennen beide Wege und den Satz „nie beides“.
5. **Platzhalter:** Register-Nummern, IHK, Kontaktdaten.
6. **Name und Marke.**
7. **DIN 77230:** Der Normtext lag nicht vor. Die Dokumente sagen deshalb „angelehnt“ und behaupten keine Konformität.
8. **Alte Sie-Fassungen:** Kundenpräsentation und Gesprächsleitfaden in `Finanzanlagen/` sind teilweise durch die neuen Decks ersetzt. Zu entscheiden ist, ob sie bleiben.
9. **Jans Rückmeldung** zu `03_Risikoabsicherung` und zu seiner Rolle in den anderen Decks.
10. **Masterarbeit:** Die Kapitel 3–7 sind noch „XXX“, Anhang A ist leer, und das Literaturverzeichnis enthält fremde Einträge (RFID, Industrie 4.0). Das ist für die Arbeit selbst wichtig, nicht für die Decks.
