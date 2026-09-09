# Kaufnebenkosten, Kennzahlen und Steuern (Deutschland)

> **Stand: Modell-Kenntnisstand Mai 2026. Keine Rechts- oder Steuerberatung.**
> Steuersätze und Gesetze ändern sich. Prüfe jeden Satz gegen eine aktuelle
> Primärquelle (Landesfinanzministerium, § im Gesetzestext, Notarkostenrechner),
> bevor du damit rechnest — und sage dem Nutzer, mit welchem Satz du gerechnet
> hast. Bei allem, was verbindlich wird: Notar, Steuerberater, Gutachter.

## 1. Kaufnebenkosten

Vier Blöcke. Zusammen typischerweise **9–15 % des Kaufpreises**. Banken
finanzieren sie in der Regel **nicht** — sie müssen aus Eigenkapital kommen.

### Grunderwerbsteuer (GrEStG, Satz je Bundesland)

| Bundesland | Satz |
|---|---|
| Bayern | 3,5 % |
| Baden-Württemberg | 5,0 % |
| Berlin | 6,0 % |
| Brandenburg | 6,5 % |
| Bremen | 5,0 % |
| Hamburg | 5,5 % |
| Hessen | 6,0 % |
| Mecklenburg-Vorpommern | 6,0 % |
| Niedersachsen | 5,0 % |
| Nordrhein-Westfalen | 6,5 % |
| Rheinland-Pfalz | 5,0 % |
| Saarland | 6,5 % |
| Sachsen | 5,5 % |
| Sachsen-Anhalt | 5,0 % |
| Schleswig-Holstein | 6,5 % |
| Thüringen | 5,0 % |

Dieselbe Tabelle steht in `scripts/property_calc.py` (`GRESt_RATES`) — wenn du
einen Satz korrigierst, korrigiere **beide** Stellen.

Hinweise:
- Bemessungsgrundlage ist die Gegenleistung, nicht nur der Kaufpreis.
- Mitverkaufte **bewegliche Gegenstände** (Einbauküche, Markise, Sauna) können im
  Kaufvertrag gesondert und mit realistischem Zeitwert ausgewiesen werden und
  gehören dann nicht zur Bemessungsgrundlage. Überzogene Werte kassiert das
  Finanzamt — Faustregel der Praxis: deutlich unter 15 % des Kaufpreises bleiben,
  Zeitwerte belegen können.
- Die **Erhaltungs-/Instandhaltungsrücklage einer WEG mindert die
  Bemessungsgrundlage nicht** (BFH, Urteil vom 16.09.2020 – II R 49/17). Ältere
  Ratgeber behaupten das Gegenteil; nicht darauf verlassen.

### Notar und Grundbuch

Gesetzlich festgelegt (GNotKG), nicht verhandelbar, gestaffelt nach
Geschäftswert. Planungsgröße:

- Notar inkl. Vollzug und Treuhandtätigkeit: **ca. 1,0–1,5 %**
- Grundbuchamt (Eigentumsumschreibung, Auflassungsvormerkung): **ca. 0,5 %**
- Zusammen **ca. 1,5–2,0 %** — das Skript rechnet mit 1,5 % + 0,5 %.

Die **Grundschuldbestellung** für die Bank kostet zusätzlich (Notar + Grundbuch,
je nach Grundschuldhöhe grob 0,2–0,3 % der Grundschuld). Bei knappem Eigenkapital
mitrechnen.

### Maklerprovision

Seit 23.12.2020 gilt für den **Verkauf von Einfamilienhäusern und
Eigentumswohnungen an Verbraucher** das Teilungsgebot (§§ 656a–656d BGB): Der
Käufer trägt höchstens die Hälfte, und er muss erst zahlen, wenn der Verkäufer
seine Hälfte nachweislich gezahlt hat.

- Übliche Gesamtprovision: 5,95–7,14 % inkl. USt → **Käuferanteil ca. 2,98–3,57 %**.
- **Nicht** anwendbar auf Mehrfamilienhäuser, Grundstücke, Gewerbe oder wenn der
  Käufer kein Verbraucher ist — dort kann die volle Provision beim Käufer liegen.
- In `commission_pct` steht **immer der Käuferanteil inkl. USt**.

### Was gern vergessen wird

Bereitstellungszinsen bei späterem Abruf · Wertermittlung/Schätzkosten der Bank ·
separat verkaufter Stellplatz (eigene GrESt) · Umzug, Küche, Renovierung vor
Einzug · doppelte Mietzahlung im Übergang · Erschließungsbeiträge (bei
Grundstücken) · Rückstände, die mit dem Objekt übergehen.

## 2. Laufende Kosten

- **Grundsteuer** — seit 2025 nach den neuen Bewertungsregeln, Höhe hängt von
  Bundesland-Modell und kommunalem Hebesatz ab. **Nicht schätzen**: den
  tatsächlichen Bescheid beim Verkäufer anfordern und ins Feld
  `grundsteuer_year` schreiben.
