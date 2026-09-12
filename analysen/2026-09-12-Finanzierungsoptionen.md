---
type: entscheidung
object: Auf Helwen 8
date: 2026-09-12
decision: offen
review_on: 2026-10-15
---

# Drei Finanzierungsoptionen — Nachbeleihung, Verkäuferdarlehen, WEG-Teilung

> [!warning] Zahlenstand
> Diese Analyse entstand **ohne Zugriff auf den Vault** und damit ohne
> `annahmen.json` und `modell.py`. Belegt sind die Werte aus `CLAUDE.md` und
> aus den Nutzerfakten in `.claude/agents/widerspruchs-pruefer.md`. Die
> Bankkonditionen (Sicherheitsabschlag, Zinsstaffel unterhalb des realen
> Angebots) und die Bewertungsparameter sind Annahmen.
>
> **Nicht nur die Beträge hängen daran, sondern auch Bewertungen.** Der
> Befund „das Darlehen liegt über dem Beleihungswert" folgt allein aus dem
> angenommenen Sicherheitsabschlag von 10 %. Platzhalterunabhängig sind nur
> die *Fragen* an die Bank, nicht die *Schlüsse*.
>
> ```
> python3 analysen/finanzierungsoptionen.py --annahmen <Strategie>/annahmen.json
> ```

> [!danger] Korrekturen gegenüber der ersten Fassung vom selben Tag
> Die erste Fassung enthielt vier Fehler, die die Prüfagenten gefunden haben.
> Sie stehen hier, statt stillschweigend ersetzt zu werden:
>
> | vorher | jetzt | warum |
> |---|---|---|
> | Zins 3,8 %, Tilgung 2 %, Zinsbindung 10 Jahre | **Volltilger 34 Jahre zu 5,45 %** | Das ist ein reales Angebot der Wüstenrot und ein mitgeteilter Nutzerfakt. Die Kernzahl „Spielraum ab 5,6 Jahren" war dadurch falsch — richtig sind **9,4 Jahre**. Derselbe Fehler (10-Jahres-Zinsbindung unterstellt) steht in `widerspruchs-pruefer.md` bereits als vorgekommen protokolliert. |
> | „Maklerprovision — fällt sie an?" als offene Frage | **Privatverkauf ohne Makler**, belegt | Ebenfalls ein bereits mitgeteilter Nutzerfakt und ein protokollierter Wiederholungsfehler. |
> | WEG-Mehrvolumen ohne Abzug der Restschuld | **Restschuld abgezogen** | Jede Zeile war um rund 52.000 € überzeichnet. Bei 10 % Aufteilungsaufschlag kippt das Ergebnis von „+48.270 €" auf **−3.637 €**. |
> | Vermutung: Indexmiete schließt § 559 BGB aus | **teilweise falsch** | § 557b Abs. 2 S. 2 BGB enthält eine Rückausnahme für den Heizungseinbau. Details unten — das Ergebnis bleibt ernüchternd, aber aus einem anderen Grund. |
>
> Zusätzlich behoben: zwei Fehler im Rechenskript, darunter einer, der still
> einen falschen Zinssatz als „belegt" ausgewiesen hätte.

## Kontext

Drei Ideen mit demselben Ziel: mehr Finanzierungsspielraum ohne mehr
Eigenkapital.

1. **Nachbeleihung**, wenn der Wert steigt und die Mieten den Kapitaldienst tragen
2. **Verkäuferdarlehen** von Stephan
3. **WEG-Teilung**, um über die Summe der Einzelwerte mehr finanzieren zu können

## Der Befund, der alle drei rahmt

| Position | Betrag |
|---|---|
| Kaufpreis | 740.000 € |
| Kaufnebenkosten 8,5 % (GrESt 6,5 % + Notar 1,5 % + Grundbuch 0,5 %, kein Makler) | 62.900 € |
| Grundschuldbestellung 0,25 % | 1.707 € |
| **Nebenkosten gesamt** | **64.607 €** |
| Gesamtinvestition | 804.607 € |
| − Eigenkapital | 120.000 € |
| **= Darlehensbedarf** | **684.607 €** |

Und die Zeile, auf die es ankommt:

| | |
|---|---|
| Eigenkapital, das die Nebenkosten deckt | 64.607 € |
| Eigenkapital, das als **echte Anzahlung** wirkt | **55.393 €** |

Von 120.000 € kommen rund 55.000 € im Objekt an. Der Rest ist beim Notar und
beim Finanzamt und taucht in keiner Bewertung wieder auf.

| Bezugsgröße | Auslauf |
|---|---|
| auf den Kaufpreis | 92,51 % |
| auf den Beleihungswert (Kaufpreis − 10 % Sicherheitsabschlag, **Annahme**) | **102,79 %** |

Der Kapitaldienst beim realen Angebot:

| Volltilger 34 Jahre zu 5,45 % | |
|---|---|
| Rate | 3.690 €/Monat |
| Annuität | 44.282 € p.a. |
| Zins Jahr 1 | 37.311 € |
| **Anfangstilgung** | **1,02 %** |

Die niedrige Anfangstilgung ist der Preis der langen Laufzeit bei hohem Zins.
Sie ist der Grund, warum Option 1 so viel später greift als gedacht. Umgekehrt
gilt: Ein Volltilger über 34 Jahre hat **kein Anschlusszinsrisiko** — der
Zinsstresstest, den die Projektreferenz sonst zwingend vorschreibt, entfällt
hier zu Recht.

