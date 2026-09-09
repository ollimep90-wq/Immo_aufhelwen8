# Obsidian syntax — what to use and what to avoid

Obsidian notes are plain Markdown files. Everything here is written directly into
the `.md` file; no plugin is needed except where marked.

## Properties (frontmatter)

A single YAML block, **first thing in the file**, fenced by `---`. Obsidian renders
it as the Properties panel. A blank line or any character before the opening `---`
turns it into ordinary text — a very common silent breakage.

```markdown
---
type: objekt
id: OBJ-2026-001
aliases:
  - Musterstr 1
tags:
  - objekt
price_asking: 485000
besichtigt_am: 2026-03-14
---
```

`tags` in frontmatter are written **without** `#`. Dates are unquoted `YYYY-MM-DD`.
Obsidian's own special keys are `tags`, `aliases`, `cssclasses`.

## Links

| Syntax | Meaning |
|---|---|
| `[[OBJ-2026-001]]` | link to a note |
| `[[OBJ-2026-001\|Musterstr 1]]` | link with display text |
| `[[OBJ-2026-001#Wirtschaftlichkeit]]` | link to a heading |
| `[[OBJ-2026-001#^ab12cd]]` | link to a block |
| `![[OBJ-2026-001#Wirtschaftlichkeit]]` | **embed** that section live |
| `![[Grundriss.pdf]]` | embed a PDF / image |
| `[[2026-03-14 Besichtigung]]` | any note, folders are not part of the link |

Links resolve by filename, not path — so **filenames must be unique across the
vault**. That is why every property note is `OBJ-YYYY-NNN.md` and carries the
address as `title`/`aliases`.

Inside frontmatter a link must be a quoted string: `makler: "[[Max Beispiel]]"`.

**Filenames:** avoid `* " \ / < > : | ? # ^ [ ]`. Umlauts and spaces are fine.
Stick to letters, digits, spaces, `-`, `,` and `.`.

## Blocks and anchors

Append `^ein-anker` at the end of a line or paragraph to make it linkable:

```markdown
Hausgeld 412 €/Monat, davon 95 € Rücklage (Wirtschaftsplan 2026). ^hausgeld
```

Use anchors for figures other notes need to cite — the citation then survives
edits elsewhere in the note.

## Callouts

```markdown
> [!warning] Erbbaurecht läuft 2041 aus
> Restlaufzeit 15 Jahre — Finanzierung über 20 Jahre wird schwierig.

> [!question]- Offene Fragen an den Makler
> Faltbar, weil das `-` hinter dem Typ steht.
```

Useful types: `note`, `info`, `tip`, `success`, `question`, `warning`, `failure`,
`danger`, `example`, `quote`. Use `warning`/`danger` for real risks only —
inflation makes them useless.

## Tasks

```markdown
- [ ] Teilungserklärung anfordern 📅 2026-03-20
- [x] Energieausweis erhalten
```

Plain checkboxes work everywhere; the `📅` date is only interpreted by the Tasks
plugin. Do not depend on it — the deadline also belongs in the note text.

## Inline fields (Dataview)

`key:: value` on its own line, or `(key:: value)` inline, is readable by Dataview
without being frontmatter. Use it for per-line facts inside a table; use
frontmatter for anything you want to sort or filter the whole vault by.

## Comments

`%% not rendered %%` — use for scratch notes you do not want in the reading view.
Do not hide caveats in comments; caveats belong in the visible text.

## Things to avoid

- **HTML** for layout — it breaks Reading view styling and mobile.
- **Renaming a note by writing a new file.** Obsidian updates backlinks on rename;
  a rewrite orphans them. If you rename from the shell, grep the vault for the old
  name and fix the links: `grep -rn "\[\[Alter Name" "$VAULT"`.
- **Editing `.obsidian/`** (app config, workspace, plugin data) unless the user
  explicitly asks. That directory is the app's state, not their content.
- **Very long single notes.** One property = one note plus subfolder notes.
