---
name: obsidian
description: Work with the user's Obsidian vault for a real-estate purchase — capture, verify and query everything known about candidate properties, and use that vault as the factual background for purchase decisions. Use whenever the user mentions Obsidian, their vault, a note, an "Objekt"/property/Immobilie/Wohnung/Haus, an Exposé, a viewing (Besichtigung), financing (Finanzierung/Annuität/Zinsbindung), Hausgeld/WEG documents, or asks to compare properties, run the numbers, or decide whether to buy or bid.
---

# Obsidian vault for a property purchase

This skill has two jobs, in this order:

1. **Keep the vault a trustworthy record.** Every fact about a property lands in a
   note, with a source and a date. Nothing is invented.
2. **Use that record for decisions.** Comparisons, offers and go/no-go calls are
   made from the vault plus the calculation script — never from memory or from a
   number the user mentioned three messages ago.

The user is buying a property (own use and/or rental — check the Suchprofil).
Money and legal exposure are real. **Being conservative and explicit about
uncertainty beats being helpful and wrong.**

## Language convention

- Skill instructions and reference files: English.
- **Vault-facing content — note bodies, headings, templates, filenames: German.**
  The domain vocabulary is German (Hausgeld, Teilungserklärung, Grunderwerbsteuer)
  and translating it loses precision.
- **Frontmatter keys: English and lowercase_snake_case** (stable, machine-readable).
  Values may be German.

## Step 0 — resolve the vault (always, before anything else)

Resolve the vault root in this order and stop at the first hit:

1. A path the user gave in this conversation.
2. `$OBSIDIAN_VAULT`.
3. `~/.config/claude-obsidian/vault-path` (a file containing one path).
4. A directory containing `.obsidian/` under `~`, `~/Documents`, `~/Dokumente`,
   `~/Library/Mobile Documents/iCloud~md~obsidian/Documents`:
   `find <dir> -maxdepth 4 -type d -name .obsidian 2>/dev/null`
5. Ask the user. Do not guess, and do not create a vault in a random location.

Remember the resolved path for the rest of the session. If a later path looks like
a *different* vault, stop and ask.

## Step 0.5 — adopt the vault as it is

**The vault belongs to the user. This skill adapts to it, never the reverse.**
Never rename, move or restructure notes and folders that already exist, and never
create a second structure next to theirs.

Check for a vault profile — `~/.config/claude-obsidian/vault-profile.md`, or
`Vault-Profil.md` inside the vault. It records the vault's real folders and the
user's own frontmatter field names.

**If a profile exists:** pass it to every script (`--profile <pfad>`) and use the
user's field names in everything you write.

**If there is none and the vault already has notes:**

```bash
python3 .claude/skills/obsidian/scripts/vault_profile.py "$VAULT"
```

This only reads. It reports the folders that look property-related, the `type`
values and tags in use, and a proposed mapping from this skill's canonical fields
onto the user's actual ones. **Show the user the proposal and let them correct it
before saving** — especially the lines marked as ambiguous or conflicting, where
one of their fields matched two skill fields. Then:

```bash
python3 .claude/skills/obsidian/scripts/vault_profile.py "$VAULT" \
    --write ~/.config/claude-obsidian/vault-profile.md
```

Whatever the profile does not map, **ask about — never guess.** A field that has
no equivalent in their vault is a question, not a default.

**If the user hands over loose notes to be rebuilt** (rather than pointing at a
live vault), use `scripts/migrate_vault.py <quelle> <ziel>`. It classifies each
note, maps the frontmatter onto canonical names, files everything into the
structure, renames object notes while keeping the old name as an alias, rewrites
the wikilinks, and writes `MIGRATION.md`. **Read that report and walk the user
through its "Bitte prüfen" section** — those are the notes it could not place
with confidence. Never present a migration as finished without it.

**Only if the vault is empty:** offer the structure in
`references/vault-structure.md` via `scripts/init_vault.py`. That script refuses
to run in a vault that already has notes of its own, and that refusal is correct —
do not `--force` past it without the user explicitly asking.

## Step 1 — load the background (before answering anything substantive)

Do not answer a question about a property, a price, a comparison or a decision
without loading context first:

```bash
python3 .claude/skills/obsidian/scripts/vault_scan.py "$VAULT" --table \
    --profile ~/.config/claude-obsidian/vault-profile.md
```

That prints one row per property note with the key figures. Then read, as relevant:

- The **Suchprofil** — buying criteria, budget ceiling, K.O. criteria.
  **Required for any comparison, scoring or recommendation.** In an adopted vault
  it may live anywhere and be called something else; the profile note or the user
  will say where. If it does not exist, create it with them first (template:
  `assets/templates/suchprofil.md`), in *their* folder.
- The **Finanzierungsrahmen** — equity, income, bank feedback, stress assumptions.
- The full note of every property under discussion, plus its `Besichtigungen/`,
  `Dokumente/` and `Finanzierung/` subfolders.

For a purely mechanical task ("rename this note", "fix the frontmatter") the scan
is enough; skip the rest.

## Core rules

**Never invent a value.** If a figure is not in a document, a listing or something
the user said, it does not go into frontmatter. It goes under `## Offene Fragen`
in the note body, phrased as a question to ask the seller/agent.

**Every fact carries a source.** Frontmatter has `data_asof` and `sources`.
Facts in the body table carry a Quelle column (Exposé, Grundbuchauszug,
Teilungserklärung, Protokoll EV 2024-05-12, Makler mündlich, Annahme).
"Makler mündlich" and "Annahme" are explicitly weaker — mark them.

