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

If the vault does not exist yet, offer to scaffold it —
see `references/vault-structure.md` and `scripts/init_vault.py`.

Remember the resolved path for the rest of the session. If a later path looks like
a *different* vault, stop and ask.

## Step 1 — load the background (before answering anything substantive)

Do not answer a question about a property, a price, a comparison or a decision
without loading context first:

```bash
python3 .claude/skills/obsidian/scripts/vault_scan.py "$VAULT" --table
```

That prints one row per property note with the key figures. Then read, as relevant:

- `90-Meta/Suchprofil.md` — the buying criteria, budget ceiling and K.O. criteria.
  **Required for any comparison, scoring or recommendation.** If it is missing,
  create it with the user first (template: `assets/templates/suchprofil.md`).
- `90-Meta/Finanzierungsrahmen.md` — equity, income, bank feedback, stress assumptions.
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

**Edits are surgical and non-destructive.** Read a note before editing it. Preserve
frontmatter keys you do not understand, preserve the user's own prose, and never
delete a section to "clean up". Prefer appending to `## Verlauf`.

**Do not give legal or tax advice.** The references summarise German rules to help
you ask the right questions and flag risk. Say plainly when something needs a
Notar, Steuerberater, Gutachter or Energieberater.

## Workflows

### New property (Exposé, link or the user describing one)
1. Assign the next free id: `OBJ-<year>-<NNN>` (check existing ids in the scan).
2. Create `10-Objekte/OBJ-YYYY-NNN <Straße Hausnr, Ort>/OBJ-YYYY-NNN.md`
   from `assets/templates/objekt.md`.
3. Fill only what is actually sourced. Everything else → `## Offene Fragen`.
4. Run `property_calc.py`; put the output in `## Wirtschaftlichkeit`.
5. Check the K.O. criteria from the Suchprofil and set `status` accordingly.
6. Tell the user what is missing before this can be judged.

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

### Decision (bid, walk away, sign)
Write a decision note in `60-Entscheidungen/` from
`assets/templates/entscheidung.md`: context, options considered, decision,
reasoning, assumptions it rests on, and what would reverse it. Link it from the
property note. This is the record the user will re-read in a year.

## References

Read the one you need; do not preload all of them.

| File | Read it when |
|---|---|
| `references/vault-structure.md` | Setting up or reorganising the vault |
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
| `scripts/vault_scan.py` | Index all property notes → table / JSON / summary. Cheap context loading. |
| `scripts/property_calc.py` | All purchase and financing math. Deterministic, shows its formulas. |
| `scripts/init_vault.py` | Scaffold folder structure, Suchprofil and dashboards in an empty vault. |

Run them with `python3`. They only need the standard library (PyYAML is used if
present, otherwise a built-in flat-YAML parser handles the schema).