> [!note] Drei Fragen an die Bank, die über 100.000 € entscheiden
> „95 % Beleihungsauslauf" heißt bei 0 % Sicherheitsabschlag 703.000 €, bei
> 10 % nur 632.700 €, bei 15 % noch 597.550 €.
>
> 1. Worauf bezieht sich eure Auslaufquote — Kaufpreis oder Beleihungswert?
> 2. Wie hoch ist euer Sicherheitsabschlag?
> 3. Nach welchem Regelwerk bewertet ihr? **Die BelWertV gilt rechtlich nur
>    für Pfandbriefbanken** (§ 1 BelWertV); andere Institute wenden sie
>    freiwillig oder gar nicht an. Ohne diese Antwort ist der Beleihungsauslauf
>    nicht prognostizierbar.
>
> Und ein Punkt, der jetzt schon feststeht: Bei 684.607 € Darlehen liegt ihr
> **über der Kleindarlehensgrenze von 600.000 €** (§ 24 BelWertV). Es braucht
> ein **Vollgutachten**, nicht die vereinfachte Wertermittlung. Kosten und
> Zeitbedarf gehören in die Terminplanung.

## Option 1 — Nachbeleihung

### Wann Spielraum entsteht

Spielraum bei 90 % Zielauslauf, Volltilger 34 J zu 5,45 % (negativ = keiner):

| Jahr | Restschuld | Wert unverändert | Wert +10 % | Wert +20 % |
|---|---|---|---|---|
| 3 | 661.943 € | −62.543 € | −2.603 € | +57.337 € |
| 5 | 644.644 € | −45.244 € | +14.696 € | +74.636 € |
| 7 | 625.357 € | −25.957 € | +33.983 € | +93.923 € |
| 10 | 592.194 € | +7.206 € | +67.146 € | +127.086 € |
| 15 | 523.357 € | +76.043 € | +135.983 € | +195.923 € |

**Ohne Wertzuwachs dauert es 9,4 Jahre**, bis die Restschuld auf 90 % des
Beleihungswerts gefallen ist. Vorher ist Nachbeleihung kein Thema. Selbst bei
10 % Wertzuwachs entsteht erst nach fünf Jahren nennenswerter Spielraum.

### Der Test, auf den es ankommt

> Eine finanzierte Maßnahme verbessert den Auslauf nur, wenn sie den
> Beleihungswert um mehr hebt, als sie die Schuld erhöht.

Bei einem vermieteten Mehrfamilienhaus bewertet die Bank im Ertragswertverfahren
— über die Miete, nicht über die Baukosten. Was an Mehrmiete nötig *wäre*:

| Maßnahme | Zuschuss | Mehrschuld | nötige Mehrmiete (Deckung) | (Quote) |
|---|---|---|---|---|
| 30.000 € | 0 % | 30.000 € | 216 €/Monat | 211 €/Monat |
| 60.000 € | 0 % | 60.000 € | 433 €/Monat | 421 €/Monat |
| 100.000 € | 0 % | 100.000 € | **721 €/Monat** | 702 €/Monat |
| 100.000 € | 30 % | 70.000 € | 505 €/Monat | 491 €/Monat |
| 150.000 € | 30 % | 105.000 € | 757 €/Monat | 737 €/Monat |

*(Kapitalisierung 5,5 % nach § 12 Abs. 4 BelWertV, Restnutzungsdauer 40 Jahre,
Bewirtschaftungskosten 20 % — § 11 Abs. 2 BelWertV verlangt mindestens 15 %.
Sicherheitsabschlag auf die Maßnahme genauso wie auf den Bestand. 30 % ist der
BEG-Fördersatz für Kapitalanleger, siehe unten.)*

Das sind **Schwellenrechnungen**: so viel wäre nötig. Ob eine solche Miete
erzielbar ist, sagt diese Rechnung nicht — dafür fehlt die Marktmiete, und eine
Marktmiete ohne Quelle gehört nach Regel 4 nicht in dieses Dokument.

### Und hier wird es rechtlich eng

Die Mehrmiete müsste ja erst einmal durchsetzbar sein. Für die Einheit, in der
Stephan wohnt, gilt die **Indexmiete**. Was das bedeutet:

**§ 557b Abs. 2 BGB** (Fassung seit 01.01.2024, durch das GModG nicht geändert):

- **§ 558 BGB (Erhöhung auf die ortsübliche Vergleichsmiete) ist vollständig
  ausgeschlossen.**
- **§ 559 / § 559e BGB** (Modernisierungsumlage) nur bei Maßnahmen aufgrund von
  Umständen, die der Vermieter nicht zu vertreten hat — **mit einer Rückausnahme
  für Maßnahmen nach § 555b Nr. 1a BGB (Heizungseinbau)**.

Meine ursprüngliche Vermutung, die Indexmiete schließe die Modernisierungsumlage
aus, war damit **für den Heizungstausch falsch**. Die Wärmepumpe ist über
§ 555b Nr. 1a umlagefähig, auch bei Indexmiete.

Nur hilft das wenig, und zwar wegen der Kappung:

- **§ 559e BGB** ist für den geförderten Heizungstausch die speziellere Norm:
  10 % der Kosten **abzüglich der Drittmittel**, gekappt bei **0,50 €/m² in
  sechs Jahren**.
- **§ 559a Abs. 1 BGB**: Der Zuschuss wird von der Kostenbasis abgezogen, bevor
  der Prozentsatz greift.

**0,50 €/m² pro Monat** ist bei realistischen Wohnungsgrößen ein zweistelliger
Monatsbetrag — gegen die 216 bis 721 € aus der Tabelle oben. Der Ertragswert-Hebel
über eine Mieterhöhung ist damit für Stephans Einheit praktisch tot.

Und für alles jenseits der Heizungsanlage — Dämmung, Fußbodenheizung, PV —
greift die Rückausnahme nicht: Dort sperrt die Indexmiete die Umlage ganz.
Ob der **Heizkörpertausch** noch zur Heizungsanlage im Sinne von § 555b Nr. 1a
zählt, ist die offene Frage, an der ein relevanter Teil der Sanierungskosten
hängt. Das gehört zum Fachanwalt.

> [!important] Was daraus folgt
> Rechnet die Wärmepumpe **nicht über eine Mieterhöhung** gegen, sondern über
> den Zuschuss und die Betriebskostenersparnis. Und erwartet von der
> energetischen Sanierung **keinen Beleihungswertzuwachs**, der die
> Finanzierung trägt.

### Ein Punkt, der leicht übersehen wird

**§ 10 Abs. 1 BelWertV**: Liegt die nachhaltig erzielbare Miete über der
vertraglich vereinbarten, ist im Regelfall die **vertraglich vereinbarte**
anzusetzen.

Die Miete, die ihr mit Stephan vereinbart, ist damit **nicht nur eine
Cashflow-Frage, sondern eine Finanzierungsfrage**. Eine freundschaftlich
niedrige Anfangsmiete drückt den Beleihungswert, hebt den Beleihungsauslauf und
verteuert den Zins — und zwar dauerhaft, weil die Indexmiete nur dem
Verbraucherpreisindex folgt. Das gehört durchgerechnet, **bevor** der
Mietvertrag verhandelt wird.

### Was daraus für heute folgt

Das Wichtigste an dieser Option passiert vor dem Notartermin:

- **Grundschuldhöhe.** Höher bestellen als das Darlehen, dann valutiert sie bei
  einer späteren Aufstockung ohne neuen Notartermin weiter. Kehrseite: Die
  übervalutierende Grundschuld bleibt Sicherheit dieser Bank und macht einen
  Wechsel zäher. Abwägung, keine eindeutige Empfehlung — aber sie gehört
  **vor** den Termin.
- **Zweckerklärung** eng oder weit.
- **Nachbeleihungs- und Sondertilgungsrechte** in den Darlehensvertrag.

## Option 2 — Verkäuferdarlehen

### Was es wirklich leistet

Der niedrigere Kapitaldienst eines endfälligen Verkäuferdarlehens ist
**gestundet, nicht gespart**:

| Variante | Zahlung 10 J | Restschuld | Summe | Barwert |
|---|---|---|---|---|
| ohne Verkäuferdarlehen | 442.822 € | 592.194 € | 1.035.016 € | 682.921 € |
| 100.000 €, endfällig | 418.140 € | 605.693 € | 1.023.832 € | 672.211 € |

*(ohne Zinsstaffel, um den Stundungseffekt zu isolieren; Barwert mit 5,45 %
diskontiert, weil nominale Zehnjahressummen den Effekt überzeichnen)*

Der echte Vorteil liegt darin, dass das Verkäuferdarlehen das Bankdarlehen in
eine **günstigere Zinsscheibe** schiebt — und zwar genau an den Scheibengrenzen:

| Grenze | max. Bankdarlehen | nötiges Verkäuferdarlehen | Zins | Zins gesamt p.a. | Ersparnis |
|---|---|---|---|---|---|
| 80 % | 532.800 € | 151.807 € | 4,15 % | 28.183 € | +9.128 € |
| 90 % | 599.400 € | 85.207 € | 4,55 % | 30.681 € | +6.630 € |
| 95 % | 632.700 € | 51.907 € | 4,95 % | 33.395 € | +3.916 € |
| 100 % | 666.000 € | 18.607 € | 5,25 % | 35.709 € | +1.602 € |

*(Die Zinsstaffel unterhalb des realen Angebots von 5,45 % ist eine Annahme.
Sie ist bei der Bank **als Staffel** zu erfragen — davon hängt diese ganze
Tabelle ab.)*

Zwei Konsequenzen:

1. Ein Verkäuferdarlehen lohnt sich, solange sein Zins unter dem **Grenzzins
   der obersten Darlehensscheibe** liegt — nicht unter dem Mischzins.
2. **Die Beträge sind spitz.** 51.907 € erreichen die 95-%-Scheibe, 51.800 €
   nicht. Ein paar hundert Euro zu wenig kosten die ganze Scheibe. Runde
   Verhandlungsbeträge sind hier teuer.

### Der Haken, an dem es scheitern kann

**Rechnet die Bank es als Eigenkapital oder als Fremdkapital?** Viele tun
Letzteres, dann entfällt der Zinsvorteil. Manche erkennen es bei
**qualifiziertem Rangrücktritt** und Tilgungsaussetzung als eigenkapitalähnlich
an. **Diese Frage gehört an die Bank, bevor sie an Stephan geht** — sonst
verbrennt ihr einen Verhandlungszug für nichts.

