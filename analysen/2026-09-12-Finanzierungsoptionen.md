---
type: entscheidung
object: OBJ-2026-001
title: Drei Finanzierungsoptionen — Nachbeleihung, Verkäuferdarlehen, WEG-Teilung
date: 2026-09-12
decision: offen
review_on: 2026-10-15
tags: [immobilie, finanzierung, strategie]
---

# Drei Finanzierungsoptionen

[[OBJ-2026-001|← Zurück zum Objekt]] · [[Strategie-und-Verhandlung]] ·
[[Reihenfolge-der-Optimierungen]] · [[Entscheidungsregister]]

> [!success] Zahlenstand
> Alle Beträge sind mit `modell.py` aus `annahmen.json` (Stand 2026-09-10)
> gerechnet. Nachvollziehbar mit:
>
> ```
> python3 analysen/finanzierungsoptionen.py --strategie <Objekt>/Strategie
> ```
>
> Das Skript rechnet nichts selbst, was `modell.py` kann — es importiert es.
> Was es hinzufügt, sind die drei Auswertungen zu diesen Optionen.

> [!danger] Korrekturen gegenüber den früheren Fassungen dieser Notiz
> Die ersten beiden Fassungen entstanden **ohne Vault-Zugriff** und mussten
> Bankkonditionen annehmen. Mit `annahmen.json` fällt das Wichtigste davon weg.
> Die Fehler stehen hier, statt stillschweigend ersetzt zu werden:
>
> | vorher | jetzt | warum |
> |---|---|---|
> | Beleihungsauslauf **102,79 %** des Beleihungswerts, „das Darlehen liegt über dem Beleihungswert" | **95 % des Kaufpreises**, Darlehen 703.000 € | Die 102,79 % waren die Folge eines von mir angenommenen Sicherheitsabschlags von 10 %. `annahmen.json` setzt `beleihungsauslauf_max_pct: 95` auf den **Kaufpreis** an. Meine Zahl war eine Konstruktion, keine Feststellung. |
> | Eigenkapital geht vollständig auf, keine Restliquidität | **20.100 € Restliquidität** | folgt aus derselben Korrektur |
> | „Nachbeleihungsspielraum erst ab 9,4 Jahren" | **ab Jahr 1 rechnerisch vorhanden**, aber zunächst winzig (7.340 €) | ebenso |
> | Zins 3,8 % / Tilgung 2 % / 10 Jahre Zinsbindung (1. Fassung) | Volltilger 34 J zu 5,45 % | reales Wüstenrot-Angebot |
> | Maklerprovision als offene Frage (1. Fassung) | Privatverkauf ohne Makler | steht im Entscheidungsregister |
> | Mehrmiete-Schwellen auf Basis geschätzter Marktmieten | **echte Mieten**: 5.374 €/Monat | `annahmen.json` |
>
> Was sich **nicht** geändert hat: die Bewertung der drei Optionen. Sie fällt
> mit den echten Zahlen sogar deutlicher aus.

## Ausgangslage

| Position | Betrag |
|---|---|
| Kaufpreis (Zielpreis) | 740.000 € |
| Kaufnebenkosten 8,5 % | 62.900 € |
| Gesamtbedarf | 802.900 € |
| Bankdarlehen (95 % des Kaufpreises) | 703.000 € |
| Eigenkapital benötigt | 99.900 € |
| **Restliquidität aus 120.000 €** | **20.100 €** |

| Volltilger 34 Jahre zu 5,45 %, Annuität 6,468 % | |
|---|---|
| Rate | 3.789 €/Monat |
| Zins Jahr 1 / Tilgung Jahr 1 | 38.132 € / 7.340 € |
| Miete | 5.374 €/Monat |
| NOI | 52.893 € p.a. |
| **Cashflow** | **7.421 € p.a. = 618 €/Monat** |
| Faktor 11,5 · Bruttorendite 8,71 % · Nettorendite 6,59 % | |

> [!warning] Die eine Annahme, die alles trägt
> `beleihungsauslauf_max_pct: 95` bezieht sich in `modell.py` auf den
> **Kaufpreis**. Rechnet Wüstenrot stattdessen auf einen Beleihungswert mit
> Sicherheitsabschlag, sieht alles anders aus: Bei 10 % Abschlag entspräche
> dasselbe Darlehen **105,6 %** statt 95 %.
>
> Das ist genau die Frage, die in [[Finanzierung-und-Sensitivitaet]] schon
> offen steht. Sie ist mit einem Anruf zu klären und entscheidet mehr als alles
> in diesem Dokument.

