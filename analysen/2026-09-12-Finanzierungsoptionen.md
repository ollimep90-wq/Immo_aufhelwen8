---
type: entscheidung
object: Auf Helwen 8
date: 2026-09-12
decision: offen
review_on: 2026-10-15
---

# Drei Finanzierungsoptionen — Nachbeleihung, Verkäuferdarlehen, WEG-Teilung

> [!warning] Zahlenstand dieser Notiz
> Diese Analyse entstand in einer Umgebung **ohne Zugriff auf den Vault und
> damit ohne `annahmen.json`**. Jede Zahl unten ist entweder aus
> `CLAUDE.md` belegt oder ein **Platzhalter**, und jede ist als das eine oder
> andere gekennzeichnet. **Bevor eine dieser Zahlen eine Entscheidung trägt:**
> ```
> python3 analysen/finanzierungsoptionen.py --annahmen <Strategie>/annahmen.json
> ```
> Das Skript zieht dann die echten Werte und schreibt zu jedem Wert dazu, woher
> er kam. Die **Struktur** der Argumente unten ist von den Platzhaltern
> unabhängig; die **Beträge** sind es nicht.

## Kontext

Drei Ideen, alle mit demselben Ziel: mehr Finanzierungsspielraum, ohne mehr
Eigenkapital einzubringen.

1. **Nachbeleihung**, wenn der Wert steigt und die Mieten den Kapitaldienst tragen
2. **Verkäuferdarlehen** von Stephan
3. **WEG-Teilung**, um über die Summe der Einzelwerte mehr finanzieren zu können

## Der Befund, der alle drei rahmt

Vor der Einzelbewertung die Ausgangslage, weil sie jede der drei Optionen
anders aussehen lässt als gedacht:

| Position | Betrag | Herkunft |
|---|---|---|
| Kaufpreis | 740.000 € | belegt, `CLAUDE.md` Zielpreis |
| Kaufnebenkosten 8,5 % | 62.900 € | GrESt NRW 6,5 % + Notar 1,5 % + Grundbuch 0,5 %, ohne Makler (Platzhalter) |
| Gesamtinvestition | 802.900 € | gerechnet |
| − Eigenkapital | 120.000 € | belegt, `CLAUDE.md` |
| **= Darlehensbedarf** | **682.900 €** | gerechnet |

Und jetzt die Zeile, auf die es ankommt:

| | |
|---|---|
| Eigenkapital, das die **Nebenkosten** deckt | 62.900 € |
| Eigenkapital, das als **echte Anzahlung** auf den Kaufpreis wirkt | **57.100 €** |

Von den 120.000 € kommen also rund 57.000 € im Objekt an. Der Rest ist beim
Notar und beim Finanzamt und taucht in keiner Bewertung je wieder auf.

Daraus folgt der Beleihungsauslauf:

| Bezugsgröße | Auslauf |
|---|---|
| auf den **Kaufpreis** | 92,3 % |
| auf den **Beleihungswert** (Kaufpreis − 10 % Sicherheitsabschlag, Platzhalter) | **102,5 %** |

**Das Darlehen liegt über dem Beleihungswert.** Nicht bei 95 %, sondern
darüber. Das ist der Ausgangspunkt, von dem aus alle drei Optionen zu beurteilen
sind — und es dreht die Bewertung von Option 1 und Option 3 um.

> [!note] Vorab zu klären, weil es über 100.000 € ausmacht
> „95 % Beleihungsauslauf" heißt je nach Bezugsgröße etwas völlig anderes:
>
> | Sicherheitsabschlag der Bank | Beleihungswert | 95 % davon | = % des Kaufpreises |
> |---|---|---|---|
> | 0 % | 740.000 € | 703.000 € | 95,0 % |
> | 10 % | 666.000 € | 632.700 € | 85,5 % |
> | 15 % | 629.000 € | 597.550 € | 80,8 % |
>
> Frag die Bank, **worauf** sich ihre Prozentzahl bezieht und **wie hoch ihr
> Sicherheitsabschlag** ist, bevor du mit 95 % planst. Das ist eine
> Ein-Satz-Frage mit sechsstelliger Wirkung.