### Was steuerlich gilt

- **Grunderwerbsteuer fällt voll an.** Der gestundete Kaufpreisteil gehört zur
  Gegenleistung (§ 9 Abs. 1 Nr. 1 GrEStG). Ein Verkäuferdarlehen ist ein
  Liquiditäts-, kein Steuerinstrument.
- **Ein zinsloses Verkäuferdarlehen ist steuerlich vermutlich stumm.** Der BFH
  hat am **24.03.2026 (VIII R 30/24)** seine bisherige Rechtsprechung
  aufgegeben: Bei zinsloser Stundung ist von einer unentgeltlichen Stundung
  auszugehen, § 12 Abs. 3 BewG ist eine Bewertungs-, keine
  Einkommensteuervorschrift. Kein Kapitalertrag bei Stephan — aber spiegelbildlich
  auch **kein Werbungskostenabzug bei euch**.
  **Zwei Vorbehalte:** Der entschiedene Fall betraf Angehörige, ihr steht im
  Fremdvergleich. Und ob die Finanzverwaltung dem folgt oder mit einem
  Nichtanwendungserlass reagiert, ist offen.
- **Ein verzinsliches Verkäuferdarlehen** bringt den Zinsabzug nach
  § 9 Abs. 1 S. 3 Nr. 1 EStG — aber nur bei sauberer Zuordnung. Nach
  BFH IX R 44/95 u. a. und IX R 35/08 muss die **Kaufpreisaufteilung in die
  notarielle Urkunde** und die Darlehensvaluta getrennt und unvermischt fließen.
  **Das lässt sich nach dem Notartermin nicht mehr reparieren.**
- **Ob eine unverzinsliche Stundung die GrESt-Bemessungsgrundlage senkt**
  (Abzinsung nach § 12 Abs. 3 BewG), war nicht abschließend klärbar. Nicht als
  Ersparnis einplanen ohne verbindliche Auskunft.

### Verhandlungsdynamik mit Stephan

Stephan wird für ein Verkäuferdarlehen etwas wollen, typischerweise Preis:

| Preisaufschlag | Kaufpreis | Mehr-Nebenkosten | Kapitaldienst p.a. | Differenz |
|---|---|---|---|---|
| +20.000 € | 760.000 € | 1.750 € | 43.230 € | +1.416 € |
| +40.000 € | 780.000 € | 3.500 € | 44.637 € | +2.823 € |
| +60.000 € | 800.000 € | 5.250 € | 46.044 € | +4.230 € |

*(verglichen mit demselben Kaufpreis **mit** demselben Verkäuferdarlehen — so
ist nur der Preiseffekt isoliert. 800.000 € ist die beschlossene **Obergrenze**,
keine Option unter dreien.)*

Der Zielpreis von 740.000 € steht in `Strategie-und-Verhandlung.md`. **Ein
Verkäuferdarlehen ist ein Mittel, ihn zu halten, nicht ein Grund, ihn
aufzugeben.**

Zwei Punkte für die Konstruktion: Stephan bleibt ohnehin als Mieter im Haus und
hat ein fortdauerndes Interesse am Objekt — ein Verkäuferdarlehen ist für ihn
weniger fremd als für einen Verkäufer, der auszieht. Eine förmliche
**Verrechnungsabrede** zwischen Miete und Zins würde ich trotzdem nicht
vereinbaren: Sie verkompliziert die steuerliche Erfassung, und die Bank will
Mieteingänge auf dem Konto sehen, nicht saldiert.

## Option 3 — WEG-Teilung

### Die Rechnung

| Aufteilungsaufschlag | Beleihungswert in Summe | 95 % davon | − Restschuld | nach 15.000 € Teilungskosten |
|---|---|---|---|---|
| 0 % | 666.000 € | 632.700 € | −51.907 € | −66.907 € |
| 5 % | 699.300 € | 664.335 € | −20.272 € | −35.272 € |
| 10 % | 732.600 € | 695.970 € | +11.363 € | **−3.637 €** |
| 15 % | 765.900 € | 727.605 € | +42.998 € | +27.998 € |
| 20 % | 799.200 € | 759.240 € | +74.633 € | +59.633 € |

**Erst ab rund 11 % Aufteilungsaufschlag trägt die Teilung ihre eigenen Kosten.**
Darunter ist sie ein Verlustgeschäft. (In der ersten Fassung fehlte der Abzug
der Restschuld — siehe Korrekturkasten oben.)

### Wo der Gedanke bricht

Drei Stellen, jede für sich ausreichend:

**1. Der Aufschlag ist ein Selbstnutzerpreis.** Er entsteht beim Einzelverkauf
an Leute, die selbst einziehen. Für die Einheit, in der **Stephan unbefristet
und unkündbar wohnt**, ist er nicht erzielbar — dort steht ein Abschlag. Die
Tabelle oben ist damit für den Altbestand eine Obergrenze, die nicht erreicht
wird.

**2. Die Bank muss den Aufschlag im Beleihungswert nachvollziehen.** Solange ihr
alle Einheiten haltet und vermietet, bewertet sie weiter über die Mieten — und
die ändern sich durch eine Teilungserklärung um null Euro. Möglich, dass eine
Bank höher ansetzt; genauso möglich, dass sie einen Paketabschlag macht.