## Option 1 — Nachbeleihung

### Wann Spielraum entsteht

Spielraum = 95 % des Werts minus Restschuld:

| Jahr | Restschuld | Wert +0 % | Wert +5 % | Wert +10 % | Wert +15 % |
|---|---|---|---|---|---|
| 1 | 695.660 € | 7.340 € | 42.490 € | 77.640 € | 112.790 € |
| 3 | 679.727 € | 23.273 € | 58.423 € | 93.573 € | 128.723 € |
| 5 | 661.963 € | 41.037 € | 76.187 € | 111.337 € | 146.487 € |
| 7 | 642.158 € | 60.842 € | 95.992 € | 131.142 € | 166.292 € |
| 10 | 608.104 € | 94.896 € | 130.046 € | 165.196 € | 200.346 € |

Weil das Darlehen bei 95 % startet und nicht darüber, ist rechnerisch ab Jahr 1
etwas da. Aber 7.340 € sind kein Finanzierungsbaustein. Aus **Tilgung allein**
kommt frühestens ab Jahr 5 bis 7 ein nennenswerter Betrag zusammen — die
Anfangstilgung liegt bei 1,04 %.

### Der Test, auf den es ankommt

> Eine Maßnahme schafft Nachbeleihungsspielraum nur, wenn sie den Wert um mehr
> hebt, als sie die Schuld erhöht.

Und hier zeigt der Vault etwas, das die ursprüngliche Überlegung nicht auf dem
Schirm hatte — die Antwort steht schon in
[[Reihenfolge-der-Optimierungen]]:

| | Nebengebäude vermieten | Heizungspaket |
|---|---|---|
| Investition | **0 €** | 87.500 € brutto |
| nach 30 % Förderung | — | 61.250 € Mehrschuld |
| Mehrertrag p.a. | 4.200 € | 2.300 € Umlage |
| Wertzuwachs bei Faktor 12 | 50.400 € | 27.600 € |
| davon 95 % beleihbar | **47.880 €** | 26.220 € |
| **Netto-Spielraum** | **+47.880 €** | **−33.650 €** |

**Die Nebengebäude sind der einzige echte Nachbeleihungshebel im Objekt.**
4.200 €/Jahr für null Euro Einsatz — das hebt den Ertragswert, ohne die Schuld
anzufassen. Rang 1 der Optimierungsliste ist damit nicht nur die beste
Cashflow-Maßnahme, sondern auch die einzige, die Option 1 überhaupt trägt.

**Das Heizungspaket verbraucht Spielraum**, statt welchen zu schaffen — um rund
33.650 €. Das ist kein Argument dagegen (es ist ohnehin Pflicht, nicht Kür),
aber es widerlegt die Erwartung, energetische Sanierung erzeuge
Beleihungswert.

### Zwei Sperren, die in der Ausgangsüberlegung fehlten

**1. Der Bestand ist eingefroren.** Fünf Wohnungen wurden 2025 um 20 % erhöht,
eine 2026. Die Kappungsgrenze des § 558 Abs. 3 BGB ist damit ausgeschöpft —
die nächste Erhöhung ist **frühestens 2028 bzw. 2029** möglich
([[Mietstruktur]]). Mietwachstum im Bestand als Treiber einer Neubewertung
fällt für die nächsten zwei bis drei Jahre aus.

**2. Die Indexmiete im Altbestand sperrt weniger, als ich zunächst vermutet
hatte — hilft aber trotzdem kaum.** Details unten unter „Modernisierungsumlage".

### Was daraus für heute folgt

- **Grundschuldhöhe** bewusst entscheiden: höher bestellen als das Darlehen
  spart bei einer späteren Aufstockung Notar- und Grundbuchkosten. Kehrseite:
  Sie bleibt Sicherheit dieser Bank.
- **Sondertilgungsrecht** — ein Volltilger hat davon meist wenig. Das steht
  bereits als offener Punkt in [[Finanzierung-und-Sensitivitaet]].