## Option 1 — Nachbeleihung

### Wie sie gedacht ist

Wert steigt (durch Sanierung oder Markt), Bank bewertet neu, die Differenz
zwischen neuem Beleihungswert und Restschuld wird als weiteres Darlehen
ausgezahlt — für die Entwicklung des Objekts oder als Eigenkapital für das
nächste.

Der Mechanismus ist real. Er ist nur langsamer und an eine engere Bedingung
geknüpft, als es zunächst aussieht.

### Wann überhaupt Spielraum entsteht

Spielraum bei 90 % Zielauslauf, in Euro (negativ = keiner):

| Jahr | Restschuld | Wert unverändert | Wert +10 % | Wert +20 % |
|---|---|---|---|---|
| 3 | 639.572 € | −40.172 € | +19.768 € | +79.708 € |
| 5 | 607.822 € | −8.422 € | +51.518 € | +111.458 € |
| 7 | 573.569 € | +25.831 € | +85.771 € | +145.711 € |
| 10 | 517.061 € | +82.339 € | +142.279 € | +202.219 € |

Ohne Wertzuwachs dauert es **rund 5,6 Jahre**, bis die Restschuld überhaupt auf
90 % des Beleihungswerts gefallen ist. Vorher ist Nachbeleihung kein Thema,
sondern eine Absage. Das liegt nicht am Objekt, sondern an den 62.900 €
Nebenkosten, die nie beleihbar waren.

### Der Test, auf den es wirklich ankommt

Das ist der Punkt, der in der ursprünglichen Überlegung fehlt:

> **Eine finanzierte Maßnahme verbessert den Beleihungsauslauf nur, wenn sie den
> Beleihungswert um mehr hebt, als sie die Schuld erhöht.**

Wenn du 100.000 € Wärmepumpe über die Bank finanzierst und der Beleihungswert
steigt um 60.000 €, hast du deinen Nachbeleihungsspielraum **verbraucht**, nicht
geschaffen. Die Sanierung zahlt sich dann energetisch und beim späteren
Verkaufspreis aus — aber nicht in der Bankbilanz.

Und bei einem vermieteten Mehrfamilienhaus bewertet die Bank im
**Ertragswertverfahren**. Der Ertragswert hängt an der nachhaltig erzielbaren
Miete, nicht an dem, was die Maßnahme gekostet hat. Wieviel Mehrmiete es
bräuchte, damit die Maßnahme sich im Beleihungswert überhaupt selbst trägt:

| Maßnahme | Zuschuss | Mehrschuld | nötige Mehrmiete dauerhaft |
|---|---|---|---|
| 30.000 € | 0 % | 30.000 € | 187 €/Monat |
| 60.000 € | 0 % | 60.000 € | 374 €/Monat |
| 100.000 € | 0 % | 100.000 € | **623 €/Monat** |
| 100.000 € | 50 % | 50.000 € | 311 €/Monat |
| 150.000 € | 0 % | 150.000 € | 934 €/Monat |
| 150.000 € | 50 % | 75.000 € | 467 €/Monat |

*(Vervielfältiger 17,16 bei 5,0 % Kapitalisierung und 40 Jahren
Restnutzungsdauer, 22 % Bewirtschaftungskosten — alles Platzhalter, siehe
Warnung oben.)*

Zwei Dinge fallen daran auf:

1. **623 €/Monat Mehrmiete** für eine 100.000-€-Wärmepumpe bekommt man in
   Nettersheim nicht. Energetische Sanierung trägt sich im Ertragswert
   **nicht selbst**.
2. **Die Förderung ist der Hebel, der das dreht.** Ein Zuschuss senkt die
   Schuld, ohne den Wert zu senken — er halbiert die nötige Mehrmiete
   ungefähr proportional. Das ist ein zusätzliches, von der Rendite
   unabhängiges Argument für die bereits getroffene Entscheidung, die
   Maßnahmen gebündelt über einen Förderantrag zu fahren.

