# Vault structure

> **This layout is a proposal for a NEW vault.** If the user already has one,
> it is not the target: run `scripts/vault_profile.py`, adopt the folders and
> field names that are there, and use this page only to fill genuine gaps.
> Nothing existing gets renamed or moved.

Numbered folders so the sort order in Obsidian's file explorer stays meaningful.
Folder names are German (vault-facing content); the numbering makes them stable
even if the user renames them later — always resolve folders by their number
prefix (`10-*`), not by the exact German word.

```
<vault>/
├── 00-Inbox/                      # unsorted captures, links, screenshots
├── 10-Objekte/
│   └── OBJ-2026-001 Musterstr 1, Musterstadt/
│       ├── OBJ-2026-001.md        # the property note (the single source of truth)
│       ├── Besichtigungen/
│       │   └── 2026-03-14 Besichtigung.md
│       ├── Dokumente/             # Exposé, Grundbuchauszug, Teilungserklärung,
│       │   │                      # Protokolle, Energieausweis, Wirtschaftsplan …
│       │   └── 2026-03-02 Teilungserklaerung.md   # note *about* the PDF
│       └── Finanzierung/
│           └── Szenario-Basis.md  # assumptions, never facts
├── 20-Standorte/                  # Ort / Stadtteil research, Mietspiegel, Lage
├── 30-Kontakte/                   # Makler, Verkäufer, Bank, Notar, Gutachter, Handwerker
├── 40-Finanzierung/               # bank offers, Eigenkapital, Finanzierungsrahmen
├── 50-Wissen/                     # checklists, law/tax notes, lessons learned
├── 60-Entscheidungen/             # decision notes (one per real decision)
├── 90-Meta/
│   ├── Suchprofil.md              # criteria, K.O. list, budget ceiling, weights
│   ├── Finanzierungsrahmen.md     # equity, income, what the bank said
│   ├── Dashboard.md               # Dataview overview
│   └── Vorlagen/                  # Obsidian template files
└── 99-Archiv/                     # rejected / sold objects, kept for the record
```

## Rules

- **One folder per property**, named `OBJ-YYYY-NNN <Straße Hausnr, Ort>`.
  The main note inside is named exactly `OBJ-YYYY-NNN.md` so links are stable even
  when the address is corrected later. Give it a `title` in frontmatter and a
  human-readable `aliases` entry so `[[Musterstr 1]]` resolves.
- **Ids are never reused**, including for rejected objects. A rejected object moves
  to `99-Archiv/` with `status: rejected` — it is not deleted. Knowing what you
  turned down and why is part of the decision record.
- **PDFs and photos** go in the object's `Dokumente/` folder. Obsidian handles
  binaries fine, but a PDF is not searchable knowledge: for every important
  document, write a short note *about* it (what it says, which figures it confirms,
  which page) next to it, and cite that note as the source.
- **Do not put figures only in the folder name or the filename.** Everything
  queryable lives in frontmatter.

## Adopting an existing vault

```bash
python3 .claude/skills/obsidian/scripts/vault_profile.py "$VAULT"
```

Read-only. It reports:

- the folders whose notes look property-related, ranked by how many notes hit the
  domain vocabulary (Kaufpreis, Hausgeld, Teilungserklärung, Grunderwerbsteuer …)
- the `type` values and tags actually in use, so object notes can be recognised
  the way the vault already marks them
- Obsidian's own settings: template folder, attachment folder, whether Dataview is
  installed
- a proposed `field_map` from this skill's canonical fields onto the user's real
  frontmatter keys, plus everything it could **not** map

Go through the proposal with the user — in particular the conflicts, where one of
their keys matched two skill fields (`stand` fits both `data_asof` and `status`;
only one can be right). Then save it:

```bash
python3 .claude/skills/obsidian/scripts/vault_profile.py "$VAULT" \
    --write ~/.config/claude-obsidian/vault-profile.md
```

`vault_scan.py` and `property_calc.py` take `--profile` and then read the vault in
its own vocabulary. Re-run the analysis after the vault's structure changes.

## Scaffolding an empty vault

```bash
python3 .claude/skills/obsidian/scripts/init_vault.py "$VAULT"
```

Refuses to run when the vault already contains notes outside these folders —
that refusal is the point, not an obstacle. Creates the folders,
`90-Meta/Suchprofil.md`, `90-Meta/Finanzierungsrahmen.md`,
`90-Meta/Dashboard.md` and copies the templates into `90-Meta/Vorlagen/`.
It never overwrites an existing file (`--force` to allow it).

Afterwards, in Obsidian: Settings → Files & links → *Default location for new
notes* = `00-Inbox`, and *Template folder location* = `90-Meta/Vorlagen` (core
Templates plugin). Recommended community plugin: **Dataview** — the dashboards in
`references/dataview.md` need it.
