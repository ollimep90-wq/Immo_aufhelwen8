# Entscheidungsrahmen

Der Zweck des Vaults ist nicht Ordnung, sondern eine **belastbare Entscheidung
unter Zeitdruck**. Der Rahmen dafür steht *vor* dem ersten guten Objekt fest,
nicht danach.

## 1. Suchprofil (`90-Meta/Suchprofil.md`)

Drei Ebenen, sauber getrennt:

**K.O.-Kriterien** — harte Ausschlüsse. Ein einziger Treffer beendet die Prüfung,
egal wie gut der Rest ist. Beispiele: Gesamtinvestition über Obergrenze ·
Erbbaurecht mit Restlaufzeit < 40 Jahre · Pendelzeit > 45 min · kein Außenbereich ·
Erdgeschoss ohne Sicherung · Hochwasser-Risikozone · Kernsanierung bei
verfügbarem Budget X.

Formuliere sie **prüfbar**: „Pendelzeit zur Arbeit unter 45 min mit ÖPNV
(Google Maps, Dienstag 8:00)" statt „gut angebunden".

**Muss-Kriterien** — nötig, aber verhandelbar gegen Preis oder Aufwand.

**Kann-Kriterien** — gewichtete Wunschliste, siehe Scoring.

Dazu gehören in dieselbe Notiz:
- **Preisobergrenze** als *Gesamtinvestition* (Kaufpreis + Nebenkosten +
  Renovierung), nicht als Kaufpreis — sonst wird sie systematisch überschritten.
- **Maximale monatliche Belastung** inklusive Puffer.
- **Datum und Begründung** jeder Änderung am Profil. Wenn sich das Profil
  während der Suche verschiebt, ist das zulässig — aber es muss sichtbar sein.

## 2. Finanzierungsrahmen (`90-Meta/Finanzierungsrahmen.md`)

Von unten nach oben rechnen, nicht vom Kaufpreis rückwärts:

```
verfügbares Eigenkapital
  − Kaufnebenkosten (9–15 %, i. d. R. nicht finanzierbar)
  − Liquiditätsreserve (mind. 3–6 Monatsausgaben, nach dem Kauf noch da!)
  = Eigenkapital, das in den Kaufpreis fließen kann

tragbare Monatsrate
  = Nettoeinkommen − Lebenshaltung − Sparraten − Puffer
  (Faustregel als Obergrenze, nicht als Ziel: max. ~35 % des Nettoeinkommens)
  → daraus über Zins + Tilgung die maximale Darlehenssumme
```

Beides zusammen ergibt die Preisobergrenze. Der Stresstest mit dem
Anschlusszins (Standard 6 %) gehört dazu — wenn die Rate nach Ende der
Zinsbindung nicht tragbar ist, ist die Obergrenze zu hoch angesetzt.

## 3. Bewertung eines Objekts — in dieser Reihenfolge

1. **Vollständigkeit.** Fehlen Kernangaben (Wohnfläche, Baujahr, Bundesland,
   Hausgeld-Split, Energiekennwert, Heizungsalter)? Dann lautet die Antwort
   „noch nicht bewertbar" plus die Liste der offenen Fragen. Keine Bewertung auf
   Basis von Lücken.
2. **K.O.-Filter.** Treffer → `status: abgelehnt`, `ko_failed` füllen, Objekt nach
   `99-Archiv/` verschieben, Begründung in die Notiz. Nicht löschen.
3. **Zahlen.** `property_calc.py` mit dem Basisszenario **und** dem Stressszenario.
4. **Scoring** der Kann-Kriterien.
5. **Risiken und offene Fragen** explizit auflisten — inklusive dessen, was man
   nicht weiß.

## 4. Scoring

Gewichte aus dem Suchprofil, Summe 100. Bewertung je Kriterium 1–5.
`score = Σ (Gewicht × Bewertung) / 5` → 0–100.

| Kriterium | Gewicht | Bewertung | Punkte |
|---|---|---|---|
| Lage / Umfeld | 25 | 4 | 20,0 |
| Preis-Leistung | 20 | 3 | 12,0 |
| Zustand / Sanierungsstau | 20 | 2 | 8,0 |
| Grundriss / Größe | 15 | 5 | 15,0 |
| Energie / Heizung | 10 | 2 | 4,0 |
| Außenbereich | 10 | 4 | 8,0 |
| **Summe** | **100** | | **67,0** |