### Was daraus für heute folgt

Der wichtigste Punkt bei dieser Option ist **nichts, was man später tut,
sondern etwas, das man jetzt beim Notar richtig machen muss**:

- **Grundschuldhöhe.** Die Grundschuld kann höher bestellt werden als das
  Darlehen. Wird später aufgestockt, valutiert die vorhandene Grundschuld
  einfach weiter — ohne neuen Notartermin und ohne neue Grundbuchkosten. Wird
  sie zu knapp bestellt, kostet jede spätere Aufstockung Gebühren auf den
  Aufstockungsbetrag und einen Termin.
  *Kehrseite:* Eine übervalutierende Grundschuld bleibt als Sicherheit bei
  dieser Bank und macht einen späteren Bankwechsel zäher. Das ist ein
  Abwägungspunkt, keine eindeutige Empfehlung — aber er gehört **vor** den
  Notartermin, nicht danach.
- **Zweckerklärung.** Eng (sichert nur dieses Darlehen) oder weit (sichert alle
  Ansprüche der Bank)? Für eine geplante Nachbeleihung ist die weite bequemer,
  für die Verhandlungsposition gegenüber der Bank die enge besser.
- **Nachbeleihungs- und Sondertilgungsrechte** gleich im Darlehensvertrag
  festhalten, statt später darum zu bitten.

## Option 2 — Verkäuferdarlehen

### Was es wirklich leistet

Der naheliegende Gedanke ist „geringerer Kapitaldienst". Das ist ein Trugschluss,
wenn das Darlehen endfällig ist — dann ist die Tilgung gestundet, nicht gespart.
Die Gegenprobe über 10 Jahre, gezahlte Raten plus verbleibende Restschuld:

| Variante | Zahlung 10 J | Restschuld | Summe |
|---|---|---|---|
| ohne Verkäuferdarlehen | 396.082 € | 517.061 € | 913.143 € |
| 100.000 €, endfällig | 378.082 € | 541.345 € | **919.427 €** |
| 100.000 €, mit 2 % Tilgung | 398.082 € | 516.804 € | 914.886 € |

Der niedrigere Kapitaldienst der endfälligen Variante (−18.000 € über 10 Jahre)
wird durch die höhere Restschuld mehr als aufgezehrt. *(Diese Gegenprobe rechnet
bewusst ohne Zinsstaffel, um den reinen Stundungseffekt zu isolieren.)*

Der echte Vorteil liegt woanders: **Das Verkäuferdarlehen schiebt das
Bankdarlehen in eine günstigere Zinsscheibe.**

| Verkäuferdarlehen | Bankdarlehen | Auslauf auf BW | Zins | Zins gesamt p.a. | ggü. ohne |
|---|---|---|---|---|---|
| — | 682.900 € | 102,5 % | 5,20 % | 35.511 € | — |
| 50.000 € | 632.900 € | 95,0 % | 4,80 % | 32.379 € | −3.132 € |
| 100.000 € | 582.900 € | 87,5 % | 3,95 % | 27.025 € | **−8.486 €** |
| 150.000 € | 532.900 € | 80,0 % | 3,95 % | 27.050 € | −8.461 € |

*(Zinsstaffel = Platzhalter. Die echten Aufschläge deiner Bank entscheiden hier
alles — erfrag sie als Staffel, nicht als einen Satz.)*

**Die Regel, die daraus folgt:** Ein Verkäuferdarlehen lohnt sich, solange sein
Zinssatz unter dem **Grenzzins der obersten Darlehensscheibe** liegt — nicht
unter dem Mischzins der Bank. Bei der obigen Staffel läge der Break-even je nach
Höhe bei 9,6 % bis 12,5 %. Das ist so hoch, dass fast jeder realistische
Verkäuferdarlehenszins sich rechnet. **Aber**: Dieser Break-even ist der Wert,
der am stärksten an der Platzhalter-Zinsstaffel hängt. Mit einer flachen Staffel
schrumpft er drastisch. Rechne ihn neu, sobald die echte Staffel vorliegt.