**Facts and assumptions live in different notes.** The property note holds facts.
Financing assumptions (interest rate, equity, repayment, vacancy, maintenance
reserve) live in a scenario note under `Finanzierung/`. That way a changed
assumption never silently rewrites a fact.

**Never do the money math in your head.** Use the script:

```bash
python3 .claude/skills/obsidian/scripts/property_calc.py "$VAULT/10-Objekte/OBJ-.../OBJ-....md" \
    --scenario "$VAULT/10-Objekte/OBJ-.../Finanzierung/Szenario-Basis.md"
```

It computes Kaufnebenkosten, Gesamtinvestition, €/m², Kaufpreisfaktor, gross and
net yield, the annuity, the balance left at the end of the Zinsbindung, cashflow,
and a rate-stress case. Quote its output; do not round it into something prettier.

**The user's structure wins.** Their folder names, note names and field names are
the convention; this skill's schema is the fallback for what does not exist yet.
Adding a new field to their notes is fine — say that you are doing it. Renaming
or moving what is already there is not.

**Edits are surgical and non-destructive.** Read a note before editing it. Preserve
frontmatter keys you do not understand, preserve the user's own prose, and never
delete a section to "clean up". Prefer appending to `## Verlauf`.

**Do not give legal or tax advice.** The references summarise German rules to help
you ask the right questions and flag risk. Say plainly when something needs a
Notar, Steuerberater, Gutachter or Energieberater.

## Workflows

### New property (Exposé, link or the user describing one)
1. **Follow the vault's existing conventions** — the folder from the profile's
   `objects_folder`, the naming pattern of the notes already there, and the
   field names from `field_map`. The scheme below is only for a vault that has
   no convention yet.
2. Assign the next free id: `OBJ-<year>-<NNN>` (check existing ids in the scan);
   skip ids entirely if the vault names notes by address.
3. Create the note from `assets/templates/objekt.md`, translated into the
   vault's field names, and add fields it does not have yet only after saying so.
4. Fill only what is actually sourced. Everything else → `## Offene Fragen`.
5. Run `property_calc.py`; put the output in `## Wirtschaftlichkeit`.
6. Check the K.O. criteria from the Suchprofil and set `status` accordingly.
7. Tell the user what is missing before this can be judged.

### Before a viewing
Create `Besichtigungen/YYYY-MM-DD Besichtigung.md` from
`assets/templates/besichtigung.md`, pre-filled with the open questions from the
property note and the relevant items from `references/due-diligence.md`.

### After a viewing / new documents
Move confirmed values from the viewing note into the property note's frontmatter
(updating `data_asof` and `sources`), remove the answered items from
`## Offene Fragen`, re-run the calculation, append to `## Verlauf`.

### Comparison / shortlist
Filter by K.O. criteria first, then score against the weighted criteria from the
Suchprofil (`references/decision-framework.md`), then show the economics side by
side. Present the ranking *and* what would change it.

### Before making an offer
Derive the ceiling from the user's own figures, never from the asking price:

```bash
python3 .claude/skills/obsidian/scripts/property_calc.py --max-price \
    --price <geforderter Preis> --bundesland … --commission … --rent … --area … \
    --equity … --rate … --target-cashflow 0 --target-factor 22 --max-total …
```

It solves for the price at which each limit binds and names the strictest one.
Record that number, with the date, in the property note **before** the first
negotiation. Afterwards it moves only when a *fact* changes — not when a
competing bidder appears. See `references/decision-framework.md`.

### Decision (bid, walk away, sign)
Write a decision note in `60-Entscheidungen/` from
`assets/templates/entscheidung.md`: context, options considered, decision,
reasoning, assumptions it rests on, and what would reverse it. Link it from the
property note. This is the record the user will re-read in a year.

## References

Read the one you need; do not preload all of them.

| File | Read it when |
|---|---|
| `references/vault-structure.md` | Setting up a NEW vault, or understanding the default layout |
| `references/frontmatter.md` | Writing or validating any note's frontmatter — the full field schema |
| `references/obsidian-syntax.md` | Wikilinks, embeds, tags, callouts, Properties, folder notes |
| `references/dataview.md` | Building dashboards and queries over the objects |
| `references/kaufnebenkosten-de.md` | Any purchase-cost, yield, AfA or tax-adjacent number |
| `references/due-diligence.md` | Documents to demand, WEG vs. Haus, red flags, viewing checklist |
| `references/decision-framework.md` | Suchprofil, K.O. filter, scoring, decision notes |
| `references/rest-api.md` | The user wants Claude to reach a *running* Obsidian instead of files |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/vault_profile.py` | Read an existing vault and propose how to map it onto this skill. Read-only unless `--write`. |
| `scripts/vault_scan.py` | Index all property notes → table / JSON / summary. Cheap context loading. Honours `--profile`. |
| `scripts/property_calc.py` | All purchase and financing math. Deterministic, shows its formulas. |
| `scripts/migrate_vault.py` | Rebuild loose notes into a clean vault: classify, normalise frontmatter, rename, relink, and write a migration report. Source is read-only. |
| `scripts/init_vault.py` | Scaffold folders, Suchprofil and dashboards — **empty vaults only**. |

Run them with `python3`. They only need the standard library (PyYAML is used if
present, otherwise a built-in flat-YAML parser handles the schema).