- **§ 489 Abs. 1 Nr. 2 BGB**: Nach zehn Jahren ist das Darlehen mit sechs
  Monaten Frist kündbar, ohne Vorfälligkeitsentschädigung. Eine Umschuldung
  mit Nachbeleihung ist ab Jahr 10 also kostenfrei möglich — das ist der
  natürliche Termin für Option 1, und er ist bereits gesichert.

## Option 2 — Verkäuferdarlehen

### Es wirkt anders, als die Frage unterstellt

Das Bankdarlehen ist bei 95 % des Kaufpreises **gedeckelt**. Ein
Verkäuferdarlehen kann es also nicht in eine günstigere Zinsscheibe schieben —
es ersetzt **Eigenkapital**:

| Verkäuferdarlehen | EK benötigt | Restliquidität | VD-Zins 4 % | Cashflow danach |
|---|---|---|---|---|
| — | 99.900 € | 20.100 € | — | 7.421 € |
| 20.000 € | 79.900 € | 40.100 € | 800 € | 6.621 € |
| 50.000 € | 49.900 € | 70.100 € | 2.000 € | 5.421 € |
| 100.000 € | −100 € | 120.100 € | 4.000 € | 3.421 € |

Das ist ein **Liquiditätsinstrument**, kein Zinsinstrument. Und gemessen an der
Regel aus [[Reihenfolge-der-Optimierungen]] — der Puffer darf nie unter zwei
Monatsmieten, rund 10.700 €, fallen — ist das der wertvollste Effekt: Die
20.100 € Startpuffer sind knapp. Sie sind der Grund, warum in
[[Reihenfolge-der-Optimierungen]] alles vor 2028 verboten ist, was Geld kostet.

Ein Verkäuferdarlehen von 20.000 bis 50.000 € würde diesen Engpass lösen — und
zwar genau in den Jahren, in denen das Objekt sonst handlungsunfähig ist.

### Die Falle

`max_kaufpreis_ek()` zeigt, was passiert, wenn man es falsch nutzt:

| Verkäuferdarlehen | tragbarer Kaufpreis | Hebel |
|---|---|---|
| — | 888.900 € | — |
| 20.000 € | 1.037.000 € | +148.100 € |
| 50.000 € | 1.259.300 € | +370.400 € |

**Jeder Euro hebt den tragbaren Preis um rund 7,70 €**, weil nur 5 %
Eigenanteil plus 8,5 % Nebenkosten aus Eigenkapital kommen müssen.

Das ist kein Argument, mehr zu bieten. Der Zielpreis von 740.000 € steht im
[[Entscheidungsregister]] und ist aus zwei unabhängigen Wegen hergeleitet — der
Summe der belegbaren Mängel und der nötigen Restliquidität. Was die Bank noch
mitmacht, war nie das Kriterium. **Ein Verkäuferdarlehen ist ein Mittel, den
Zielpreis zu halten und Puffer zu gewinnen, nicht ein Grund, höher zu gehen.**

Wenn Stephan es als Gegenleistung für einen höheren Preis anbietet, ist das
rechnerisch fast immer schlechter: Der Preisaufschlag erhöht dauerhaft
Grunderwerbsteuer, Restschuld und den Betrag, den ein späterer Verkauf erst
wieder einspielen muss.

### Was steuerlich gilt

- **Grunderwerbsteuer fällt voll an.** Der gestundete Kaufpreisteil gehört zur
  Gegenleistung (§ 9 Abs. 1 Nr. 1 GrEStG).
- **Ein zinsloses Verkäuferdarlehen ist steuerlich vermutlich stumm.** Der BFH
  hat am 24.03.2026 (VIII R 30/24) seine bisherige Rechtsprechung aufgegeben:
  zinslose Stundung = unentgeltliche Stundung, kein Zinsanteil nach
  § 12 Abs. 3 BewG. Kein Kapitalertrag bei Stephan — aber auch **kein
  Werbungskostenabzug** bei dir. *Vorbehalt:* entschieden wurde ein
  Angehörigenfall; ob die Verwaltung folgt, ist offen.
