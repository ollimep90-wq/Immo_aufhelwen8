---
type: entscheidung
object: OBJ-2026-001
title: Drei Finanzierungsoptionen — Nachbeleihung, Verkäuferdarlehen, WEG-Teilung
date: 2026-09-12
decision: offen
review_on: 2026-10-15
tags: [immobilie, finanzierung, strategie, vertraulich]
---

> [!danger] ÜBERHOLT durch die Unterlagen vom 2026-09-18
> Diese Analyse beruht auf `annahmen.json` **Stand 2026-09-13** — vor Eingang
> der Grundbücher, Mietverträge und Abrechnungen. Drei ihrer Grundlagen sind
> widerlegt:
>
> 1. **Option 3 ist gegenstandslos.** Das Objekt ist seit dem 03.02.2003 nach
>    WEG geteilt, sieben Einheiten, Blätter 506–512. Es gibt nichts zu teilen
>    → [[Eigentumsstruktur]]. Was unten über Kosten, Abgeschlossenheit und
>    Genehmigung steht, ist erledigt; was über die **Drei-Objekt-Grenze**
>    steht, gilt weiter und ist jetzt der Ausgangszustand, nicht die Folge
>    einer Entscheidung.
> 2. **Die Kaltmiete ist 3.027 €, nicht 3.924 €** → [[Mietverhaeltnisse]].
>    Jede Cashflow-, Faktor- und Kapazitätszahl unten ist damit zu hoch.
> 3. **Die Anbaufläche ist 478 m², nicht 450.** Das erhöht die
>    Instandhaltungsrücklage in jeder Rechnung.
>
> **Der Stand nach der Umstellung**, gerechnet über `modell.py` beim Zielpreis
> 740.000 €: Cashflow **−280 €/Monat** statt +590. Der Kaufpreis, der Cashflow
> null trägt, liegt bei **685.400 €** statt 855.300 €.
>
> Die Notiz bleibt vollständig stehen — ihre Methode, die Rechtsprüfung und die
> Befunde zu Option 1 und 2 tragen weiter. Nur die Beträge sind es nicht mehr.
> Eine Neufassung folgt, wenn die letzten offenen Werte da sind
> (Mietvertrag 8a, Zustimmung 8c, Aufmaß Altbestand).

# Drei Finanzierungsoptionen

[[OBJ-2026-001|← Zurück zum Objekt]] · [[Strategie-und-Verhandlung]] ·
[[Reihenfolge-der-Optimierungen]] · [[Entscheidungsregister]]

> [!danger] Vertraulich — nichts davon geht an die Verkäufer
> Diese Notiz nennt Verhandlungsspielraum, Puffergrößen und den tragbaren
> Kaufpreis. Bevor auch nur ein Absatz in eine Mail an die Verkäufer oder an
> Wüstenrot wandert: `aussenwirkung-pruefer`.

> [!success] Zahlenstand
> Kaufpreis, Finanzierung, Mieten, Investitionen und Bewirtschaftung kommen aus
> `annahmen.json` (Stand 2026-09-13); alle Finanzmathematik aus `modell.py`.
> Förderrecht, Mietrecht und drei Bankannahmen kommen **nicht** von dort —
> sie stehen unten in der Annahmenliste.
>
> ```
> python3 analysen/finanzierungsoptionen.py --strategie <Objekt>/Strategie
> ```

> [!warning] Korrekturen — auch an dieser Fassung
> Die ersten beiden Fassungen entstanden ohne Vault-Zugriff. Die dritte hatte
> mit den echten Zahlen eigene Fehler, die die Prüfagenten gefunden haben.
> Alles steht hier, statt stillschweigend ersetzt zu werden.
>
> **Aus Fassung 1 und 2 (ohne Vault):**
>
> | vorher | jetzt |
> |---|---|
> | Beleihungsauslauf **102,79 %**, „das Darlehen liegt über dem Beleihungswert" | **95 % des Kaufpreises**. Die 102,79 % folgten aus einem von mir angenommenen Sicherheitsabschlag **und** aus dem aufgerufenen Preis statt dem Zielpreis — eine doppelte Konstruktion. |
> | Eigenkapital geht vollständig auf | **20.100 € Restliquidität** |
> | „Spielraum erst ab 9,4 Jahren" | rechnerisch ab Jahr 1, praktisch später |
> | Zins 3,8 % / Tilgung 2 % / 10 J Zinsbindung | Volltilger 34 J zu 5,45 % |
> | Maklerprovision als offene Frage | Privatverkauf ohne Makler. **Das war kein Vault-Problem** — die Frage war seit 2026-09-10 abgehakt und steht in den Projektregeln als wiederholter Fehler. |
>
> **Aus Fassung 3 (mit Vault, aber fehlerhaft):**
>
> | vorher | jetzt |
> |---|---|
> | „Räumung der Garagen **zum Übergabetermin** in den Kaufvertrag" | **zum Auszug** — so steht es abgehakt in [[Fragen-an-den-Verkaeufer]] und im [[Entscheidungsregister]]. Meine Fassung widersprach dem unbefristeten Wohnrecht. |
> | Nebengebäude wirken „sofort" | **erst ab dem Auszug.** Das verschiebt den einzigen echten Nachbeleihungshebel um Jahre — und der Auszug ist bewusst nicht erzwingbar. |
> | 47.880 € Beleihungskapazität | **rund 46.400 €**, und das ist eine Spanne. Die 4.200 €/Jahr sind eine **Brutto**miete; der Vault führt sie in einer Spalte „Netto/Jahr", rechnet die Nachbarzeilen dort aber echt netto. |
> | Heizungspaket 87.500 € / 61.250 € | **103.500 € / 72.450 €** — der Planwert des Vaults. Ich hatte die Fußbodenheizung im Altbestand weggelassen. |
> | „Netto-Spielraum −33.650 €" | **−46.230 €**. Zwei Fehler: das falsche Paket und ein Methodenbruch (95 % in der einen Spalte, nicht in der anderen). |
> | „Jeder Euro hebt den Preis um 7,70 €" | **7,41 €** — 1/0,135, nicht 1/0,13. |
> | „Die Frage nach der 95-%-Bezugsgröße steht schon in [[Finanzierung-und-Sensitivitaet]]" | **Sie steht nirgends im Vault.** Sie ist neu — und nach meiner eigenen Einschätzung die wichtigste. |
> | „echte Mieten: 5.374 €/Monat" | 3.924 € belegt **+ 1.450 € unbelegt**. `annahmen.json` markiert die Verkäufermiete selbst als „UNBELEGT". Sie trägt 27 % der Miete und 29 % des Cashflows. |
> | Höchstgrenzen-Absenkung „−2.000 € / −4.000 €" | **0 €.** Das Planpaket liegt unter jedem Deckel. |
>
> **Aus Fassung 4 — nach den Angaben des Nutzers vom 2026-09-12:**
>
> | vorher | jetzt |
> |---|---|
> | 6 Nebengebäude, 350 €/Monat, rund 46.400 € Kapazität | **3 freie Einheiten, 165 €/Monat, rund 21.900 €** (Stand 13.09.). Nicht hebbar: hintere Garage links (**bereits vermietet**), hintere Garage rechts (**Fahrradraum für die Mieter**), Partyraum (**aktuell nicht vermietbar**). |
> | Mietansätze 80/45/40/100 € als Vault-Ansatz geführt | **unbelegt.** Sie stammen aus einer frühen Projektfassung, nicht vom Nutzer. Belegt ist nur, *welche* Einheiten frei sind. |
> | Miete der hinteren Garage links als „vermutlich enthalten" behandelt | **nicht in den 3.924 € enthalten** (Nutzerangabe 13.09.). Es fließen Mieteinnahmen, die in keiner Rechnung des Vaults stehen. |
> | Bestandsniveau 8,78 €/m² | **8,72 €/m².** Die 8,78 stammten aus der alten Miete von 3.952 € und hatten deren Korrektur überlebt — genau der Fehlertyp, den das Projekt fürchtet. |
> | Verkäufermiete als Punktwert 10,00 €/m² | **Korridor 8,72–10,00 €/m²**, Fläche 140–150 m². Der Cashflow schwankt dadurch zwischen **5.261 € und 7.421 €** p.a. |

