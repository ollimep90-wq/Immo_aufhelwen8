# Dataview queries

Requires the community plugin **Dataview** (Settings → Community plugins →
Browse → "Dataview"). Everything below is DQL in a ```dataview code fence.
For it to work, frontmatter must hold **numbers, not strings** — see
`frontmatter.md`.

Dataview renders live in Obsidian but is invisible to the scripts and to you when
you read a file. **Never read a figure out of a dashboard — read it from the
source note or from `vault_scan.py`.**

## Aktive Objekte

````markdown
```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Objekt",
  status AS "Status",
  price_asking AS "Preis",
  living_area_m2 AS "m²",
  round(price_asking / living_area_m2) AS "€/m²",
  city AS "Ort"
FROM "10-Objekte"
WHERE type = "objekt" AND status != "abgelehnt"
SORT price_asking ASC
```
````

## Kapitalanlage-Kennzahlen

````markdown
```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Objekt",
  price_asking AS "Preis",
  rent_cold_month AS "Miete kalt",
  round(price_asking / (rent_cold_month * 12), 1) AS "Faktor",
  round(rent_cold_month * 12 * 100 / price_asking, 2) AS "Brutto-Rendite %",
  hausgeld_month AS "Hausgeld"
FROM "10-Objekte"
WHERE type = "objekt" AND rent_cold_month AND status != "abgelehnt"
SORT (price_asking / (rent_cold_month * 12)) ASC
```
````

> Faktor and Brutto-Rendite here ignore Kaufnebenkosten and non-apportionable
> costs — they are a first screen, not a decision basis. Use `property_calc.py`
> before acting on them.

## Datenlücken — was fehlt, bevor entschieden werden kann

````markdown
```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Objekt",
  choice(living_area_m2, "", "Wohnfläche") AS "fehlt 1",
  choice(year_built, "", "Baujahr") AS "fehlt 2",
  choice(energy_value_kwh_m2a, "", "Energiekennwert") AS "fehlt 3",
  choice(heating_year, "", "Heizung Bj.") AS "fehlt 4",
  choice(bundesland, "", "Bundesland") AS "fehlt 5"
FROM "10-Objekte"
WHERE type = "objekt" AND status != "abgelehnt"
  AND (!living_area_m2 OR !year_built OR !energy_value_kwh_m2a OR !heating_year OR !bundesland)
```
````

## Heizungsrisiko (Alter der Anlage)

````markdown
```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Objekt",
  heating_type AS "Art",
  heating_year AS "Baujahr",
  (date(today).year - heating_year) AS "Alter"
FROM "10-Objekte"
WHERE type = "objekt" AND heating_year AND status != "abgelehnt"
SORT heating_year ASC
```
````

## Offene Aufgaben aus allen Objektnotizen

````markdown
```dataview
TASK
FROM "10-Objekte"
WHERE !completed
GROUP BY file.link
```
````

## Termine / Besichtigungen

````markdown
```dataview
TABLE WITHOUT ID
  file.link AS "Notiz", date AS "Datum", verdict AS "Fazit"
FROM "10-Objekte"
WHERE type = "besichtigung"
SORT date DESC
```
````

## Archiv — was abgelehnt wurde und warum

````markdown
```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Objekt",
  price_asking AS "Preis",
  ko_failed AS "K.O.-Kriterium"
FROM "10-Objekte" OR "99-Archiv"
WHERE type = "objekt" AND status = "abgelehnt"
SORT updated DESC
```
````

## Syntax notes

- `FROM "Ordner"`, `FROM #tag`, `FROM [[Notiz]]` (backlinks); combine with
  `AND` / `OR` / `-`.
- `WHERE !feld` is true when the field is missing or empty — that is how the
  gap query above works.
- `TABLE WITHOUT ID` drops the automatic file-link column so you control the first
  column.
- Numeric fields stored as strings silently sort alphabetically and break
  arithmetic. If a query looks wrong, check the frontmatter types first.
- `dataviewjs` blocks are more powerful but harder to maintain — do not reach for
  them unless DQL genuinely cannot express the query.