**3. Abgeschlossenheit.** Eigene abschließbare Zugänge, klar getrennte
Einheiten. Bei einem gewachsenen Bestand aus Altbestand und Anbau oft baulich
nicht gegeben. Das ist eine Frage an den Grundriss, und sie kann die Option
ersatzlos beenden — **vor allen anderen zu klären, weil sie am billigsten zu
beantworten ist.**

### Was rechtlich gilt — teils besser, teils schlechter als erwartet

**Gute Nachrichten:**

- **§ 250 BauGB greift in Nettersheim nicht.** Die Norm gilt bundesrechtlich
  weiter (um fünf Jahre verlängert), wirkt aber nur über eine Landesverordnung
  — und **NRW hat keine Umwandlungsverordnung erlassen**. Die NRW-Verordnung
  nach § 201a BauGB begründet keinen Umwandlungsvorbehalt. (DNotI-Übersicht,
  Stand 20.01.2026: gelistet sind nur Bayern, Berlin, Hamburg, Hessen,
  Niedersachsen.) Vor dem Notartermin trotzdem den aktuellen Stand abfragen.
- **Die Teilung nach § 8 WEG löst keine Grunderwerbsteuer aus** — kein
  Rechtsträgerwechsel. Erst die spätere Veräußerung einzelner Einheiten.
- **Keine verlängerte Kündigungssperrfrist.** Die Mieterschutzverordnung NRW
  vom 28.01.2025 verlängert sie auf acht Jahre, aber nur in 57 Kommunen.
  **Nettersheim ist nicht dabei** — aus dem Kreis Euskirchen nur Weilerswist.
  Es gilt die gesetzliche Regelsperrfrist von drei Jahren (§ 577a BGB), und es
  gibt dort auch keine Mietpreisbremse.

**Schlechte Nachrichten:**

- **§ 577 BGB: Stephan bekommt ein Vorkaufsrecht.** Wird nach der Überlassung an
  den Mieter Wohnungseigentum begründet und die Einheit an einen Dritten
  verkauft, steht dem Mieter das Vorkaufsrecht zu. Genau eure Zeitfolge. Es
  greift nicht durch die Teilung selbst, sondern durch die Veräußerung — aber
  es begrenzt den Exit, auf dem die ganze Option beruht.
- **Gewerblicher Grundstückshandel — das größte Risiko.** Nach dem
  BMF-Schreiben vom 26.03.2004 (BStBl I S. 434) und BFH GrS 1/98 ist **jede
  WEG-Einheit ein eigenes Objekt**. Aus einem Mehrfamilienhaus werden durch die
  Teilung so viele Objekte, wie Einheiten entstehen. Mehr als drei davon
  innerhalb von fünf Jahren verkauft, und es wird gewerblicher
  Grundstückshandel. Die Aufteilung selbst ist bereits ein **Indiz** für
  Veräußerungsabsicht; die Gegenindizien müsst ihr liefern.

  Die Folgen treffen alle drei gleichzeitig: **Gewerbesteuer**,
  **Umlaufvermögen statt Anlagevermögen — also keine AfA**, und **§ 23 EStG
  wird gegenstandslos**, die Zehnjahresfrist schützt nur im Privatvermögen.
  Das kollidiert frontal mit der Entscheidung „Erwerb privat".

- **Die Antragstellung für die Förderung ändert sich.** Die Zahl der
  *Wohneinheiten* ändert sich durch eine Teilung nicht — Wohneinheit ist ein
  baulicher Begriff (KfW-Merkblatt 458, Stand 07/2026). Aber bei Maßnahmen am
  **Gemeinschaftseigentum** wird die WEG Antragstellerin, mit Verwalternachweis,
  ggf. Steuernummer und Kontonachweis. Ob die KfW eine „Ein-Personen-WEG"
  weiterhin als Einzeleigentümer behandelt, ergibt sich aus dem Merkblatt
  **nicht eindeutig** und sollte vor einer Teilung schriftlich geklärt werden.

### Und zwei Punkte aus eurer eigenen Planung

- Nach einer Teilung werden Heizung, Dach und Fassade **Gemeinschaftseigentum**.
  Solange euch alles gehört, unproblematisch; ab der ersten verkauften Einheit
  bestimmen fremde Miteigentümer mit. *(Ob die Wärmepumpe für beide Hausteile
  **zentral** ausgelegt wird, steht in `Reihenfolge-der-Optimierungen.md` — das
  konnte ich ohne Vault nicht prüfen. Bei zwei getrennten Anlagen wäre nur die
  Hülle betroffen.)*
- Die **PV soll privat gewerblich** betrieben werden und aufs Dach — das nach
  einer Teilung Gemeinschaftseigentum wäre. Eine gewerbliche PV auf einem
  Gemeinschaftsdach mit fremden Miteigentümern ist ein eigener Konflikt.
- Die Teilung ist **nicht umkehrbar**.

## Ein Befund außer der Reihe: die Förderung läuft euch davon

Das gehört nicht zu den drei Optionen, kam aber bei der Rechtsprüfung heraus und
ist zeitkritischer als alles andere in diesem Dokument.

**Zwei Änderungen vom Juli 2026:**