- **Ein verzinsliches Verkäuferdarlehen** bringt den Zinsabzug nach
  § 9 Abs. 1 S. 3 Nr. 1 EStG — aber nur bei sauberer Zuordnung. Die
  **Kaufpreisaufteilung muss in die notarielle Urkunde**, die Valuta getrennt
  fließen (BFH IX R 44/95 u. a., IX R 35/08). Das lässt sich danach nicht mehr
  reparieren und berührt direkt [[Kaufpreisaufteilung-und-AfA]].

### Ein Punkt zur Verhandlung

Stephan bleibt ohnehin als Mieter im Haus und baut gleichzeitig neu — er ist
finanziell gestreckt ([[Haus-A-Sanierungsplan]] weist darauf beim Thema Kaution
hin). Das schneidet in beide Richtungen: Es macht ein Verkäuferdarlehen für ihn
weniger attraktiv, und es ist ein Grund, es nicht zu groß zu dimensionieren.

## Option 3 — WEG-Teilung

| Aufschlag | Wert | 95 % davon | − Restschuld J3 | − 15.000 € Kosten |
|---|---|---|---|---|
| 0 % | 740.000 € | 703.000 € | 23.273 € | 8.273 € |
| 5 % | 777.000 € | 738.150 € | 58.423 € | 43.423 € |
| 10 % | 814.000 € | 773.300 € | 93.573 € | 78.573 € |
| 20 % | 888.000 € | 843.600 € | 163.873 € | 148.873 € |

Auf den ersten Blick trägt sich das ab etwa 2 % Aufschlag. Drei Dinge sprechen
trotzdem dagegen, und das dritte ist ein K.-o.

**1. Es gibt einen besseren Weg zum selben Ziel.** Die Nebengebäude bringen
47.880 € Beleihungskapazität — für null Euro, ohne Teilung, ohne Wartezeit, ohne
Steuerrisiko. Das entspricht der WEG-Teilung bei gut 5 % Aufschlag nach Kosten.
**Wer Nachbeleihungsspielraum will, fängt dort an.**

**2. Der Aufschlag ist ein Selbstnutzerpreis.** Er entsteht beim Einzelverkauf
an Leute, die selbst einziehen. Für sechs vermietete Einheiten im Anbau und die
unbefristet an Stephan vermietete Einheit im Altbestand ist er nicht erzielbar.
Ob die Bank ihn im **Beleihungswert** überhaupt nachvollzieht, während alle
Einheiten gehalten und vermietet werden, ist ohnehin offen — und in
[[Finanzierung-und-Sensitivitaet]] steht bereits, dass Wüstenrot
voraussichtlich nach BelWertV rechnet, also über die nachhaltig erzielbare
Miete. Die ändert eine Teilungserklärung um null Euro.

**3. Die Drei-Objekt-Grenze — und hier wird es ernst.**

Das Objekt hat **7 Einheiten**, im Zielzustand 9. Nach dem BMF-Schreiben vom
26.03.2004 (BStBl I S. 434) und BFH GrS 1/98 ist **jede WEG-Einheit ein eigenes
Objekt**. Aus einem Objekt würden sieben bis neun. Die Aufteilung selbst gilt
als **Indiz** für Veräußerungsabsicht; die Gegenindizien müsstest du liefern.

Bei einer Umqualifizierung zum gewerblichen Grundstückshandel treffen drei
Folgen gleichzeitig:

- **Gewerbesteuer** auf Veräußerungsgewinne
- **Umlaufvermögen statt Anlagevermögen → keine AfA.** Die AfA ist in
  [[Kaufpreisaufteilung-und-AfA]] Teil der Rendite.
- **§ 23 EStG wird gegenstandslos** — die Zehnjahresfrist schützt nur im
  Privatvermögen.

Das kollidiert frontal mit der Entscheidung **„Erwerb privat"**. Und es ist
derselbe Mechanismus, der im [[Entscheidungsregister]] bereits die
PV-GmbH-Variante ausgeschlossen hat: Betriebsvermögen, § 23 EStG entfällt.