Auffällig ist außerdem, dass zwischen 100.000 € und 150.000 € kaum noch etwas
gewonnen wird — beide landen in derselben Zinsscheibe. **Die sinnvolle Höhe ist
genau der Betrag, der die nächste Scheibengrenze unterschreitet**, nicht der
höchstmögliche.

### Der Haken, an dem es scheitern kann

**Rechnet die Bank es als Eigenkapital oder als Fremdkapital?** Davon hängt die
ganze Option ab. Viele Banken behandeln ein Verkäuferdarlehen als Fremdkapital —
dann bleibt der Auslauf effektiv hoch, der Zinsvorteil entfällt, und der
Kapitaldienst ist trotzdem höher. Manche akzeptieren es als eigenkapitalähnlich,
wenn ein **qualifizierter Rangrücktritt** und Tilgungsaussetzung während der
Zinsbindung vereinbart sind.

**Diese Frage gehört an die Bank, bevor sie an Stephan gestellt wird.** Ein
Verkäuferdarlehen, das du verhandelst und das die Bank dann nicht anerkennt,
hat dir nichts gebracht und einen Verhandlungszug gekostet.

### Verhandlungsdynamik mit Stephan

Ein Verkäuferdarlehen ist kein reines Geschenk — es ist eine Gegenleistung, für
die er etwas will, typischerweise Preis. Die Rechnung dazu:

| Preisaufschlag | Kaufpreis | Mehr-Nebenkosten einmalig | Kapitaldienst ggü. Referenz |
|---|---|---|---|
| +20.000 € | 760.000 € | +1.700 € | −541 € p.a. |
| +40.000 € | 780.000 € | +3.400 € | +717 € p.a. |
| +60.000 € | 800.000 € | +5.100 € | +1.976 € p.a. |

*(mit 100.000 € Verkäuferdarlehen, endfällig, ohne Zinsstaffel)*

Bemerkenswert: Auch ein um 40.000 € höherer Preis kostet beim Kapitaldienst
zunächst wenig. **Das ist eine Falle.** Der höhere Preis erhöht dauerhaft die
Bemessungsgrundlage der Grunderwerbsteuer, die Restschuld und den Betrag, den du
beim Verkauf erst wieder verdienen musst. Der Zielpreis 740.000 € steht in
`Strategie-und-Verhandlung.md` — ein Verkäuferdarlehen ist kein Grund, ihn
aufzugeben, sondern ein Mittel, ihn zu **halten**.

Zwei weitere Punkte, die für die Konstruktion sprechen:

- Stephan bleibt **unbefristet als Mieter** im Haus. Er hat damit ohnehin ein
  fortdauerndes wirtschaftliches Interesse an dem Objekt und an dir als
  Vertragspartner — ein Verkäuferdarlehen ist für ihn weniger fremd als für
  einen Verkäufer, der auszieht.
- Umgekehrt entsteht eine **wechselseitige Abhängigkeit**: Er schuldet dir
  Miete, du schuldest ihm Zins und Tilgung. Das kann man als Risikodämpfer
  sehen. Eine förmliche **Verrechnungsabrede** würde ich trotzdem nicht
  vereinbaren — sie verkompliziert die steuerliche Erfassung beider Ströme
  und die Bank will Mieteingänge auf dem Konto sehen, nicht saldiert.

## Option 3 — WEG-Teilung

### Der Gedanke und wo er bricht

Der Gedanke stimmt als **Marktbeobachtung**: Die Summe der Einzelverkaufspreise
von Eigentumswohnungen liegt regelmäßig über dem Preis desselben Hauses als
Ganzes. Das ist der Aufteilungsgewinn, und davon leben ganze Geschäftsmodelle.

Die Rechnung dazu, rein mechanisch:

| Aufteilungsaufschlag | Beleihungswert in Summe | 95 % davon | Mehrvolumen | nach 15.000 € Teilungskosten |
|---|---|---|---|---|
| 0 % | 666.000 € | 632.700 € | 0 € | −15.000 € |
| 10 % | 732.600 € | 695.970 € | 63.270 € | 48.270 € |
| 20 % | 799.200 € | 759.240 € | 126.540 € | 111.540 € |

Der Bruch liegt in der ersten Spalte. **Der Aufteilungsaufschlag ist eine
Marktgröße beim Einzelverkauf an Selbstnutzer — kein Bewertungsparameter der
Bank.** Solange du alle Einheiten hältst und vermietest, bewertet die Bank
weiterhin im Ertragswertverfahren über die Mieten. Die Mieten ändern sich durch
eine Teilungserklärung um exakt null Euro.

Es ist möglich, dass eine Bank nach Teilung höher ansetzt, weil die einzelne
Einheit besser verwertbar ist. Es ist genauso möglich, dass sie einen
**Paketabschlag** macht, weil du alle hältst. **Diese Frage entscheidet die
gesamte Option, und sie ist mit einem Anruf zu klären, bevor irgendein Geld für
Aufteilungspläne ausgegeben wird.**

### Die praktische Hürde vor allen anderen

**Abgeschlossenheit.** Für eine Teilung nach § 8 WEG braucht es eine
Abgeschlossenheitsbescheinigung: eigene abschließbare Zugänge, klar getrennte
Einheiten. Bei einem gewachsenen Bestand aus Altbestand und Anbau ist das oft
**baulich nicht gegeben** — gemeinsame Zugänge, eine durchgehende Versorgung,
Räume, die sich nicht eindeutig zuordnen lassen.

Das ist keine Rechtsfrage, sondern eine Frage an den Grundriss. Sie ist vor
allen anderen zu beantworten, weil sie die Option ersatzlos beenden kann.

### Was zusätzlich dagegen spricht

- **Zentrale Wärmepumpe für beide Hausteile wird Gemeinschaftseigentum.** Solange
  dir alles gehört, ist das unproblematisch. Ab der ersten verkauften Einheit
  sind Heizung, Dach und Fassade Beschlusssache einer Eigentümergemeinschaft.
  Genau die Maßnahmen, die in `Reihenfolge-der-Optimierungen.md` als gebündelter
  Plan stehen, würden dann von fremden Miteigentümern mitbestimmt.
- **Die Option ist nicht umkehrbar.** Eine Teilung rückgängig zu machen, ist
  aufwendig; die WEG-Struktur bleibt im Grundbuch.
- **Steuerlich ist sie der riskanteste der drei Wege** — Stichwort gewerblicher
  Grundstückshandel, wenn später mehrere Einheiten verkauft werden. Das steht im
  Rechtsteil unten.

## Wie die drei zusammenhängen

Die drei Optionen sind keine Alternativen — sie wirken zu **verschiedenen
Zeitpunkten** und schließen sich nicht aus.

| | wirkt | Voraussetzung | verfällt, wenn |
|---|---|---|---|
| **Option 2** Verkäuferdarlehen | beim Kauf | Zusage der Bank **und** Stephans Bereitschaft | der Kaufvertrag unterschrieben ist |
| **Option 1** Nachbeleihung | ab ca. Jahr 5–6 ohne Wertzuwachs, früher mit | Grundschuld heute richtig bestellt | nie — aber die Vorarbeit dafür verfällt beim Notartermin |
| **Option 3** WEG-Teilung | frühestens nach 1–2 Jahren | bauliche Abgeschlossenheit; Bank rechnet den Aufschlag an | nie |

Drei Beobachtungen zum Zusammenspiel:

1. **Option 1 und 3 zielen auf dasselbe** — mehr Kreditvolumen aus einem höheren
   Wert. Option 3 ist der teurere, langsamere und steuerlich riskantere Weg
   dorthin. Wenn Option 1 den Spielraum liefert, braucht es Option 3 nicht.