- **BEG-EM-Reform vom 17.07.2026**, gültig ab 21.07.2026: Der **Effizienzbonus
  ist ersatzlos entfallen**, der Förderhöchstbetrag der ersten Wohneinheit von
  30.000 € auf **28.000 €** gesenkt.
- **Gebäudemodernisierungsgesetz (GModG)**, in Kraft seit 29.07.2026: Das GEG
  heißt jetzt GModG, **§ 71 GEG mit der 65-%-Regel ist gestrichen** und durch
  einen technologieoffenen Optionenkatalog in § 42 GModG ersetzt.

**Was das für euch heißt:**

| | |
|---|---|
| Grundförderung als Kapitalanleger | **30 %** |
| Klimageschwindigkeitsbonus (16 %) | **nein** — nur Selbstnutzer |
| Einkommensbonus | **nein** — nur Selbstnutzer |
| Effizienzbonus | **entfallen** |
| Höchstbetrag 1. Wohneinheit | 28.000 € |
| Höchstbetrag 2.–6. Wohneinheit | je 15.000 € |

> [!warning] Korrektur einer Zahl, die im Projekt steht
> Die Aussage „als Kapitalanleger bleiben 30 %, mit Effizienzbonus 35 %" ist
> **seit 21.07.2026 überholt**. Es bleiben **30 %, ohne Aufschlag.**

Und der Punkt, der eure Reihenfolge betrifft:

> [!danger] Zielkollision mit „Umsetzung gebündelt nach dem Auszug"
> Der **Förderhöchstbetrag der ersten Wohneinheit sinkt ab 01.02.2027
> halbjährlich um 750 €**, der Klimageschwindigkeitsbonus um 4 Prozentpunkte.
> Maßgeblich ist der **Zeitpunkt der Antragstellung**.
>
> Die Entscheidung, die Maßnahmen zu bündeln und erst nach Stephans Auszug
> umzusetzen, läuft damit gegen eine Kostenuhr. Das ist kein Grund, die
> Entscheidung umzuwerfen — aber es ist ein Preis, der bisher nicht beziffert
> ist. Er gehört gerechnet, sobald der voraussichtliche Antragszeitpunkt
> feststeht.

Weitere Punkte mit Geldwirkung:

- **Ein Antrag pro Maßnahme, eine spätere Aufstockung ist ausgeschlossen.** Das
  stützt eure Entscheidung „ein Förderantrag für beide Hausteile" — heißt aber
  auch: Der Antrag muss beim ersten Mal vollständig sein.
- **Vorhabenbeginn vor Antragstellung schließt die Förderung aus.** Der
  Liefer-/Leistungsvertrag braucht eine aufschiebende oder auflösende Bedingung.
- **Kumulierung mit § 35c EStG ist ausgeschlossen.** Für dieselbe Maßnahme kein
  Steuerbonus zusätzlich.
- **Zweckbindung 10 Jahre** für die Heizungsanlage.
- **Eine im Grundbuch eingetragene GbR ist nicht antragsberechtigt.** Falls je
  eine GbR-Struktur erwogen wird: Sie kostet die Heizungsförderung.

*(Die PV bleibt von dieser Betrachtung ausgenommen — sie wird nach der
getroffenen Entscheidung aus dem Cashflow bezahlt, nicht über eine weitere
Kreditlinie.)*

## Wie die drei zusammenhängen

| | wirkt | Voraussetzung | verfällt, wenn |
|---|---|---|---|
| **Option 2** Verkäuferdarlehen | beim Kauf | Bank erkennt es an **und** Stephan macht mit | der Kaufvertrag unterschrieben ist |
| **Option 1** Nachbeleihung | ab ca. Jahr 9 ohne Wertzuwachs, ab Jahr 5 mit +10 % | Grundschuld heute richtig bestellt | nie — aber die Vorarbeit verfällt beim Notartermin |
| **Option 3** WEG-Teilung | erst nach geklärter Abgeschlossenheit und Bankauskunft | bauliche Abgeschlossenheit; Bank rechnet den Aufschlag an | nie |

1. **Option 1 und 3 zielen auf dasselbe** — mehr Kreditvolumen aus höherem Wert.
   Option 3 ist der teurere, langsamere und steuerlich riskantere Weg dorthin.
2. **Nur Option 2 ist zeitkritisch.** Sie ist die einzige, die man durch
   Nichtstun verliert.
3. **Option 2 verbessert die Startposition für Option 1** — ein niedrigerer
   Auslauf beim Kauf lässt den Spielraum Jahre früher entstehen.

Und der Punkt, der in keiner der drei Ideen steckt: **Beleihungsauslauf ist
nicht Tragfähigkeit.** Der Sprung von 80 % auf 95 % Auslauf kostet bei der
angenommenen Staffel rund **5.477 € Zinsen mehr pro Jahr** auf dasselbe
Darlehen. „Wieviel kann ich finanzieren" ist nicht „wieviel sollte ich
finanzieren".

## Was ich daraus empfehle

**Vor dem Notartermin — kostet nichts, verfällt sonst:**

1. Bank fragen: Sicherheitsabschlag, Bezugsgröße der Auslaufquote, Zinsstaffel
   **als Staffel**, und nach welchem Regelwerk bewertet wird.