## Ausgangslage

| Position | Betrag |
|---|---|
| Kaufpreis (Kalkulationsbasis) | 740.000 € |
| Kaufnebenkosten 8,5 % | 62.900 € |
| Gesamtbedarf | 802.900 € |
| Bankdarlehen (95 % des Kaufpreises) | 703.000 € |
| Eigenkapital benötigt | 99.900 € |
| **Restliquidität aus 120.000 €** | **20.100 €** |

| Volltilger 34 Jahre zu 5,45 %, Annuität 6,468 % | |
|---|---|
| Rate | 3.789 €/Monat |
| Zins / Tilgung Jahr 1 | 38.132 € / 7.340 € |
| Miete Anbau — **vertraglich belegt** | 3.924 €/Monat |
| Miete Altbestand — **noch zu vereinbaren**, Korridor 8,72–10,00 €/m², 140–150 m² | 1.221–1.500 €/Monat |
| **Cashflow** | **7.421 € p.a. = 618 €/Monat** |
| Faktor 11,5 · Bruttorendite 8,71 % · Nettorendite 6,59 % | |

> [!warning] Die Miete ist zu 27 % unbelegt
> Die 5.374 € bestehen aus **3.924 € Anbau** (bestätigt 2026-09-10) und
> **1.450 € Altbestand** = 145 m² × 10,00 €/m². Dieser zweite Teil ist kein
> Vertrag, sondern eine Zielannahme — `annahmen.json` markiert sie selbst als
> „UNBELEGT", und [[Haus-A-Sanierungsplan]] empfiehlt, die Übergangsmiete am
> **Bestandsniveau** anzusetzen — dort stand bis zum 2026-09-13 noch 8,78 €/m²,
richtig sind
> **8,72 €/m²** (die Notiz gehört nachgezogen).
>
> | | 10,00 €/m² | 9,36 €/m² | 8,72 €/m² |
> |---|---|---|---|
> | Cashflow p.a. | 7.421 € | 6.341 € | **5.261 €** |
> | Cashflow/Monat | 618 € | 528 € | **438 €** |
>
> Das sind **2.160 € oder 29 % des Cashflows**, die an einer Zahl hängen, die
> noch verhandelt wird. Der Nutzer hat den Korridor am 2026-09-12 bestätigt:
> zwischen der Durchschnittsmiete des Hauptgebäudes und 10 €/m². Die
> Restliquidität von 20.100 € ändert sich dabei nicht — sie hängt am Kaufpreis,
> nicht an der Miete.

> [!danger] Die wichtigste offene Frage — und sie ist neu
> `beleihungsauslauf_max_pct: 95` bezieht sich in `modell.py` auf den
> **Kaufpreis**. Rechnet Wüstenrot stattdessen auf einen Beleihungswert mit
> Sicherheitsabschlag, entspräche dasselbe Darlehen bei 10 % Abschlag
> **105,6 %** — und wäre so nicht darstellbar.
>
> Ich hatte geschrieben, die Frage stehe schon in
> [[Finanzierung-und-Sensitivitaet]]. **Das stimmt nicht.** Dort stehen drei
> andere Bankfragen (ob der Mietvertrag mit den Verkäufern im Ertragswert
> anerkannt und ob die Vertragsmiete gekappt wird). Eine Volltextsuche über den
> Vault findet keine Stelle, an der die **Bezugsgröße** der 95 % hinterfragt
> wird — [[Reihenfolge-der-Optimierungen]] und [[Rechenweg-Cashflow]] setzen
> „95 % des Kaufpreises" als gegeben.
>
> **Diese Frage gehört ins Entscheidungsregister unter „Was noch offen ist",
> blockiert die gesamte Finanzierungsarchitektur, fällig vor dem Notartermin.**

## Option 1 — Nachbeleihung

### Wann Spielraum entsteht

| Jahr | Restschuld | Wert +0 % | Wert +5 % | Wert +10 % | Wert +15 % |
|---|---|---|---|---|---|
| 1 | 695.660 € | 7.340 € | 42.490 € | 77.640 € | 112.790 € |
| 3 | 679.727 € | 23.273 € | 58.423 € | 93.573 € | 128.723 € |
| 5 | 661.963 € | 41.037 € | 76.187 € | 111.337 € | 146.487 € |
| 7 | 642.158 € | 60.842 € | 95.992 € | 131.142 € | 166.292 € |
| 10 | 608.104 € | 94.896 € | 130.046 € | 165.196 € | 200.346 € |

Aus **Tilgung allein** kommt frühestens ab Jahr 5 bis 7 ein Betrag zusammen,
mit dem sich etwas anfangen lässt — die Anfangstilgung liegt bei 1,04 %.

### Der Test, auf den es ankommt

> Eine Maßnahme schafft Nachbeleihungsspielraum nur, wenn sie den Wert um mehr
> hebt, als sie die Schuld erhöht.

**a) Nebengebäude separat vermieten** — Rang 1 in
[[Reihenfolge-der-Optimierungen]], **drei freie Garagen**, null Euro Investition.
*(Die Rangliste dort rechnete bis zum 2026-09-13 mit sechs Einheiten und
350 €/Monat; inzwischen korrigiert.)*

Die Höhe ist allerdings zu klären:

| Ansatz | netto p.a. | Beleihungskapazität |
|---|---|---|
| brutto, ohne jeden Abzug | 1.980 € | 22.572 € |
| − Mietausfallwagnis 3 % | 1.921 € | **21.895 €** |
| − zusätzlich Verwaltung 30 €/Einheit | 841 € | 9.583 € |

| frei verfügbar | Ansatz | nicht hebbar | Grund |
|---|---|---|---|
| Wohnmobilgarage (im Haus) | 80 € | Partyraum | **aktuell nicht vermietbar** |
| Garage Auto (im Haus) | 45 € | hintere Garage links | **bereits vermietet** |
| Garage klein (im Haus) | 40 € | hintere Garage rechts | Fahrradraum für die Mieter |

> [!warning] Die Ansätze sind unbelegt
> Auf die Frage, woher 80/45/40 € stammen, lautet die Antwort des Nutzers:
> **„Sind von dir. Nicht von mir."** Sie stammen aus einer frühen Fassung dieses
> Projekts und sind nie am Markt geprüft worden. Belegt ist ausschließlich,
> *welche* Einheiten frei sind — nicht, was sie bringen.
>
> Damit steht die gesamte Zahl auf einer Schätzung, die niemand verantwortet.
> `annahmen.json` führt das jetzt so (`_quelle_nebengebaeude`).

Der Vault führte den Betrag in einer Spalte **„Netto/Jahr"**, rechnete die
Nachbarzeilen dort aber echt netto: Rang 4 (WE 8) kommt von 7.200 € brutto über
Ausfallwagnis, Instandhaltung und Verwaltung auf exakt die 5.904 €, die in der
Tabelle stehen — für Rang 1 fehlte dieser Schritt.

**Behoben am 13.09.:** `build.py` rechnet die Zeile jetzt netto, die PDFs sind
neu erzeugt. Der mittlere Ansatz ist plausibel — Garagen brauchen kaum
Verwaltung und keine Instandhaltungsrücklage nach Wohnfläche —, aber das ist
eine Einschätzung, keine Rechnung.

**b) Heizungspaket** — der Planwert aus
[[Heizung-und-Energetische-Sanierung]], alle sechs Positionen einschließlich
Fußbodenheizung im Altbestand:

| | |
|---|---|
| Kosten brutto | 103.500 € |
| − 30 % Grundförderung = **Mehrschuld** | 72.450 € |
| Modernisierungsumlage | 2.300 € p.a. |
| Wertzuwachs bei Faktor 12 | 27.600 € |
| davon 95 % beleihbar | 26.220 € |
| **Netto-Spielraum** | **−46.230 €** |

Und die härtere Zahl, die in den früheren Fassungen ganz fehlte:

| Kapitaldienst des Pakets | |
|---|---|
| Modernisierungsdarlehen 5,5 % / 15 J, Annuität 9,805 % | 7.104 € p.a. |
| − Modernisierungsumlage | 2.300 € p.a. |
| **= Cashflow-Belastung** | **4.804 € p.a.** |
| bei einem Gesamtcashflow von | 7.421 € p.a. |

**Das Heizungspaket kostet fast zwei Drittel des Cashflows.** Das ist kein
Argument dagegen — es ist Pflicht, nicht Kür — aber es ist der Grund, warum die
Reihenfolge aus [[Reihenfolge-der-Optimierungen]] eingehalten werden muss.

*(Nebenbefund: [[Reihenfolge-der-Optimierungen]] misst Rang 3 am
Ausbaudarlehen mit 8,255 % statt am Modernisierungsdarlehen mit 9,805 %. Für
eine Modernisierung ist der zweite Block der richtige — das macht die Maßnahme
um 1,55 Prozentpunkte teurer als dort gerechnet.)*

### Drei Sperren

**1. Der Bestand ist eingefroren.** Fünf Wohnungen 2025 um 20 % erhöht, eine
2026 — die Kappungsgrenze des § 558 Abs. 3 BGB ist ausgeschöpft, nächste
Erhöhung frühestens **2028 bzw. 2029** ([[Mietstruktur]]).

**2. Die Nebengebäude sind erst ab dem Auszug frei.** In
[[Fragen-an-den-Verkaeufer]] steht abgehakt: *„Werden die Garagen geräumt
übergeben? — ja, **zum Auszug der Verkäufer**. Bis dahin nutzen sie sie weiter,
gegebenenfalls über einen separaten Mietvertrag."* Der Auszug ist für Herbst
2027 geplant, aber nach der Entscheidung **unbefristet und nicht erzwingbar**.
Der einzige echte Nachbeleihungshebel steht damit unter einem Zeitvorbehalt,
den man bewusst akzeptiert hat.

**3. Die Indexmiete im Altbestand** — siehe unten, sperrt weniger als vermutet,
hilft aber kaum.

> [!note] Ein Vorbehalt, der auch für die Nebengebäude gilt
> Ich argumentiere gegen Option 3, die Bank rechne nach BelWertV über den
> kapitalisierten Reinertrag, eine Teilungserklärung ändere daran nichts.
> Dasselbe Argument trifft die 21.895 €: Auch dort wird aus einer Mehrmiete über
> einen Faktor Beleihungskapazität. Ob Wüstenrot Garagen- und Partyraummieten
> als nachhaltig ansetzt, ist offen — und eine Neubewertung kostet Geld und
> braucht einen Anlass. Der Faktor 12 liegt zudem über dem objekteigenen
> Faktor 11,5.

### Was daraus für heute folgt

- **Grundschuldhöhe** bewusst entscheiden — höher bestellen spart bei einer
  späteren Aufstockung Notar- und Grundbuchkosten.
- **Sondertilgungsrecht** — ein Volltilger hat davon meist wenig. *(Steht
  bereits als offener Punkt in [[Finanzierung-und-Sensitivitaet]], dort
  allerdings unter der Überschrift „Die alte Annahme (überholt)" — der Punkt
  selbst ist gültig und gehört herausgezogen.)*
- **§ 489 Abs. 1 Nr. 2 BGB**: Nach zehn Jahren ist das Darlehen mit sechs
  Monaten Frist kündbar, ohne Vorfälligkeitsentschädigung. Das ist der
  natürliche Termin für eine Umschuldung mit Nachbeleihung — und er ist
  bereits gesichert.

## Option 2 — Verkäuferdarlehen

### Es wirkt anders, als die Frage unterstellt

Das Bankdarlehen ist bei 95 % des Kaufpreises **gedeckelt**. Ein
Verkäuferdarlehen kann es nicht in eine günstigere Zinsscheibe schieben — es
ersetzt **Eigenkapital**:

| Verkäuferdarlehen | EK benötigt | Restliquidität | Zins 4 % | Cashflow danach |
|---|---|---|---|---|
| — | 99.900 € | 20.100 € | — | 7.421 € |
| 20.000 € | 79.900 € | 40.100 € | 800 € | 6.621 € |
| 50.000 € | 49.900 € | 70.100 € | 2.000 € | 5.421 € |

Über 99.900 € hinaus bringt es nichts — mehr Eigenkapital als nötig ersetzt es
nicht. Und die Rechnung unterstellt ein **tilgungsfreies** Darlehen: Die
Restliquidität ist gestreckt, nicht geschenkt.

**Warum das der wertvollste der drei Effekte ist:** Die 20.100 € Startpuffer
sind knapp. Sie sind der Grund, warum in [[Reihenfolge-der-Optimierungen]] vor
2028 alles verboten ist, was Geld kostet, und die Regel lautet, nie unter zwei
Monatsmieten (rund 10.700 €) zu fallen. Und weil Option 1 erst ab dem Auszug
wirkt — der nicht erzwingbar ist —, muss der Puffer genau diese unbestimmte
Zeit überbrücken. **Option 2 ist damit nicht die Alternative zu Option 1,
sondern ihre Voraussetzung.**

### Die Falle

> [!danger] Diese Tabelle verlässt die Datei nie — auch nicht gegenüber der Bank
> Sie zeigt nicht nur, dass das Objekt die Obergrenze trägt, sondern wie weit
> darüber hinaus. Wer sie kennt, verhandelt gegen dich.

| Verkäuferdarlehen | tragbarer Kaufpreis | Hebel |
|---|---|---|
| — | 888.900 € | — |
| 20.000 € | 1.037.000 € | +148.100 € |
| 50.000 € | 1.259.300 € | +370.400 € |

**Jeder Euro hebt den tragbaren Preis um 7,41 €** — aus Eigenkapital kommen nur
8,5 % Nebenkosten plus 5 % Eigenanteil, zusammen 13,5 %.

Das ist kein Argument, mehr zu bieten. Zielpreis 740.000 €, Obergrenze
800.000 € — beides steht im [[Entscheidungsregister]] und ist aus belegbaren
Mängeln und nötiger Restliquidität hergeleitet, nicht aus dem, was die Bank
mitmacht. Ein höherer Preis erhöht dauerhaft Grunderwerbsteuer, Restschuld und
den Betrag, den ein späterer Verkauf erst wieder einspielen muss.

### Wie man es anspricht

> [!important] Ohne Begründung fragen
> Das [[Entscheidungsregister]] hält fest: *„Fragen ohne Begründung stellen.
> Wer erklärt, wofür er eine Auskunft braucht, verrät seine Pläne."* Den
> Verkäufern mitzuteilen, dass die Restliquidität knapp ist, wäre die denkbar
> schlechteste Eröffnung einer Preisverhandlung.
>
> Also: sondieren, ohne den Zweck zu nennen; den Zins nicht proaktiv ansprechen;
> **spät platzieren**, nicht als Einstieg.

Zwei Punkte zur Konstruktion:

- **Wer sind „die Verkäufer"?** Die Eigentümerfrage ist offen — in
  [[Fragen-an-den-Verkaeufer]] steht als Priorität-1-Frage, wer im Grundbuch
  eingetragen ist, und ob eine Erbengemeinschaft besteht. Bei mehreren Verkäufern
  ändert sich die Dimensionierung (pro Kopf klein halten) und der Kreis der
  Vorkaufsberechtigten nach § 577 BGB.
- Die Verkäufer **bauen gleichzeitig neu** (belegt). *Schlussfolgerung,
  unbelegt:* Daraus folgt vermutlich begrenzte Liquidität — was ein
  Verkäuferdarlehen für sie weniger attraktiv macht und ein Grund wäre, es
  nicht groß zu dimensionieren. [[Haus-A-Sanierungsplan]] zieht denselben
  Schluss beim Thema Kaution. **Die Annahme ist nicht geprüft und darf im
  Gespräch nie als Argument auftauchen** — eine Einschätzung über die
  Finanzlage der Gegenseite beschädigt ein Verhältnis per Du dauerhaft.

### Was steuerlich gilt

- **Grunderwerbsteuer fällt voll an** (§ 9 Abs. 1 Nr. 1 GrEStG).
- **Ein zinsloses Verkäuferdarlehen ist steuerlich vermutlich stumm** — BFH
  24.03.2026, VIII R 30/24: zinslose Stundung = unentgeltliche Stundung. Kein
  Kapitalertrag bei den Verkäufern, aber auch **kein Werbungskostenabzug** bei
  dir. *Vorbehalt:* entschieden wurde ein Angehörigenfall.
- **Ein verzinsliches** bringt den Zinsabzug (§ 9 Abs. 1 S. 3 Nr. 1 EStG) — aber
  nur bei sauberer Zuordnung: **Kaufpreisaufteilung in die notarielle Urkunde**,
  Valuta getrennt (BFH IX R 44/95, IX R 35/08). Berührt
  [[Kaufpreisaufteilung-und-AfA]].
- **Spannung, die dem Notar vorzulegen ist:** [[Due-Diligence-Status]] rät,
  ein Verkäuferdarlehen **separat** zu regeln und nicht im Notarvertrag zu
  verankern. Der Zinsabzug verlangt aber die Kaufpreisaufteilung in der Urkunde.
  Beides muss zusammengehen.

## Option 3 — WEG-Teilung

| Aufschlag | Wert | 95 % davon | − Restschuld J3 | − 15.000 € |
|---|---|---|---|---|
| 0 % | 740.000 € | 703.000 € | 23.273 € | 8.273 € |
| 5 % | 777.000 € | 738.150 € | 58.423 € | 43.423 € |
| 10 % | 814.000 € | 773.300 € | 93.573 € | 78.573 € |
| 15 % | 851.000 € | 808.450 € | 128.723 € | 113.723 € |
| 20 % | 888.000 € | 843.600 € | 163.873 € | 148.873 € |

Die Spalte „− Restschuld" zählt die ohnehin erfolgte Tilgung mit und sieht
deshalb günstiger aus, als die Maßnahme ist. **Inkrementell** gerechnet muss der
Aufschlag 2,13 % erreichen, damit allein die Teilungskosten hereinkommen — und
rund **5,2 %**, um so viel zu bringen wie die Nebengebäude. *(Die Schwelle ist
gesunken, weil der Nebengebäude-Hebel kleiner geworden ist — nicht, weil die
Teilung besser wurde. Die Drei-Objekt-Grenze bleibt ihr K.-o.)*

Drei Dinge sprechen dagegen, das dritte ist ein K.-o.

**1. Es gibt einen billigeren Weg zum selben Ziel** — aber er ist deutlich
schmaler geworden. Die Nebengebäude bringen noch rund 21.900 € für null Euro und
ohne Steuerrisiko. Beide wirken allerdings erst
ab dem Auszug — der Zeitvorteil, den ich der Nebengebäude-Lösung in einer
früheren Fassung zugeschrieben hatte, besteht nicht.

