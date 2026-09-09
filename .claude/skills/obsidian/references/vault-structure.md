# Vault structure

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

## Scaffolding an empty vault

```bash
python3 .claude/skills/obsidian/scripts/init_vault.py "$VAULT"
```

Creates the folders, `90-Meta/Suchprofil.md`, `90-Meta/Finanzierungsrahmen.md`,
`90-Meta/Dashboard.md` and copies the templates into `90-Meta/Vorlagen/`.
It never overwrites an existing file (`--force` to allow it).

Afterwards, in Obsidian: Settings → Files & links → *Default location for new
notes* = `00-Inbox`, and *Template folder location* = `90-Meta/Vorlagen` (core
Templates plugin). Recommended community plugin: **Dataview** — the dashboards in
`references/dataview.md` need it.
