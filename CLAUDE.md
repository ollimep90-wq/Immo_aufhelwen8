# Immobilienankauf Auf Helwen 8 — Arbeitsregeln

Dieses Projekt begleitet den Kauf eines Mehrfamilienhauses in Nettersheim bei
120.000 € Eigenkapital. Die Verkäufer rufen **800.000 €** auf; was das Objekt
trägt, wird gerechnet und nicht gesetzt. **Eine falsche Zahl oder ein
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
7. **Jedes Dokument wird vollständig gelesen — jede Seite.** Kein Auswerten
   nach der ersten Seite, kein Überfliegen, kein Schluss aus einem Auszug. Bei
   gescannten PDFs heißt das: jede Seite rendern und ansehen, nicht nur die
   mit Text. Die entscheidende Information steht regelmäßig hinten — die
   Mieterhöhungen und die unterschriebenen Zustimmungserklärungen standen auf
   den Seiten 8 bis 10 von zehn, während aus Seite 1 bereits eine
   Schlussfolgerung über den Kaufpreis gezogen worden war. Wer nur den Anfang
   liest, erfindet den Rest.
   - Vor jeder Auswertung die **Seitenzahl** feststellen und nennen.
   - Am Ende festhalten, **welche Seiten** gelesen wurden. Was ungelesen
     blieb, wird als ungelesen ausgewiesen, nicht stillschweigend übergangen.

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
- **Der Zielpreis ist eine Rechengröße, keine Entscheidung.** Er kommt aus
  `preisregel` in `annahmen.json` und `preisbild()` in `modell.py` und ändert
  sich mit jeder neuen Information, ohne dass jemand ihn neu beschließt. Drei
  Schranken, die kleinste bindet: **Ertragsgrenze** (Preis, bei dem der
  Cashflow null ist), **Liquiditätsgrenze** (Restliquidität deckt Reserve plus
  24 Monate Defizit — sie *ist* die Obergrenze), **Mängelgrenze** (aufgerufener
  Preis minus belegbare Mängel). Stand 2026-09-19: Zielpreis **612.400 €**
  (die Ertragsgrenze bindet), Obergrenze **732.800 €**
- **800.000 € ist der aufgerufene Preis der Verkäufer, keine Obergrenze des
  Käufers.** Bis zum 2026-09-19 stand hier „Zielpreis 740.000 €, Obergrenze
  800.000 €" als feste Entscheidung. Beides ist überholt: Der alte Zielpreis
  trug auf der berichtigten Miete keinen positiven Cashflow mehr, und was der
  Verkäufer aufruft, sagt nichts darüber, was der Käufer zahlen kann. Wer die
  beiden Größen gleichsetzt, übernimmt die Preisvorstellung der Gegenseite als
  eigene Grenze

**Nach außen heißt es Altbestand und Anbau, nicht Haus A und Haus B.**
Der Verkäufer heißt Stephan und wird geduzt.

## Sprache

Alle Inhalte für den Nutzer auf Deutsch. Der Skill selbst ist auf Englisch
dokumentiert, seine Ausgaben sind deutsch.