2. Bank fragen: Verkäuferdarlehen mit qualifiziertem Rangrücktritt als
   eigenkapitalähnlich? **Vor** dem Gespräch mit Stephan.
3. Grundschuldhöhe, Zweckerklärung und Nachbeleihungsrecht bewusst entscheiden.
4. **Kaufpreisaufteilung in die notarielle Urkunde** — sie entscheidet über den
   Zinsabzug und ist danach nicht mehr reparabel.

**Vor der Mietvertragsverhandlung mit Stephan:**

5. Die Anfangsmiete durchrechnen. Sie bestimmt über § 10 Abs. 1 BelWertV den
   Beleihungswert und damit euren Zinssatz — nicht nur den Cashflow.
6. Verkäuferdarlehen als Mittel einsetzen, die 740.000 € zu **halten**. Höhe
   spitz auf die Scheibengrenze rechnen, nicht runden.

**Zeitnah, unabhängig von den drei Optionen:**

7. Antragszeitpunkt für die BEG-Förderung gegen die halbjährliche Absenkung ab
   01.02.2027 rechnen.

**Später, in dieser Reihenfolge:**

8. Nachbeleihung als geplanten Schritt vorsehen — realistisch ab Jahr 5 bis 9.
9. WEG-Teilung **zurückstellen.** Erst die billigste Frage beantworten (ist
   Abgeschlossenheit baulich herstellbar?), dann die zweitbilligste (rechnet die
   Bank den Aufschlag an?). Erst wenn beide mit Ja beantwortet sind, lohnt der
   Gang zum Steuerberater wegen der Drei-Objekt-Grenze. Vorher ist jede Ausgabe
   dafür verfrüht.

## Was fachlich abzusichern ist

Nichts davon ist Rechts- oder Steuerberatung. Was vor einer Entscheidung
geklärt gehört:

**Steuerberater — vor jeder Unterschrift**

- Gewerblicher Grundstückshandel vor **jeder** Teilungsentscheidung
  (BMF 26.03.2004, BFH GrS 1/98). Bei diesem Risiko ist eine **verbindliche
  Auskunft nach § 89 Abs. 2 AO** die Gebühr wert.
- Anwendbarkeit von BFH VIII R 30/24 auf ein **Fremdgeschäft** — entschieden
  wurde ein Angehörigenfall. Dazu: BStBl-Veröffentlichung oder
  Nichtanwendungserlass?
- Ob eine unverzinsliche Stundung die GrESt-Bemessungsgrundlage senkt.
- Kaufpreis- und Darlehenszuordnung vor dem Notartermin.
- **Grunderwerbsteuersatz NRW** — die 6,5 % sind nicht gegen eine Primärquelle
  geprüft.

**Fachanwalt für Mietrecht**

- Fällt der **Heizkörpertausch** noch unter § 555b Nr. 1a BGB? Daran hängt ein
  relevanter Teil der Sanierungskosten. Die Fußbodenheizung fast sicher nicht.
- Indexmietklausel (§ 557b Abs. 1 BGB, Schriftform) zusammen mit der
  Umlagemechanik des § 559e. § 557b Abs. 4 und § 559a Abs. 5: Abweichungen
  zulasten des Mieters sind unwirksam.
- Vorkaufsrecht und Sperrfrist, Zeitfolge sauber dokumentieren.

**Energieberater**

- Besteht nach dem GModG noch eine Austauschpflicht für den **Kessel von 2004**?
  § 72 GEG wurde gestrichen; ob für Konstanttemperaturkessel etwas
  fortbesteht, ist unklar. **Nicht am Gesetzestext geprüft** — nicht in der
  Verhandlung damit argumentieren, bevor das geklärt ist.
- BEG-Antrag: BzA vor Vertragsabschluss, aufschiebende Bedingung, Zählung der
  Wohneinheiten.

**KfW, schriftlich, vor einer Teilung**

- Wie wird eine „Ein-Personen-WEG" behandelt — als WEG oder als
  Einzeleigentümer?

**Notar**

- Aktueller Stand einer etwaigen NRW-Umwandlungsverordnung zum Termin.
- Kaufpreisaufteilung und Verkäuferdarlehen in derselben Urkunde.

> [!note] Quellenvorbehalt
> `gesetze-im-internet.de` war während der Recherche durchgehend nicht
> erreichbar. Alle Gesetzeszitate stammen von dejure.org und buzer.de, jeweils
> mit Änderungsfußnoten gegengeprüft. Eine verbreitete Fundstelle führte
> § 557b Abs. 2 BGB noch in der Fassung **vor 2024** und hätte zum gegenteiligen
> Ergebnis geführt. Vor Verwendung in einem bindenden Dokument gegen die
> amtliche Fassung prüfen.

## Offene Fragen

### An die Bank — vor dem Notartermin

- [ ] Sicherheitsabschlag zwischen Kaufpreis und Beleihungswert?
- [ ] Bezieht sich eure Auslaufquote auf Beleihungswert oder Kaufpreis?
- [ ] **Zinsstaffel** nach Beleihungsauslauf — als Staffel, nicht als ein Satz.
- [ ] Bewertet ihr nach BelWertV? Mit welchem Kapitalisierungszinssatz und
      welcher Restnutzungsdauer?
- [ ] Verkäuferdarlehen mit qualifiziertem Rangrücktritt — eigenkapitalähnlich?
- [ ] Empfohlene **Grundschuldhöhe** im Hinblick auf spätere Aufstockung, und
      Kosten einer späteren Erhöhung?