> [!success] Zwei Entwarnungen, die auch dazugehören
> - **§ 250 BauGB greift in Nettersheim nicht.** Die Norm gilt bundesrechtlich
>   weiter, wirkt aber nur über eine Landesverordnung — **NRW hat keine
>   Umwandlungsverordnung erlassen** (DNotI-Übersicht, Stand 20.01.2026:
>   nur Bayern, Berlin, Hamburg, Hessen, Niedersachsen).
> - **Keine verlängerte Kündigungssperrfrist.** Die Mieterschutzverordnung NRW
>   vom 28.01.2025 verlängert sie auf acht Jahre, aber nur in 57 Kommunen.
>   Nettersheim ist nicht dabei — aus dem Kreis Euskirchen nur Weilerswist.
>   Es gilt die Regelsperrfrist von drei Jahren (§ 577a BGB). **Dort steht auch,
>   dass Nettersheim keine Mietpreisbremse hat** — das beantwortet nebenbei
>   eine offene Frage aus [[Mietstruktur]].
>
> Was bleibt: **§ 577 BGB** gibt Stephan ein **Vorkaufsrecht**, wenn nach der
> Überlassung an ihn Wohnungseigentum begründet und seine Einheit an einen
> Dritten verkauft wird. Genau diese Zeitfolge läge vor.

## Zwei Befunde außer der Reihe

Beide kamen bei der Rechtsprüfung heraus, betreffen nicht die drei Optionen,
sind aber geldwert und zeitkritisch.

### 1. Die Förderannahmen sind überholt

Die BEG-EM-Richtlinie vom 17.07.2026 gilt seit 21.07.2026. Zwei Änderungen
treffen dieses Projekt:

| | Projektstand | ab 21.07.2026 | Differenz |
|---|---|---|---|
| Fördersatz Kapitalanleger | 30 % + 5 % Effizienzbonus | **30 %, Bonus entfallen** | −4.375 € auf das 87.500-€-Paket |
| Höchstgrenze, ein Wohngebäude 7 WE | 113.000 € | **111.000 €** | −2.000 € |
| Höchstgrenze, zwei Wohngebäude (6+1) | 135.000 € | **131.000 €** | −4.000 € |

Zu ändern: `annahmen.json` → `foerderung.effizienzbonus_pct` von 5 auf **0**
und `hoechstgrenze_ein_gebaeude` von 113000 auf **111000**. Dazu die Passage in
[[Heizung-und-Energetische-Sanierung]], die „30 %, mit Effizienzbonus 35 %"
sagt. Danach `python3 build.py`.

> [!danger] Und eine Zielkollision, die bisher nicht beziffert ist
> Der Förderhöchstbetrag der ersten Wohneinheit **sinkt ab 01.02.2027
> halbjährlich um 750 €**. Maßgeblich ist der **Zeitpunkt der Antragstellung**.
>
> Die Entscheidung „Umsetzung gebündelt nach dem Auszug" (Herbst 2027) läuft
> damit gegen eine Kostenuhr. Das ist kein Grund, sie umzuwerfen — der
> gebündelte Antrag bringt laut [[Heizung-und-Energetische-Sanierung]] das
> Mehrfache dessen, was die Absenkung kostet. Aber der Preis gehört gerechnet,
> sobald der Antragszeitpunkt feststeht. **Wichtig: Der Antrag ist an den
> Antragszeitpunkt gebunden, nicht an die Umsetzung** — es könnte also möglich
> sein, früher zu beantragen als zu bauen. Der Bewilligungszeitraum beträgt
> 36 Monate. Das ist mit dem Energieberater zu klären.

### 2. Die Modernisierungsumlage steht gegen eine Kappung, die im Vault fehlt

**§ 559e BGB** ist für den **geförderten** Heizungstausch die speziellere Norm
gegenüber § 559: 10 % der Kosten abzüglich Drittmittel, **gekappt bei
0,50 €/m² in sechs Jahren**.

| | Kappungsgrenze | annahmen.json | |
|---|---|---|---|
| Anbau, 450 m² | 2.700 €/Jahr | 2.300 €/Jahr = 0,426 €/m² | liegt darunter, plausibel |
| Altbestand, 145 m² | 870 €/Jahr | — | |

Die angesetzten 2.300 € halten also. Für den Altbestand gilt die **Indexmiete**
— und hier muss ich meine eigene frühere Vermutung korrigieren:

> [!warning] Korrektur einer Vermutung
> Ich hatte vermutet, eine Indexmiete schließe die Modernisierungsumlage aus.
> Das ist **für den Heizungstausch falsch**: § 557b Abs. 2 S. 2 BGB enthält eine
> **Rückausnahme für Maßnahmen nach § 555b Nr. 1a** (Heizungseinbau). Die
> Wärmepumpe ist also auch bei Indexmiete umlagefähig.
>
> Nur bringt das wenig: gekappt bei **870 €/Jahr** für den Altbestand. Und für
> alles jenseits der Heizungsanlage — Dämmung, Fußbodenheizung, PV — bleibt es
> dabei, dass die Indexmiete die Umlage sperrt. Die **Fußbodenheizung** bei
> Mieterwechsel ist davon nicht betroffen, weil bei Neuvermietung ohnehin neu
> verhandelt wird.
>
> Offen: Zählt der **Heizkörpertausch Typ 33** noch zur Heizungsanlage im Sinne
> von § 555b Nr. 1a? Daran hängen 20.000 € Investition. Frage an den
> Fachanwalt.

## Wie die drei zusammenhängen

| | wirkt | Voraussetzung |
|---|---|---|
| **Option 2** Verkäuferdarlehen | beim Kauf | Bank akzeptiert es; Stephan macht mit |
| **Option 1** Nachbeleihung | ab Jahr 5–7 aus Tilgung; **sofort** über die Nebengebäude | Grundschuld heute richtig bestellt |
| **Option 3** WEG-Teilung | frühestens nach Abgeschlossenheitsprüfung | Steuerberater zuerst |

Die eigentliche Einsicht: **Option 1 und Option 3 zielen beide auf mehr
Beleihungskapazität — und die billigste Quelle dafür steht schon als Rang 1 in
der Optimierungsliste.** Die Nebengebäude bringen 47.880 € für null Euro. Erst
danach lohnt es, über teurere Wege nachzudenken.

Und: **Nur Option 2 ist zeitkritisch.** Sie ist die einzige, die durch Nichtstun
verfällt — mit dem Kaufvertrag.

## Was ich empfehle

**Vor dem Notartermin:**

1. **Wüstenrot fragen**, worauf sich die 95 % beziehen: Kaufpreis oder
   Beleihungswert mit Sicherheitsabschlag? Das ist die Frage, die in
   [[Finanzierung-und-Sensitivitaet]] schon steht und mehr entscheidet als
   alles hier. Bei derselben Gelegenheit: die drei Mietvertrag-Fragen von dort.
2. **Verkäuferdarlehen sondieren** — 20.000 bis 50.000 €, mit dem erklärten
   Zweck, den Startpuffer von 20.100 € auf eine tragfähige Größe zu bringen.
   Erst die Bank fragen, ob sie es akzeptiert, dann Stephan.
3. **Grundschuldhöhe und Sondertilgungsrecht** bewusst entscheiden.
4. **Kaufpreisaufteilung in die Urkunde** — für AfA und Zinsabzug.
5. **Räumung der Garagen zum Übergabetermin in den Kaufvertrag.** Das steht
   schon in [[Reihenfolge-der-Optimierungen]] — mit dem Befund oben wird es
   wichtiger: Diese Klausel ist der Zugang zu 47.880 € Beleihungskapazität.

**Zeitnah, unabhängig davon:**

6. `annahmen.json` auf die neuen Fördersätze umstellen und `build.py` laufen
   lassen.
7. Antragszeitpunkt BEG gegen die halbjährliche Absenkung rechnen — und klären,
   ob Antrag und Umsetzung zeitlich getrennt werden können.

**Später:**

8. Nachbeleihung ab Jahr 10 vorsehen: § 489 Abs. 1 Nr. 2 BGB macht den
   Ausstieg dann kostenfrei.
9. **WEG-Teilung zurückstellen.** Erst die Nebengebäude heben, dann neu
   bewerten. Wenn die Frage wieder aufkommt: zuerst Steuerberater
   (Drei-Objekt-Grenze, ggf. verbindliche Auskunft nach § 89 Abs. 2 AO), dann
   Abgeschlossenheit, dann Bank. In dieser Reihenfolge, weil die
   steuerliche Frage die einzige ist, die das Objekt dauerhaft beschädigen
   kann.

## Offene Fragen

### An Wüstenrot — vor dem Notartermin

- [ ] Beziehen sich die 95 % auf den **Kaufpreis** oder auf einen
      Beleihungswert mit Sicherheitsabschlag? Wie hoch ist der Abschlag?