- **Hausgeld (WEG)** — enthält umlagefähige Betriebskosten *und* nicht
  umlagefähige Anteile (Verwaltung, Zuführung zur Erhaltungsrücklage). Bei
  Vermietung sind nur die umlagefähigen Teile auf den Mieter umlegbar. Für die
  Renditerechnung zählt der **nicht umlagefähige** Teil als Kosten — dieser Split
  steht im Wirtschaftsplan, nicht im Exposé.
- **Instandhaltung** — Planungsgröße **10–15 €/m²/Jahr** für Wohngebäude, bei
  Altbau und schlechtem Zustand mehr. Die tatsächliche WEG-Rücklage liegt häufig
  darunter; die Differenz kommt später als Sonderumlage. Das Skript nutzt
  standardmäßig 12 €/m²/Jahr.
- **Verwaltung** bei Vermietung: 25–40 €/Wohnung/Monat (Standard: 30).
- **Mietausfallwagnis**: 2–4 % der Jahresnettokaltmiete (Standard: 3 %).
- Versicherungen (Wohngebäude, Haftpflicht), Schornsteinfeger, Wartung.

## 3. Kennzahlen — exakte Definitionen

Verwende genau diese Definitionen, sonst sind Vergleiche wertlos.

```
Kaufnebenkosten      = Kaufpreis × (GrESt% + Notar% + Grundbuch% + Provision%)
Gesamtinvestition    = Kaufpreis + Kaufnebenkosten + Renovierungskosten
Preis je m²          = Kaufpreis / Wohnfläche          (nicht: Gesamtinvestition)

Jahresnettokaltmiete = Nettokaltmiete/Monat × 12
Kaufpreisfaktor      = Kaufpreis / Jahresnettokaltmiete        (Vervielfältiger)
Bruttomietrendite    = Jahresnettokaltmiete / Kaufpreis
Nettomietrendite     = (Jahresnettokaltmiete − nicht umlagefähige Bewirtschaftungskosten)
                       / Gesamtinvestition
Cashflow vor Steuern = Jahresnettokaltmiete
                       − Mietausfallwagnis − Instandhaltung − Verwaltung
                       − nicht umlagefähiges Hausgeld
                       − Kapitaldienst (Zins + Tilgung)
Eigenkapitalrendite  = Cashflow vor Steuern / eingesetztes Eigenkapital
```

Der Kaufpreisfaktor ist die ehrlichste schnelle Zahl: **Faktor 25 = 4 %
Bruttorendite.** Bruttorendite ohne Nebenkosten ist immer zu optimistisch —
deshalb steht in der Nettorendite die Gesamtinvestition im Nenner.

## 4. Finanzierung

Deutsches Annuitätendarlehen: die Annuität ist **konstant** und ergibt sich aus
`Darlehen × (Sollzins% + anfängliche Tilgung%)`, monatlich gezahlt. Der Zinsanteil
sinkt, der Tilgungsanteil steigt.

Entscheidend ist nicht die Monatsrate, sondern die **Restschuld am Ende der
Zinsbindung**. Rechne immer einen Anschlusszins-Stresstest (Standard 6 %; bei
langer Restschuld auch 7 %). Wenn die Rate im Stressfall die Haushaltsrechnung
sprengt, ist das Objekt zu teuer — unabhängig davon, wie gut es sich anfühlt.

Weitere Punkte: Sondertilgungsrecht (üblich 5 % p. a., kostenlos verhandelbar),
Tilgungssatzwechsel, Beleihungsauslauf (unter 60 % / 80 % gibt es bessere Zinsen),
Forward-Darlehen, KfW-Programme (Konditionen ändern sich häufig — vor Nennung
prüfen).

## 5. Steuern — nur bei Vermietung relevant

- **AfA (§ 7 EStG)**, nur auf den **Gebäudeanteil**, nie auf Grund und Boden.
  Kaufnebenkosten werden im selben Verhältnis aufgeteilt.
  - 2,0 % linear, Fertigstellung nach dem 31.12.1924
  - 2,5 % linear, Fertigstellung vor dem 01.01.1925
  - 3,0 % linear für Wohngebäude, fertiggestellt nach dem 31.12.2022
  - 5 % degressiv (§ 7 Abs. 5a EStG) für Wohngebäude mit Baubeginn zwischen
    01.10.2023 und 30.09.2029 — Voraussetzungen genau prüfen
- **Schuldzinsen** sind bei Vermietung Werbungskosten, bei Eigennutzung nicht.
  Tilgung ist nie absetzbar.
- **Spekulationsfrist (§ 23 EStG)**: Verkauf innerhalb von 10 Jahren ist
  steuerpflichtig; steuerfrei bei durchgehender Eigennutzung oder Nutzung zu
  eigenen Wohnzwecken im Verkaufsjahr und den beiden Vorjahren.
- Die Aufteilung Grund/Gebäude im Kaufvertrag hat reale steuerliche Wirkung und
  wird vom Finanzamt geprüft — Thema für den Steuerberater, nicht für dich.
