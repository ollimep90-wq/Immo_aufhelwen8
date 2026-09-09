# Frontmatter schema

Keys are English `lowercase_snake_case`; values may be German. Obsidian shows
these as **Properties**. Dataview and the scripts read them, so format matters:

- **Money and areas: plain numbers.** `price_asking: 485000` — no `€`, no thousand
  separators, no `"485.000"`. A quoted string breaks every calculation.
- **Dates: `YYYY-MM-DD`**, unquoted.
- **Booleans: `true` / `false`**, not `ja`/`nein`.
- **Unknown: omit the key, or `null`.** Never `0`, never `"?"`, never a guess.
  A missing figure belongs under `## Offene Fragen` in the body.
- **Lists: block style** (`- item` on its own lines) — easier to diff and to edit.

---

## `type: objekt` — the property note

### Identity (required)

| Key | Type | Notes |
|---|---|---|
| `type` | `objekt` | fixed |
| `id` | string | `OBJ-YYYY-NNN`, unique, never reused |
| `title` | string | human-readable, e.g. `Musterstr 1, 12345 Musterstadt` |
| `aliases` | list | short names you would type in `[[…]]` |
| `status` | enum | `beobachtung` · `shortlist` · `besichtigt` · `angebot` · `kaufvertrag` · `gekauft` · `abgelehnt` |
| `created` | date | |
| `updated` | date | bump on every edit |
| `data_asof` | date | when the figures below were last confirmed |
| `sources` | list | e.g. `Exposé 2026-03-01`, `Teilungserklärung`, `Protokoll EV 2025-05-12`, `Makler mündlich 2026-03-14` |

### Location

`street`, `zip`, `city`, `district` (Stadtteil/Ortsteil), `bundesland`, optional
`lat`, `lon`.

`bundesland` is **required for any cost calculation** — it sets the
Grunderwerbsteuer rate. Use the full German name: `Nordrhein-Westfalen`,
`Bayern`, `Baden-Württemberg`, `Rheinland-Pfalz`, …

### Listing

`listing_url`, `listing_id`, `listing_date`, `source`
(`immoscout24` · `kleinanzeigen` · `immowelt` · `makler` · `privat` · `sonstige`),
`days_on_market`.

### The object itself

| Key | Type | Notes |
|---|---|---|
| `property_type` | enum | `wohnung` · `haus-einfamilien` · `haus-doppelhaus` · `haus-reihen` · `mehrfamilienhaus` · `grundstueck` · `gewerbe` |
| `usage_intent` | enum | `eigennutzung` · `kapitalanlage` · `gemischt` |
| `tenure` | enum | `eigentum` · `erbbaurecht` |
| `erbbauzins_year` | number | only if `tenure: erbbaurecht` |
| `erbbaurecht_until` | date | ditto — a short remaining term is a financing killer |
| `living_area_m2` | number | Wohnfläche |
| `plot_area_m2` | number | Grundstücksfläche |
| `rooms` | number | may be `3.5` |
| `floor` / `floors_total` | number | |
| `elevator` | bool | |
| `year_built` | number | |
| `year_renovated` | number | last significant renovation |
| `condition` | enum | `neubau` · `gepflegt` · `renovierungsbedarf` · `sanierungsbedarf` · `kernsanierung` |
| `features` | list | Balkon, Garten, Stellplatz, Keller, Gäste-WC … |
| `parking` | string | `tiefgarage` · `stellplatz` · `garage` · `keiner` |
| `parking_price` | number | if sold separately — it is extra purchase cost |
| `denkmalschutz` | bool | |
| `sanierungsgebiet` | bool | municipality may hold a Vorkaufsrecht |

### Energy (§ 80 GEG: the Energieausweis must be shown at the viewing)

`energy_certificate` (`bedarf` · `verbrauch` · `fehlt`),
`energy_value_kwh_m2a` (number), `energy_class` (`A+` … `H`),
`heating_type` (`gas-brennwert`, `gas-niedertemperatur`, `oel`, `fernwaerme`,
`waermepumpe`, `pellets`, `nachtspeicher`, …), `heating_year`,
`insulation_notes`.

> `heating_year` plus `heating_type` drives the biggest foreseeable cost after
> purchase. A 2004 gas boiler is a five-figure item on a five-year horizon.

### Money — facts only