**2. Der Aufschlag ist ein Selbstnutzerpreis** — für sechs vermietete Einheiten
im Anbau und die unbefristet vermietete Einheit im Altbestand nicht erzielbar.
Und [[Finanzierung-und-Sensitivitaet]] hält fest, dass Wüstenrot
voraussichtlich nach BelWertV rechnet, also über die nachhaltig erzielbare
Miete. Die ändert eine Teilungserklärung um null Euro.

**3. Die Drei-Objekt-Grenze.** Das Objekt hat **7 Einheiten**, im Zielzustand 9.
Nach BMF 26.03.2004 (BStBl I S. 434) und BFH GrS 1/98 ist jede WEG-Einheit ein
eigenes Objekt. Die Aufteilung selbst gilt als **Indiz** für
Veräußerungsabsicht. Bei Umqualifizierung: **Gewerbesteuer**, **keine AfA**
(Umlaufvermögen), **§ 23 EStG entfällt**. Das kollidiert mit „Erwerb privat" —
und ist derselbe Mechanismus, der im [[Entscheidungsregister]] schon die
PV-GmbH ausgeschlossen hat.

> [!success] Zwei Entwarnungen
> - **§ 250 BauGB greift in Nettersheim nicht.** NRW hat keine
>   Umwandlungsverordnung erlassen (DNotI-Übersicht, Stand 20.01.2026).
> - **Keine verlängerte Kündigungssperrfrist.** Die Mieterschutzverordnung NRW
>   vom 28.01.2025 gilt in 57 Kommunen; Nettersheim ist nicht dabei, aus dem
>   Kreis Euskirchen nur Weilerswist. Es gilt die Regelsperrfrist von drei
>   Jahren (§ 577a BGB) — **und keine Mietpreisbremse.** Das bestätigt, was
>   [[Haus-A-Sanierungsplan]] bereits als Faktum führt und [[Mietstruktur]] noch
>   als „zu bestätigen" offenhält.
>
> Was bleibt: **§ 577 BGB** gibt den Verkäufern ein **Vorkaufsrecht**, wenn nach
> der Überlassung an sie Wohnungseigentum begründet und ihre Einheit an einen
> Dritten verkauft wird.

## Zwei Befunde außer der Reihe

### 1. Die Förderannahmen sind überholt — aber weniger schlimm als gedacht

Die BEG-EM-Richtlinie gilt in der seit 21.07.2026 geltenden Fassung (BAnz AT
27.08.2026 B1). Das früher hier genannte Ausfertigungsdatum 17.07.2026 ließ
sich in keiner Quelle bestätigen; belegt ist das Inkrafttreten.

| | Deckel alt | Deckel neu | Zuschuss alt | Zuschuss neu |
|---|---|---|---|---|
| Ein Wohngebäude, 7 WE | 113.000 € | 111.000 € | 31.050 € | 31.050 € |
| Zwei Wohngebäude (6+1) | 135.000 € | 131.000 € | 31.050 € | 31.050 € |

**Das Planpaket von 103.500 € liegt unter jedem dieser Deckel. Die Absenkung
der Höchstgrenze kostet damit 0 €** — und dasselbe gilt für die offene Frage
„ein oder zwei Wohngebäude", solange der Umfang nicht wächst. *(In der letzten
Fassung hatte ich −2.000 € und −4.000 € als Einbuße ausgewiesen. Das war
falsch: Deckeländerungen sind keine Euro-Wirkung, solange das Paket darunter
liegt.)*

Die einzige Änderung mit echter Wirkung ist der **Effizienzbonus**:

| Fördersatz auf 103.500 € | Zuschuss |
|---|---|
| Projektstand vor dem 21.07.2026: 35 % (30 + 5) | 36.225 € |
| ab 21.07.2026: 30 % | 31.050 € |
| **entgangene Chance** | **5.175 €** |

**Aber:** Der Vault-Eigenanteil von 72.450 € ist bereits mit 30 % gerechnet. Der
Wegfall ändert ihn **nicht** — er nimmt nur den besseren Fall. Und der Bonus
galt laut [[Heizung-und-Energetische-Sanierung]] ohnehin nur „bei passender
Technik", war also nie gesichert.

> [!note] Keine Zielkollision mit dem Auszug
> Der Höchstbetrag der ersten WE sinkt ab 01.02.2027 halbjährlich um 750 €.
> Maßgeblich ist der **Antragszeitpunkt** — und der liegt im Vaultplan bei
> Mitte 2027, die Umsetzung bei Winter 2027/28.
>
> In der letzten Fassung hatte ich daraus eine Kollision mit „Umsetzung
> gebündelt nach dem Auszug" konstruiert. Das war falsch und hätte Druck auf
> einen Auszugstermin erzeugt, den die Entscheidung bewusst offenlässt. Beim
> Planpaket, das unter jedem Deckel liegt, ist die Wirkung ohnehin **0 €**.

### 2. Die Modernisierungsumlage ist zu niedrig angesetzt

**§ 559e BGB** ist für den **geförderten** Heizungstausch die speziellere Norm:
**10 %** der Kosten abzüglich Drittmittel, gekappt bei **0,50 €/m²** in sechs
Jahren.

[[Heizung-und-Energetische-Sanierung]] leitet die 2.300 € aus **§ 559 mit 8 %**
auf rund 28.750 € umlagefähige Kosten ab. Nach der eigenen Rechtsanalyse dieser
Notiz gilt aber § 559e:

| | Anbau, 450 m² |
|---|---|
| § 559 (8 %) — so im Vault | 2.300 € p.a. |
| § 559e (10 %) | 2.875 € p.a. |
| Kappung 0,50 €/m² | 2.700 € p.a. |
| **maßgeblich** | **2.700 € p.a.** |

Das sind **400 € p.a. mehr** als angesetzt. `annahmen.json` sollte 2.700 €
führen.

> [!warning] Und die Kappung steht im Vault falsch
> [[Heizung-und-Energetische-Sanierung]] nennt „bequem innerhalb der
> Kappungsgrenze von **3 €/m²** in sechs Jahren" — das ist § 559 Abs. 3a. Nach
> § 559e sind es **0,50 €/m²**, also ein Sechstel. Der Abstand zwischen 0,426
> und 0,50 €/m² ist deutlich enger als der zu 3 €/m². Dort steht außerdem
> „0,45 €/m²", richtig sind 0,426 €/m².
>
> *(In der letzten Fassung schrieb ich, die Kappung „fehle im Vault". Sie fehlt
> nicht — sie steht falsch da. Das ist eine Korrektur, kein Lückenschluss.)*