Regeln, die den Score ehrlich halten:

- **Der Score entscheidet nichts.** Er ordnet Objekte und macht sichtbar, *warum*
  sie unterschiedlich bewertet werden. Ein K.O.-Kriterium wird nie
  weggerechnet.
- Bewertungen werden **begründet** — eine 2 bei „Zustand" ohne Satz dazu ist wertlos.
- Gewichte werden **vor** dem Objekt festgelegt. Wer Gewichte anpasst, während er
  ein konkretes Objekt bewertet, sucht Bestätigung. Falls es doch passiert:
  Datum und Grund im Suchprofil notieren, alle Objekte neu rechnen.
- Der Score ist nicht vergleichbar zwischen unterschiedlichen Gewichtungsständen.

## 5. Gebotsstrategie

Das Maximalgebot kommt aus der Rechnung, nicht aus dem Angebotspreis:

```
Maximalgebot = der Kaufpreis, bei dem entweder
               die Gesamtinvestition die Obergrenze erreicht
               oder die Monatsbelastung (auch im Stressfall) die Grenze erreicht
               — je nachdem, was zuerst greift.
```

Das Skript rechnet das rückwärts aus — jede gesetzte Grenze wird einzeln gelöst,
die strengste bindet:

```bash
python3 property_calc.py --max-price \
    --price 800000 --bundesland Nordrhein-Westfalen --commission 3.57 \
    --rent 3200 --area 210 --equity 200000 --rate 3.7 \
    --target-cashflow 0 --target-factor 22 --max-total 900000
```

`--target-cashflow 0` fragt: bis zu welchem Preis trägt sich das Objekt selbst?
`--target-factor` und `--max-total` setzen die Grenzen aus dem Suchprofil. Das
Ergebnis wird **abgerundet** — bei einer Obergrenze ist das die sichere Richtung.

Vor dem ersten Gespräch aufschreiben, mit Datum, in der Objektnotiz. Danach nicht
mehr nach oben korrigieren, außer es ändern sich **Fakten** (nicht Gefühle,
nicht ein Konkurrent). Argumente für einen Abschlag sind belegte Mängel,
Sanierungsstau mit Kostenschätzung, Sonderumlagen, lange Marktzeit.

## 6. Entscheidungsnotiz (`60-Entscheidungen/`)

Für jede echte Entscheidung eine Notiz — auch für ein „nein". Struktur:

- **Kontext** — Stand, Datum, was zur Entscheidung zwingt
- **Optionen** — mindestens die realistische Alternative, inkl. „weitersuchen"
- **Entscheidung** — ein Satz, unmissverständlich
- **Begründung** — die Zahlen und Fakten, die tragen
- **Annahmen** — worauf sie beruht (Zinssatz, Mietniveau, Sanierungskosten,
  Einkommen). Diese Liste ist der wertvollste Teil.
- **Was diese Entscheidung umkehren würde** — konkret und prüfbar
- **Überprüfen am** (`review_on`)

## 7. Verzerrungen, gegen die dieser Rahmen gebaut ist

| Effekt | Wie er sich zeigt | Gegenmittel |
|---|---|---|
| Ankereffekt | Der Angebotspreis wird zum Maßstab | Maximalgebot vorher aus den eigenen Zahlen ableiten |
| Sunk Cost | „Wir haben schon 12 Besichtigungen gemacht" | Aufwand kommt in keiner Formel vor |
| Knappheitsdruck | „Es gibt noch drei Interessenten" | Unterlagen-Checkliste bleibt Voraussetzung; unvollständig = kein Gebot |
| Besitzeffekt | Nach der zweiten Besichtigung ist es „unsere Wohnung" | K.O.-Kriterien stehen schriftlich fest und werden nicht neu verhandelt |
| Bestätigungssuche | Nur noch Argumente dafür | Jede Entscheidungsnotiz braucht die Gegenoption |

**Wenn der Nutzer eine Entscheidung gegen die eigenen Kriterien treffen will:**
einmal klar benennen, welches Kriterium verletzt wird und was das kostet. Wenn er
dabei bleibt, ist das seine Entscheidung — dann sauber dokumentieren (inklusive
der bewussten Abweichung) und weiterarbeiten. Nicht wiederholt widersprechen.