2. **Nur Option 2 ist zeitkritisch.** Sie ist die einzige, die man durch
   Nichtstun verliert, und die einzige, die die Verhandlung mit Stephan berührt.
3. **Option 2 verbessert die Startposition für Option 1.** Ein niedrigerer
   Auslauf beim Kauf bedeutet, dass der Nachbeleihungsspielraum Jahre früher
   entsteht — der Effekt von Block A im Rechenskript.

Und ein Punkt, der in keiner der drei Ideen steckt, aber danebengehört:
**Beleihungsauslauf ist nicht dasselbe wie Tragfähigkeit.** Mehr Volumen zu
95 % ist nur dann gut, wenn der Cashflow es trägt. Bei der Platzhalter-Zinsstaffel
kostet der Sprung von 80 % auf 95 % Auslauf rund **4.780 € Zinsen mehr pro
Jahr** auf dasselbe Darlehen. Die Frage „wieviel kann ich finanzieren" ist nicht
die Frage „wieviel sollte ich finanzieren".

## Was ich daraus empfehle

**Jetzt, vor dem Notartermin — kostet nichts, verfällt sonst:**

1. Bank fragen: Sicherheitsabschlag, Bezugsgröße der Auslaufquote, und die
   **Zinsstaffel** nach Auslauf. Drei Fragen, sechsstellige Wirkung.
2. Bank fragen: Wird ein Verkäuferdarlehen mit qualifiziertem Rangrücktritt als
   eigenkapitalähnlich anerkannt? **Vor** dem Gespräch mit Stephan.
3. Grundschuldhöhe, Zweckerklärung und Nachbeleihungsrecht bewusst entscheiden
   und in den Darlehensvertrag schreiben.

**In der Verhandlung mit Stephan:**

4. Verkäuferdarlehen als Mittel einsetzen, den Zielpreis von 740.000 € zu
   **halten** — nicht als Gegenleistung für einen höheren Preis.
5. Höhe so wählen, dass das Bankdarlehen die nächste Zinsscheibengrenze
   unterschreitet. Mehr bringt nichts.

**Später, in dieser Reihenfolge:**

6. Nachbeleihung als geplanten Schritt vorsehen, aber erst ab dem Zeitpunkt, zu
   dem die Rechnung sie trägt. Vorher ist jeder Antrag eine Absage.
7. WEG-Teilung **zurückstellen**, bis zwei Fragen beantwortet sind: Ist die
   Abgeschlossenheit baulich überhaupt herstellbar, und rechnet die Bank den
   Aufteilungsaufschlag im Beleihungswert an? Solange beide offen sind, ist
   jede Ausgabe dafür verfrüht.

## Offene Fragen

### An die Bank — vor dem Notartermin

- [ ] Welchen **Sicherheitsabschlag** setzt ihr zwischen Kaufpreis und
      Beleihungswert an?
- [ ] Bezieht sich eure Auslaufquote auf den **Beleihungswert** oder auf den
      **Kaufpreis**?
- [ ] Wie sieht die **Zinsstaffel** nach Beleihungsauslauf aus? (Als Staffel,
      nicht als ein Satz — die Scheibengrenzen bestimmen die sinnvolle Höhe
      eines Verkäuferdarlehens.)
- [ ] Wird ein **Verkäuferdarlehen** mit qualifiziertem Rangrücktritt als
      eigenkapitalähnlich anerkannt, oder als Fremdkapital gerechnet?
- [ ] Welche **Grundschuldhöhe** empfehlt ihr im Hinblick auf eine spätere
      Aufstockung, und welche Kosten entstehen bei einer späteren Erhöhung?
- [ ] **Nachbeleihungsrecht** und Sondertilgungsrechte: was ist vertraglich
      zusicherbar?
- [ ] Nach welchem Verfahren bewertet ihr — **Ertragswert**, Sachwert oder
      Mischung? Mit welchem Kapitalisierungszinssatz und welcher
      Restnutzungsdauer?
- [ ] Würdet ihr nach einer **WEG-Teilung** die Summe der Einzelwerte ansetzen,
      oder bliebe es beim Ertragswert des Gesamtobjekts (ggf. mit Paketabschlag)?