Für den **Altbestand** gilt die Indexmiete: § 557b Abs. 2 S. 2 BGB enthält eine
**Rückausnahme für § 555b Nr. 1a** (Heizungseinbau), die Wärmepumpe ist also
umlagefähig — gekappt bei **870 €/Jahr**. Alles jenseits der Heizungsanlage
(Dämmung) bleibt gesperrt. Offen: Zählt der **Heizkörpertausch Typ 33** noch
dazu? Daran hängen 20.000 €.

## Wie die drei zusammenhängen

| | wirkt | Voraussetzung |
|---|---|---|
| **Option 2** Verkäuferdarlehen | beim Kauf | Bank akzeptiert es; Verkäufer machen mit |
| **Option 1** Nachbeleihung | ab Jahr 5–7 aus Tilgung; über die Nebengebäude **ab dem Auszug** | Grundschuld heute richtig bestellt |
| **Option 3** WEG-Teilung | frühestens nach Steuerberatung | Drei-Objekt-Grenze geklärt |

**Die Reihenfolge ergibt sich von selbst:** Option 1 wirkt erst ab dem Auszug,
der nicht erzwingbar ist. Bis dahin muss der Puffer von 20.100 € halten — und
genau den hebt Option 2. Option 3 zielt auf dasselbe wie Option 1, kostet mehr
und riskiert die AfA.

## Was ich empfehle

**Vor dem Notartermin:**

1. **Wüstenrot fragen, worauf sich die 95 % beziehen** — Kaufpreis oder
   Beleihungswert. Das ist die neue, wichtigste Frage.
   > [!warning] Blank stellen
   > Die Rechnung, dass dasselbe Darlehen bei 10 % Abschlag 105,6 % ergäbe und
   > „so nicht darstellbar" wäre, darf die Frage **nicht** begleiten. Wer der
   > Bank mitteilt, dass die eigene Architektur bei ihrer Methode zusammenbricht,
   > bekommt die Methode, die sie zusammenbrechen lässt.

   Die versandfertige Fassung dieser und aller weiteren Bankfragen steht in
   [[2026-09-12-Fragen-an-die-Bank]].
2. **Verkäuferdarlehen sondieren, ohne den Zweck zu nennen.** Erst die Bank
   fragen, ob sie es akzeptiert, dann die Verkäufer. **Früh im Prozess, spät im
   Gespräch** — nicht als Einstieg. Den Zins nicht proaktiv ansprechen, und
   keine Spanne zuerst nennen: wer die erste Zahl nennt, ankert. Frag, was für
   sie vorstellbar wäre. *(Interner Korridor: 20.000–50.000 €.)*
3. **Grundschuldhöhe** bewusst entscheiden.
4. **Kaufpreisaufteilung in die Urkunde** — für AfA und Zinsabzug. Mit dem Notar
   klären, wie sich das mit der separaten Regelung eines Verkäuferdarlehens
   verträgt.
5. **Mietgegenstand positiv definieren**, nicht negativ. Also: „die Wohnung
   im Altbestand mit den Räumen X, Y, Z, dem Kellerabteil und dem
   Carport-Stellplatz" — statt aufzuzählen, was *nicht* mitvermietet wird.
   Rechtlich identisch (was nicht benannt ist, ist nicht vermietet), aber eine
   Negativliste mit Dachboden, Garagen und Partyraum legt die drei
   Entwicklungsflächen nebeneinander auf den Tisch. Der Dachboden ist dabei der
   teuerste Verrat.
   Für die Nebengebäude bis zum Auszug genügt ein separater Vertrag — ohne auf
   Kündbarkeit zu bestehen, Garagenmietverträge sind ohnehin frei kündbar.
   *(Die Räumung selbst ist unverdächtig: zugesagt am 2026-09-10, zum Auszug.
   Nicht zur Übergabe — das widerspräche dem unbefristeten Wohnrecht.)*
6. **Die Miethöhe im Mietvertrag mit den Verkäufern** durchrechnen — sie trägt
   29 % des Cashflows und bestimmt über § 10 Abs. 1 BelWertV womöglich den
   Beleihungswert.
   > [!danger] Nur intern
   > Der Verkäufer ist hier zugleich der künftige Mieter. Erfährt er, dass an
   > seiner Miethöhe fast ein Drittel deines Cashflows hängt, hat er einen Hebel, den
   > er gegen den Kaufpreis tauschen kann — und sein eigenes Interesse zeigt
   > ohnehin nach unten. Im Gespräch wird die Miete als schlichter Marktwert
   > verhandelt, nicht als etwas, das du brauchst.

**Zeitnah:**

7. `annahmen.json` korrigieren (Liste unten), dann `build.py` und
   `kennzahlen.py`.

**Später:**

8. Nachbeleihung ab Jahr 10 vorsehen — § 489 Abs. 1 Nr. 2 BGB macht den
   Ausstieg dann kostenfrei.
9. **WEG-Teilung zurückstellen.** Falls die Frage wiederkommt: zuerst
   Steuerberater (Drei-Objekt-Grenze, ggf. verbindliche Auskunft nach
   § 89 Abs. 2 AO), dann Abgeschlossenheit, dann Bank.

## Was im Vault nachzuziehen ist

> [!success] Alle sieben sind am 2026-09-13 durchgezogen
> Die Liste unten bleibt stehen, weil sie den Befund dokumentiert. Was in jeder
> Notiz geändert wurde, steht dort jeweils in einem Korrekturkasten — nach
> Regel 6 sichtbar, nicht stillschweigend. Der Verlauf in [[OBJ-2026-001]]
> fasst es zusammen.
>
> Zwei Dinge sind **bewusst** unverändert geblieben:
> - **Der Ordner `99-Archiv/`.** Ein Archiv protokolliert historische Stände;
>   es zu korrigieren hieße, die Nachvollziehbarkeit zu zerstören, für die es da
>   ist. Gleiches gilt für die Einträge im Verlauf von [[OBJ-2026-001]], die
>   älter als heute sind.
> - **Die Ampelsymbole in [[Due-Diligence-Status]].** Die Zahlen dahinter sind
>   korrigiert, die Bewertung rot/gelb/grün steht dir zu.

Die Prüfung hatte **sieben** Stellen gefunden, an denen eine alte Fassung
weiterlebte. (Hier stand zuvor „vier" — das war der Stand vor den letzten beiden
Prüfrunden und ist mit der Liste unten nie mitgewachsen.)
Keine davon stammt aus dieser Notiz, alle betreffen Zahlen, die Entscheidungen
tragen.

