---
type: dashboard
---

# Dashboard

%% Benötigt das Community-Plugin "Dataview". Weitere Abfragen:
references/dataview.md im Skill. %%

## Aktive Objekte

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

## Datenlücken

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Objekt",
  choice(living_area_m2, "", "Wohnfläche") AS "fehlt 1",
  choice(year_built, "", "Baujahr") AS "fehlt 2",
  choice(energy_value_kwh_m2a, "", "Energie") AS "fehlt 3",
  choice(heating_year, "", "Heizung Bj.") AS "fehlt 4",
  choice(bundesland, "", "Bundesland") AS "fehlt 5"
FROM "10-Objekte"
WHERE type = "objekt" AND status != "abgelehnt"
  AND (!living_area_m2 OR !year_built OR !energy_value_kwh_m2a OR !heating_year OR !bundesland)
```

## Offene Aufgaben

```dataview
TASK
FROM "10-Objekte"
WHERE !completed
GROUP BY file.link
```

## Entscheidungen

```dataview
TABLE WITHOUT ID
  file.link AS "Notiz", date AS "Datum", decision AS "Entscheidung", review_on AS "Prüfen am"
FROM "60-Entscheidungen"
WHERE type = "entscheidung"
SORT date DESC
```

## Verknüpft

- [[Suchprofil]]
- [[Finanzierungsrahmen]]