- [ ] Ab welcher Darlehenshöhe verlangt ihr ein **Vollgutachten**, und was
      kostet eine spätere Neubewertung?

### An den Architekten oder Vermesser

- [ ] Ist **Abgeschlossenheit** für Altbestand und Anbau baulich herstellbar —
      und wenn ja, mit welchem Umbauaufwand?

### An Stephan — erst nach der Bankauskunft

- [ ] Wäre ein Verkäuferdarlehen für dich grundsätzlich denkbar, und in welcher
      Größenordnung?
- [ ] Welche Laufzeit und welche Verzinsung stellst du dir vor?

### Für den Vault noch zu ergänzen

- [ ] **Nettokaltmiete** — ohne sie ist keine Aussage zum Ertragswert und damit
      zu Option 1 belastbar. Das ist die wichtigste fehlende Zahl in dieser
      ganzen Analyse.
- [ ] Tatsächliche Kaufnebenkostenstruktur: fällt Maklerprovision an?
- [ ] Aktuelles Zinsangebot und Zinsbindung

## Annahmen, auf denen diese Analyse beruht

**Belegt** (aus `CLAUDE.md`, Stand der Entscheidungen):

- Zielpreis 740.000 €, Obergrenze 800.000 €
- Eigenkapital 120.000 €
- Erwerb privat; Verkäufer bleiben unbefristet als Mieter, Indexmiete
- Ein Förderantrag für beide Hausteile, Maßnahmen gebündelt nach dem Auszug

**Referenz** (aus dem Skill, mit Stand und Prüfvorbehalt):

- Grunderwerbsteuer NRW 6,5 % — Stand Mai 2026, vor Verwendung prüfen
- Notar ca. 1,5 %, Grundbuch ca. 0,5 % — Planungsgrößen

**Platzhalter** — durchweg nicht belegt, nur zur Größenordnung, **vor jeder
Entscheidung durch echte Werte zu ersetzen**:

| Größe | Platzhalter | woher der echte Wert kommt |
|---|---|---|
| Sollzins | 3,8 % | Bankangebot |
| Anfangstilgung | 2,0 % | Entscheidung |
| Zinsbindung | 10 Jahre | Entscheidung |
| Maklerprovision | 0 % | Kaufvertragsentwurf |
| Sicherheitsabschlag Beleihungswert | 10 % | Bank |
| Zinsstaffel nach Auslauf | 3,50 %–5,20 % | Bank |
| Kapitalisierungszinssatz | 5,0 % | Bank / Gutachten |
| Restnutzungsdauer | 40 Jahre | Gutachten |
| Bewirtschaftungskosten | 22 % | Gutachten |
| Zins Verkäuferdarlehen | 4,0 % | Verhandlung |
| Teilungskosten | 15.000 € | Angebot Architekt/Notar |
| **Nettokaltmiete** | **fehlt ganz** | **Mietverträge** |

## Was diese Analyse umkehren würde

- Die Bank rechnet mit **deutlich geringerem Sicherheitsabschlag** als 10 % —
  dann ist der Ausgangsauslauf niedriger und Option 1 rückt näher.
- Die Bank rechnet ein **Verkäuferdarlehen nicht als eigenkapitalähnlich** —
  dann fällt der Hauptvorteil von Option 2 weg und übrig bleibt eine reine
  Stundung.
- Die Bank sagt zu, nach einer Teilung die **Summe der Einzelwerte** anzusetzen
  — dann wird Option 3 von der Außenseiterin zum ernsthaften Kandidaten, und
  die steuerliche Frage wird zur entscheidenden.
- Die **Abgeschlossenheit ist baulich nicht herstellbar** — dann entfällt
  Option 3 vollständig, ohne weitere Prüfung.
- Die **Nettokaltmiete** liegt deutlich über dem, was für den Kapitaldienst
  nötig ist — dann verschiebt sich das ganze Bild zugunsten von Option 1.