**1. ✅ Die Restliquidität von 4.500 € lebte an fünf Stellen weiter** —
erledigt 2026-09-13, einschließlich der beiden Risikozeilen in
[[OBJ-2026-001]], die zunächst übersehen worden waren:
[[Due-Diligence-Status]], [[Heizung-und-Energetische-Sanierung]],
[[Startpaket-WP-und-PV]], [[Vorbereitung-vor-dem-Verkaeufergespraech]] — und
**[[OBJ-2026-001]] an zwei Stellen**, obwohl die Notiz dort andernorts bereits
auf 20.100 € korrigiert ist. Korrigiert sind [[Reihenfolge-der-Optimierungen]],
[[Rechenweg-Cashflow]] und der Finanzierungsrahmen.
**In der Heizungsnotiz trägt die alte Zahl ein Argument**: Sie entscheidet dort
„praktisch allein" gegen „beide Wärmepumpen gleichzeitig". Mit 20.100 € ist zu
prüfen, ob die Begründung noch trägt — die Entscheidung selbst (gemeinsamer
Antrag, gebündelte Umsetzung) ist davon unberührt.

**2. ✅ Die Förderkorrektur betraf mehr als zwei Stellen** — erledigt
2026-09-13, dazu die Bonus-Tabelle und der hartkodierte Hebelbetrag in
`build.py`/`unterlagen.py`. Neben
`annahmen.json` sind in [[Heizung-und-Energetische-Sanierung]] betroffen: der
Effizienzbonus-Eintrag, die Höchstgrenzen 113.000/135.000, die Zuschussspannen,
der Planwert-Block und die Wiederholung im Fragenteil. Dazu der Eigenanteil
72.450 €, der über [[Rechenweg-Cashflow]] in den Cashflow ab 2028 wandert.

**3. ✅ [[Finanzierung-und-Sensitivitaet]] rechnete noch mit 3.952 € Miete** —
erledigt 2026-09-13: Die Notiz trägt jetzt einen Überholt-Kasten mit dem
gültigen Stand.
[[Mietstruktur]] behauptet, „alle Rechnungen im Vault sind auf 3.924 €
umgestellt" — das stimmt nicht: Die Sensitivitätstabellen laufen mit 5.225 €
und 6.452 € Gesamtmiete. Die Notiz steht zudem auf einer überholten
Finanzierungsarchitektur (Modernisierungskredit im Kaufdarlehen, Gesamtdarlehen
bis 910.000 €), die [[Rechenweg-Cashflow]] bereits verworfen hat. Ich verweise
in dieser Notiz mehrfach darauf — die Verweise gelten den dort **offenen
Fragen**, nicht den Rechnungen.