| Key | Notes |
|---|---|
| `price_asking` | asking price |
| `price_offered` | what the user offered |
| `price_agreed` | notarised/agreed price — once set, calculations use this |
| `commission_pct` | **buyer's share** incl. USt, e.g. `3.57` |
| `commission_note` | e.g. `Teilungsgebot § 656c BGB, hälftig` |
| `hausgeld_month` | WEG total monthly |
| `hausgeld_reserve_share_month` | the Instandhaltungsrücklage share of it |
| `weg_reserve_total` | reserve on hand for the whole WEG |
| `weg_sonderumlage` | resolved or foreseeable special levy |
| `grundsteuer_year` | |
| `rent_cold_month` | current Nettokaltmiete, if rented |
| `rent_potential_month` | realistic market rent — **cite the source** (Mietspiegel, comparable listings) |
| `rented` | bool |
| `tenant_notes` | Mietvertrag date, indexed?, Eigenbedarf feasible? |

`renovation_budget_est` may be recorded here, but it is an **estimate**: put the
derivation in the body and repeat it in the financing scenario.

### Process

`makler`, `verkaeufer`, `notar` (each a `"[[Kontakt]]"` link string),
`decision` (link to the decision note), `score` (number, from the scoring in
`decision-framework.md`), `ko_failed` (list of violated K.O. criteria).

---

## `type: finanzierung-szenario` — a financing scenario

Facts stay in the property note; **every assumption lives here.** Multiple
scenarios per object are normal (`Szenario-Basis`, `Szenario-Stress`,
`Szenario-Bank-A`).

| Key | Default | Meaning |
|---|---|---|
| `object` | – | the `id` of the property note (required) |
| `name` | – | scenario label |
| `equity` | – | Eigenkapital actually put in (required) |
| `price_override` | – | use instead of the note's price |
| `interest_rate_pct` | – | nominal Sollzins p.a. (required) |
| `repayment_pct` | `2.0` | anfängliche Tilgung p.a. |
| `fixed_years` | `10` | Zinsbindung |
| `stress_rate_pct` | `6.0` | follow-up rate for the Anschlussfinanzierung stress test |
| `finance_side_costs` | `false` | confirms that financing the Kaufnebenkosten is intended. It only suppresses the warning — the loan is always `Gesamtinvestition − Eigenkapital`; watch the Beleihungsauslauf the script reports |
| `renovation_cost` | `0` | planned renovation, added to the investment |
| `grunderwerbsteuer_pct` | from Bundesland | override only with a reason |
| `notary_pct` | `1.5` | Notar incl. Vollzug |
| `land_register_pct` | `0.5` | Grundbuchamt |
| `commission_pct` | from the note | buyer's share incl. USt |
| `living_area_m2` | from the note | override only when the scenario assumes an extension — maintenance scales with it |
| `rent_used_month` | from the note | which rent the calculation uses |
| `vacancy_pct` | `3.0` | Mietausfallwagnis |
| `maintenance_eur_m2a` | `12.0` | non-apportionable Instandhaltung |
| `management_eur_month` | `30.0` | Verwaltung (non-apportionable) |
| `hausgeld_non_apportionable_month` | – | for a WEG, use this instead of the two rows above if you know the real split |

Defaults are conventional planning values, not law — see
`kaufnebenkosten-de.md`. Say which ones you used.

---

## `type: vault-profil` — the adopted vault's own conventions

Written by `scripts/vault_profile.py`, confirmed by the user, read by the other
scripts via `--profile`. It is what makes the skill work in a vault that never
heard of this schema.

| Key | Meaning |
|---|---|
| `vault_path` | the vault this profile describes |
| `generated` | when it was produced — regenerate after restructuring |
| `objects_folder` | folder holding the property notes, vault-relative (`""` = vault root) |
| `templates_folder` / `attachments_folder` | taken from Obsidian's own settings |
| `dataview` | whether the Dataview plugin is installed |
| `object_type_values` | the `type:` values that mark a property note in this vault |
| `object_tags` | tags that mark one |
| `field_map` | `canonical_field: name_in_this_vault`, one line each |

A note counts as a property note if it sits under `objects_folder`, **or** carries
one of `object_type_values`, **or** one of `object_tags`.

`field(fm, key, profile)` in `scripts/frontmatter.py` resolves a canonical name
through `field_map` and falls back to the canonical name — so a vault that
already uses this schema works with or without a profile.

Canonical fields missing from `field_map` do not exist in that vault. **Ask;
never substitute a default.**

## Other note types

`type: besichtigung` (`object`, `date`, `attendees`, `weather`, `verdict`),
`type: dokument` (`object`, `doc_type`, `doc_date`, `received`, `file`),
`type: kontakt` (`role`, `company`, `phone`, `email`),
`type: standort` (`city`, `district`, `mietspiegel_eur_m2`, `asof`),
`type: entscheidung` (`object`, `date`, `decision`, `review_on`),
`type: suchprofil` (see `decision-framework.md`).