- [ ] Wird ein **Verkäuferdarlehen** akzeptiert, und wenn ja, unter welchen
      Bedingungen (qualifizierter Rangrücktritt)?
- [ ] Empfohlene **Grundschuldhöhe** im Hinblick auf spätere Aufstockung?
- [ ] **Sondertilgungsrecht** beim Volltilger — was ist möglich?
- [ ] Rechnet ihr nach **BelWertV**? Mit welchem Kapitalisierungszinssatz?
- [ ] *(bereits offen in [[Finanzierung-und-Sensitivitaet]])* Wird der
      Mietvertrag mit dem Verkäufer im Ertragswert anerkannt, und wird die
      Vertragsmiete angesetzt oder gekappt?

### An den Steuerberater — nur falls Option 3 wieder aufkommt

- [ ] Drei-Objekt-Grenze bei 7 bis 9 WEG-Einheiten. Verbindliche Auskunft nach
      § 89 Abs. 2 AO erwägen.

### An den Fachanwalt für Mietrecht

- [ ] Zählt der **Heizkörpertausch Typ 33** zur Heizungsanlage nach
      § 555b Nr. 1a BGB? Daran hängen 20.000 € Investition und die Frage, ob
      sie im Altbestand umlagefähig ist.

### An den Energieberater

- [ ] Können **Antragstellung und Umsetzung** zeitlich getrennt werden, um der
      halbjährlichen Absenkung ab 01.02.2027 zu entgehen?
- [ ] *(bereits offen)* Ein oder zwei Wohngebäude im Förderrecht? Die Differenz
      beträgt jetzt 111.000 € gegen 131.000 €.

### Für annahmen.json

- [ ] `foerderung.effizienzbonus_pct`: 5 → **0**
- [ ] `foerderung.hoechstgrenze_ein_gebaeude`: 113000 → **111000**
- [ ] Danach `python3 build.py` und `kennzahlen.py` zum Abgleich

## Annahmen, auf denen diese Analyse beruht

**Aus `annahmen.json` (Stand 2026-09-10)** — Kaufpreis, Eigenkapital,
Nebenkosten, Sollzins, Laufzeit, Beleihungsauslauf, Mieten,
Bewirtschaftungskosten, Investitionen, Modernisierungsumlage.

**Aus dem Vault** — Nebengebäude 4.200 €/Jahr und Faktor 12
([[Reihenfolge-der-Optimierungen]]), Mietstopp bis 2028/29
([[Mietstruktur]]), Zielpreis und Erwerbsstruktur ([[Entscheidungsregister]]).

**Annahme dieser Notiz** — nur drei, alle im Skript unter `PARAMETER`:

| Größe | Annahme | woher der echte Wert kommt |
|---|---|---|
| Zins Verkäuferdarlehen | 4,0 % | Verhandlung |
| Teilungskosten | 15.000 € | Angebot Architekt/Notar |
| Wertzuwachs-Stufen (+5/10/15 %) | Rechenstützstellen | — |

**Rechtsstand** — geprüft am 2026-09-12. `gesetze-im-internet.de` war nicht
erreichbar; alle Zitate von dejure.org und buzer.de mit Änderungsfußnoten.
Eine verbreitete Fundstelle führte § 557b Abs. 2 BGB noch in der Fassung vor
2024. Vor bindender Verwendung gegen die amtliche Fassung prüfen.

## Was diese Analyse umkehren würde

- **Wüstenrot rechnet auf einen Beleihungswert mit Sicherheitsabschlag** statt
  auf den Kaufpreis → die gesamte Finanzierungsarchitektur ändert sich, und
  zwar zum Schlechteren.
- **Die Garagen sind nicht frei vermietbar** (Stellplatzsatzung,
  Stellplatznachweis für den Bestand) → der einzige echte
  Nachbeleihungshebel entfällt, und Option 3 wird wieder diskutabel.
- **Die Marktmiete von 10 €/m² ist nicht erzielbar** → sie ist in
  `annahmen.json` ausdrücklich als unbelegt markiert und trägt den gesamten
  Entwicklungsteil.
- **Der Steuerberater sieht die Drei-Objekt-Grenze anders** → Option 3 verliert
  ihren K.-o.-Punkt.
