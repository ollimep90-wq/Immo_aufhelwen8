# Immobilienankauf Auf Helwen 8 — Arbeitsregeln

Dieses Projekt begleitet den Kauf eines Mehrfamilienhauses in Nettersheim für
rund 740.000–800.000 € bei 120.000 € Eigenkapital. **Eine falsche Zahl oder ein
übersehener Widerspruch kostet hier fünf- bis sechsstellig.** Gründlichkeit geht
vor Geschwindigkeit.

## Wo was liegt

| Ort | Inhalt |
|---|---|
| `.claude/skills/obsidian/` | Der Skill: Vault-Struktur, Rechner, Referenzen |
| `.claude/agents/` | Fünf Prüfagenten, siehe unten |
| Vault `immo_invest` (beim Nutzer) | Alle Notizen zum Objekt |
| Vault `.../Strategie/` | `annahmen.json`, `modell.py`, `build.py` → die vier PDFs |

**Die einzige Quelle für Eingabewerte ist `annahmen.json`.** Wer eine Zahl
ändert, ändert sie dort und lässt `python3 build.py` laufen. Zahlen direkt in
eine Notiz oder ein PDF zu schreiben, erzeugt genau die Widersprüche, die dieses
Projekt gefährden.

## Die harten Regeln

1. **Nie Geld im Kopf rechnen.** Annuitäten, Tilgungspläne, Zinseszins immer
   über `modell.py`. Auch scheinbar einfache Prozentrechnungen laufen über
   Python.
2. **Jede Tatsachenbehauptung trägt ihre Quelle.** Belegt, eigene Angabe,
   Recherche, Annahme oder Schlussfolgerung — die Klasse gehört dazu.
3. **Annahme und Beleg werden nie vermischt.** Eine Schätzung, die in eine
   Rechnung wandert, wird als Schätzung gekennzeichnet.
4. **Nichts erfinden.** Kein Paragraf, kein Fördersatz, keine Marktmiete ohne
   Quelle. Lieber „das weiß ich nicht, das ist zu klären".
5. **Was nach außen geht, geht vorher durch die Prüfung.** Siehe
   `aussenwirkung-pruefer`.
6. **Korrekturen werden sichtbar gemacht, nicht stillschweigend eingebaut.**
   Eine revidierte Zahl bekommt einen Hinweis, was vorher dort stand und warum
   es falsch war. So bleibt nachvollziehbar, worauf eine Entscheidung beruht.

## Die Prüfagenten

Fünf Agenten in `.claude/agents/`, jeder auf einen Fehlertyp gerichtet, der in
diesem Projekt **tatsächlich vorgekommen ist**.

| Agent | Wofür | Wann einsetzen |
|---|---|---|
| `zahlen-pruefer` | rechnet jede Zahl nach, findet veraltete und widersprüchliche Werte | bevor eine Zahl in ein Entscheidungsdokument geht; nach jeder Annahmenänderung |
| `quellen-pruefer` | trennt Beleg von Annahme, findet Schlüsse, die als Fakt auftreten | nach jeder Runde mit neuen Informationen |
| `widerspruchs-pruefer` | prüft gegen getroffene Entscheidungen und beantwortete Fragen | vor jeder Auslieferung |
| `aussenwirkung-pruefer` | interne Begriffe, verratene Absichten, Vertrauliches | **immer**, bevor etwas an Verkäufer, Bank oder Dritte geht |
| `recht-und-foerderung-pruefer` | Paragrafen, Fristen, Fördersätze, Anwendbarkeit | bevor eine rechtliche oder steuerliche Aussage in ein Dokument geht |

### Das Auslieferungstor

Bevor ein PDF oder eine überarbeitete Notiz an den Nutzer geht:

1. `zahlen-pruefer` — wenn Zahlen geändert wurden
2. `widerspruchs-pruefer` — immer
3. `aussenwirkung-pruefer` — wenn das Dokument ganz oder teilweise nach außen geht

Die anderen beiden laufen anlassbezogen. Befunde werden **behoben oder
begründet abgelehnt**, nie stillschweigend übergangen.

## Der mechanische Abgleich

```
python3 .claude/skills/obsidian/scripts/kennzahlen.py \
    --strategie <Strategie-Ordner> --vault <Vault-Ordner>
```

Berechnet die Kennzahlen aus den Annahmen und meldet:

- **FEHLT** — eine Kennzahl steht nirgends im Vault, wurde also nach einer
  Änderung nicht nachgezogen
- **ABWEICHUNG** — ein Betrag liegt nahe an einer Kennzahl, ohne ihr zu
  entsprechen. Typischer Fall: eine alte Zahl hat eine Korrektur überlebt

Das Skript entscheidet nichts, es macht sichtbar. Die Bewertung macht der
`zahlen-pruefer`.

## Stand der Entscheidungen

Der verbindliche Stand steht im Vault in `Strategie-und-Verhandlung.md` und in
`Reihenfolge-der-Optimierungen.md`. Kurz:

- Erwerb **privat**, PV ebenfalls privat gewerblich
- Finanzierung: **Volltilger über 34 Jahre zu 5,45 %** (reales Angebot der
  Wüstenrot). Kein Annuitätendarlehen mit Zinsbindung — es gibt keine
  Anschlussfinanzierung und kein Zinsänderungsrisiko. Der Beleihungsauslauf
  ist in `annahmen.json` mit 95 % **des Kaufpreises** angesetzt; ob die Bank
  so rechnet oder auf einen Beleihungswert, ist offen
- Verkäufer bleiben **unbefristet** wohnen, Absicherung über **Indexmiete**
- **Ein** Förderantrag für beide Hausteile, Umsetzung gebündelt nach dem Auszug
- Wärmepumpe plus Heizkörpertausch zuerst, Fußbodenheizung bei Mieterwechsel
- PV zuletzt und aus dem Cashflow
- Zielpreis 740.000 €, Obergrenze 800.000 €

**Nach außen heißt es Altbestand und Anbau, nicht Haus A und Haus B.**
Der Verkäufer heißt Stephan und wird geduzt.

## Sprache

Alle Inhalte für den Nutzer auf Deutsch. Der Skill selbst ist auf Englisch
dokumentiert, seine Ausgaben sind deutsch.