- [ ] Nachbeleihungsrecht und Sondertilgungsrechte vertraglich zusicherbar?
- [ ] Was kostet das **Vollgutachten** (Darlehen über 600.000 €), und was eine
      spätere Neubewertung?
- [ ] Würdet ihr nach einer WEG-Teilung die Summe der Einzelwerte ansetzen —
      oder bliebe es beim Ertragswert, ggf. mit Paketabschlag?
- [ ] Gibt es neben dem Volltilger-Angebot eine Variante mit Zinsscheibenstaffel?

### An den Architekten oder Vermesser

- [ ] Ist **Abgeschlossenheit** für Altbestand und Anbau baulich herstellbar —
      und mit welchem Umbauaufwand?

### An Stephan — erst nach der Bankauskunft

- [ ] Wäre ein Verkäuferdarlehen denkbar, und in welcher Größenordnung?
- [ ] Welche Laufzeit und Verzinsung stellst du dir vor?

### Für den Vault

- [ ] **Nettokaltmiete** — die wichtigste fehlende Zahl. Ohne sie ist keine
      Ertragswertaussage und damit keine Bewertung von Option 1 belastbar.
- [ ] Voraussichtlicher Antragszeitpunkt BEG, für die Kostenuhr-Rechnung.
- [ ] Sieht `Reihenfolge-der-Optimierungen.md` **eine zentrale** Wärmepumpe für
      beide Hausteile vor oder zwei getrennte Anlagen?
- [ ] Bezieht sich die Obergrenze 800.000 € auf den Kaufpreis oder auf die
      Gesamtinvestition? (Die Gesamtinvestition liegt bei 804.607 € — optisch
      fast identisch, inhaltlich etwas anderes.)

## Annahmen, auf denen diese Analyse beruht

**Belegt**

| Größe | Wert | Quelle |
|---|---|---|
| Zielpreis / Obergrenze | 740.000 € / 800.000 € | `CLAUDE.md` |
| Eigenkapital | 120.000 € | `CLAUDE.md` |
| **Volltilger 34 Jahre zu 5,45 %** | reales Angebot Wüstenrot | Nutzerfakt |
| **Kein Makler, Privatverkauf** | 0 % | Nutzerfakt |
| Verkäufer bleiben unbefristet, Indexmiete | | `CLAUDE.md` |
| Ein Förderantrag für beide Hausteile | | `CLAUDE.md` |

**Referenz, mit Prüfvorbehalt**

| Größe | Wert | Quelle |
|---|---|---|
| Grunderwerbsteuer NRW | 6,5 % | Skill-Referenz, **nicht primärgeprüft** |
| Notar / Grundbuch | 1,5 % / 0,5 % | Planungsgrößen Skill |
| Grundschuldbestellung | 0,25 % | Skill-Referenz (0,2–0,3 %) |
| Kapitalisierungszinssatz | 5,5 % | § 12 Abs. 4 BelWertV, Korridor-Obergrenze Wohnen |
| Bewirtschaftungskosten | 20 % | § 11 Abs. 2 BelWertV verlangt mind. 15 % |
| Kleindarlehensgrenze | 600.000 € | § 24 BelWertV |

**Annahme — vor jeder Entscheidung durch echte Werte ersetzen**

| Größe | Annahme | woher der echte Wert kommt |
|---|---|---|
| Sicherheitsabschlag Beleihungswert | 10 % | Bank |
| Zinsstaffel unterhalb 5,45 % | 3,95–5,45 % | Bank |
| Zielauslauf für Nachbeleihung | 90 % | Bank |
| Beleihungsquote Option 3 | 95 % | Bank |
| Restnutzungsdauer | 40 Jahre | Gutachten |
| Zins Verkäuferdarlehen | 4,0 % | Verhandlung |
| Teilungskosten | 15.000 € | Angebot Architekt/Notar |
| Wertzuwachs-Stufen (+10 %, +20 %) | Rechenstützstellen | — |
| Aufteilungsaufschlag (0–20 %) | Rechenstützstellen | Marktvergleich |
| **Nettokaltmiete** | **fehlt ganz** | Mietverträge |

## Was diese Analyse umkehren würde

- **Sicherheitsabschlag deutlich unter 10 %** → niedrigerer Ausgangsauslauf,
  Option 1 rückt näher.
- **Bank erkennt das Verkäuferdarlehen nicht als eigenkapitalähnlich an** →
  Hauptvorteil von Option 2 entfällt, übrig bleibt eine Stundung.
- **Bank sagt zu, nach einer Teilung die Summe der Einzelwerte anzusetzen** →
  Option 3 wird ernsthafter Kandidat, und die Drei-Objekt-Grenze wird zur
  entscheidenden Frage.
- **Abgeschlossenheit nicht herstellbar** → Option 3 entfällt vollständig, ohne
  weitere Prüfung.
- **Nettokaltmiete deutlich über dem Kapitaldienst** → das ganze Bild
  verschiebt sich zugunsten von Option 1.
- **Der Heizkörpertausch fällt unter § 555b Nr. 1a BGB** → ein größerer Teil
  der Sanierung wäre trotz Indexmiete umlagefähig, wenn auch weiter durch
  § 559e gekappt.