**4. ✅ Die Garagenfrage** — erledigt 2026-09-13, Frage wieder geöffnet. [[Reihenfolge-der-Optimierungen]] trägt noch „Räumung
zum Übergabetermin" und „sofort nach Übergabe" — beides steht vor der Antwort
vom 2026-09-10 („zum Auszug"). Schwerer wiegt: In
[[Fragen-an-den-Verkaeufer]] ist **abgehakt**, die „Garagen nutzen die
Eigentümer selbst". Das ist durch die Angabe vom 13.09. falsch geworden — eine
falsch abgehakte Frage wird nicht mehr gelesen und ist damit gegen Nachprüfung
immunisiert. Sie gehört wieder geöffnet.

**5. ✅ Das Bestandsniveau 8,78 €/m² lebte an sechs Stellen weiter** — erledigt
2026-09-13 —
[[Mietstruktur]], [[Haus-A-Sanierungsplan]] (dreimal),
[[Fragen-an-den-Verkaeufer]], [[OBJ-2026-001]] und [[Nettersheim]] — dazu die
daraus abgeleiteten 1.273 €/Monat und 5.197 € Gesamtmiete.

**6. ✅ Die alte Nebengebäude-Rechnung (4.200 €/Jahr, 350 €/Monat)** — erledigt
2026-09-13. Sie stand in
[[Reihenfolge-der-Optimierungen]], [[Strategie-und-Verhandlung]] und — am
schwersten — im [[Entscheidungsregister]]: Dort ist die Entscheidung
„Reihenfolge: Nebengebäude zuerst" mit „4.200 €/Jahr für null Investition"
begründet. Tatsächlich sind es **1.921 €**. Die Entscheidung selbst trägt
weiter (Rang 1 bleibt Rang 1, null Investition bleibt null), aber ihre
Begründungszahl ist um Faktor 2,2 zu hoch. Nach der Registerregel wird die
Zeile nicht überschrieben, sondern durchgestrichen und neu eingetragen.

**7. ✅ [[OBJ-2026-001]]** — erledigt 2026-09-13. Die Notiz nannte „95 % der **Gesamtkosten** (Kaufpreis +
Modernisierung)" statt des Kaufpreises — das ist die verworfene Architektur —
und führt die **Maklerfrage** als offen, obwohl sie seit dem 10.09. beantwortet
ist.

## Offene Fragen

> [!warning] Die Formulierungen hier sind Rohmaterial
> Klammerzusätze, Beträge und Begründungen sind **interne Notizen**. Keine
> dieser Zeilen wird so verschickt. Die versandfertigen Fassungen stehen in
> [[2026-09-12-Fragen-an-die-Bank]] und gehören für die Verkäuferseite in
> [[Fragen-an-den-Verkaeufer]] — nicht hierher dupliziert, sonst wird
> irgendwann die falsche Fassung versendet.

### An Wüstenrot

Versandfertig in [[2026-09-12-Fragen-an-die-Bank]]. Was dort **nicht** steht und
auch nicht hingehört, aber intern der Grund für die Fragen ist:

- Die Bezugsgröße der 95 % entscheidet die gesamte Architektur — bei 10 %
  Abschlag wären es 105,6 %. **Diese Rechnung begleitet die Frage nicht.**
- An der Frage, ob Garagenmieten als nachhaltig angesetzt werden, hängen rund
  21.900 € Beleihungskapazität. **Auch das nennt die Frage nicht** — wer zeigt,
  wie viel an einer Antwort hängt, lädt zur vorsichtigen Antwort ein.
- Die Frage nach der Mietbewertung ist bewusst als **Methodenfrage** gestellt,
  nicht als Frage zum Mietvertrag mit den Verkäufern. Wer auf den einen
  verwundbaren Vertrag zeigt und das Stichwort „Kappung" mitliefert, bekommt
  genau dort geprüft — und verliert die Anrechnung von 1.450 €/Monat.

### An die Verkäufer

> [!danger] Beantwortet — und die Antwort kostet Klarheit
> Die **hintere Garage links ist vermietet, und ihre Miete ist NICHT in den
> 3.924 € enthalten** (Nutzerangabe 2026-09-13).
>
> Damit fließen heute Mieteinnahmen, die in **keiner** Rechnung dieses Vaults
> stehen — weder im Cashflow noch im Kaufpreisfaktor noch in der Bruttorendite.
> Die Höhe ist unbekannt. Aus den Mietverträgen zu ermitteln; die
> Unterlagenanforderung deckt das ab.
>
> Für die Bewertung heißt das: Der Cashflow von 7.421 € ist um diesen Betrag
> **zu niedrig** angesetzt. Das ist die einzige der offenen Zahlen, die in die
> günstige Richtung wirkt.

Alle drei Fragen stehen bereits in [[Fragen-an-den-Verkaeufer]] (Grundbuch als
Priorität 1, Nebengebäude als Priorität 3, Verkäuferdarlehen als Priorität 4).
**Dort pflegen, nicht hier duplizieren.** Drei Anmerkungen dazu:

- Die Frage nach den Nebengebäuden muss **alle** umfassen — die drei Garagen im
  Haus, die beiden hinteren Garagen und den Partyraum. Wer nur die
  ertragsstärksten herausgreift, signalisiert, dass er gerechnet hat.
- **Keine Begründung, keine Beträge.** Welche Einheit wieviel trägt, ist eine
  interne Zahl — und obendrein eine unbelegte.
- [[Fragen-an-den-Verkaeufer]] **siezt** durchgehend und ist auf einen
  Adressaten im Singular geschrieben. Beides widerspricht der Sprachregelung und
  dem offenen Eigentümerstand — vor dem Versand auf du/ihr umstellen und die
  Mehrzahl prüfen.

### An den Steuerberater — nur falls Option 3 wiederkommt

- [ ] Drei-Objekt-Grenze bei 7 bis 9 WEG-Einheiten; verbindliche Auskunft nach
      § 89 Abs. 2 AO erwägen.

### An den Fachanwalt für Mietrecht

- [ ] Zählt der **Heizkörpertausch Typ 33** zur Heizungsanlage nach
      § 555b Nr. 1a BGB? *(20.000 € Investition)*
- [ ] Gilt für den geförderten Heizungstausch § 559e statt § 559? *(400 €/Jahr)*

### An den Energieberater

- [ ] *(bereits offen)* Ein oder zwei Wohngebäude im Förderrecht? **Beim
      Planpaket wirkungslos** — erst relevant, wenn der Umfang an den Deckel
      stößt.
- [ ] *(bereits offen)* Wie lang ist der Bewilligungszeitraum **konkret**?
      Die 36 Monate sind eine Annahme.

### Für `annahmen.json`

- [x] ~~`foerderung.effizienzbonus_pct`: 5 → **0**~~ — erledigt 2026-09-12
- [x] ~~`foerderung.hoechstgrenze_ein_gebaeude`: 113000 → **111000**~~ — erledigt
- [x] ~~`mieten.haus_a_bestandsniveau_eur_m2`: 8,78 → **8,72**~~ — erledigt; die
      8,78 hingen an der alten Miete von 3.952 €
- [x] ~~`ausbau.nebengebaeude`: auf die **drei** freien Einheiten~~ — erledigt; die
      **drei** nicht hebbaren stehen separat als `nebengebaeude_nicht_hebbar`
- [ ] `modernisierungsfinanzierung.modernisierungsumlage_haus_b_jahr`:
      2300 → **2700** — **bewusst noch nicht geändert**, weil § 559e erst vom
      Fachanwalt zu bestätigen ist. Der Hinweis steht in der Datei.
- [x] ~~Danach `build.py`~~ — gelaufen, alle vier PDFs neu erzeugt
- [x] ~~`kennzahlen.py`~~ — gelaufen, keine neuen Abweichungen

## Annahmen, auf denen diese Analyse beruht

**Aus `annahmen.json` und `modell.py`** — Kaufpreis, Eigenkapital, Nebenkosten,
Sollzins, Laufzeit, Beleihungsauslauf, Mieten, Bewirtschaftung, Investitionen,
sämtliche Finanzmathematik.

**Aus dem Vault** — Nebengebäude-Ansätze und Faktor 12, Mietstopp bis 2028/29,
Zielpreis und Erwerbsstruktur, Puffer-Regel, Heizungs-Planwert 103.500 €.

**Unbelegt oder Annahme** — vollständig, nicht nur drei:

| Größe | Klasse | woher der echte Wert kommt |
|---|---|---|
| **Verkäufermiete** — Punkt im Korridor 8,72–10,00 €/m² | Korridor belegt (Nutzer 12.09.), Punkt darin offen | Mietvertrag |
| **Nebengebäude-Ansätze** (165 €/Monat) | **unbelegt** — stammen aus einer frühen Projektfassung, nicht vom Nutzer | Marktvergleich |
| **Miete der hinteren Garage links** | vermietet, Höhe unbekannt, **nicht in den 3.924 €** | Mietvertrag |
| Faktor 12 | Vault-Ansatz, über dem objekteigenen 11,5 | Bewertung |
| Sicherheitsabschlag 10 % | Annahme, nur für die Gegenrechnung | Bank |
| Zins Verkäuferdarlehen 4 %, tilgungsfrei | Annahme | Verhandlung |
| Teilungskosten 15.000 € | Annahme | Angebot Architekt/Notar |
| BEG-Staffel 28.000/15.000/8.000 €, Absenkung 750 €/Halbjahr | **Recherche 2026-09-12** | KfW-Merkblatt 458, vor Antragstellung bestätigen |
| Bewilligungszeitraum 36 Monate | Recherche, im Vault als offen geführt | Energieberater |

**Rechtsstand** — geprüft 2026-09-12. `gesetze-im-internet.de` war nicht
erreichbar; Zitate von dejure.org und buzer.de mit Änderungsfußnoten. Eine
verbreitete Fundstelle führte § 557b Abs. 2 BGB noch in der Fassung vor 2024.
Vor bindender Verwendung gegen die amtliche Fassung prüfen.

## Was diese Analyse umkehren würde

- **Wüstenrot rechnet auf einen Beleihungswert statt auf den Kaufpreis** → die
  gesamte Finanzierungsarchitektur ändert sich, zum Schlechteren.
- **Die Verkäufermiete wird an der unteren Korridorecke vereinbart** (8,72 €/m²)
  → Cashflow 5.261 € statt 7.421 €, der Puffer wird knapper, Option 2 wird
  zwingend.
- **Die Mietansätze halten nicht.** Sie sind unbelegt; schon 20 € weniger je
  Garage kosten rund 7.960 € Kapazität — bei diesem Hebel mehr als ein Drittel.
- **Die Stellplatzsatzung verlangt die Garagen für den Bestand** → derselbe
  Effekt, vollständig.
- **Die Bank setzt Garagenmieten nicht als nachhaltig an** → ebenso.
- **Der Steuerberater sieht die Drei-Objekt-Grenze anders** → Option 3 verliert
  ihren K.-o.-Punkt.
