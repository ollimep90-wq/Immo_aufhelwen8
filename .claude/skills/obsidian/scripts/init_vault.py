#!/usr/bin/env python3
"""Scaffold the folder structure and the meta notes of a property vault.

    python3 init_vault.py /pfad/zum/vault [--dry-run] [--force]

Never overwrites an existing file unless --force is given. Creating the vault in
Obsidian itself (so that .obsidian/ exists) stays the user's job.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"

FOLDERS = [
    "00-Inbox",
    "10-Objekte",
    "20-Standorte",
    "30-Kontakte",
    "40-Finanzierung",
    "50-Wissen",
    "60-Entscheidungen",
    "90-Meta/Vorlagen",
    "99-Archiv",
]

# template file -> destination inside the vault
META_NOTES = {
    "suchprofil.md": "90-Meta/Suchprofil.md",
    "finanzierungsrahmen.md": "90-Meta/Finanzierungsrahmen.md",
    "dashboard.md": "90-Meta/Dashboard.md",
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("vault")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="bestehende Dateien überschreiben")
    args = p.parse_args()

    root = Path(args.vault).expanduser().resolve()
    if not TEMPLATES.is_dir():
        raise SystemExit(f"Vorlagenordner nicht gefunden: {TEMPLATES}")
    if not root.exists() and not args.dry_run:
        root.mkdir(parents=True)
        print(f"angelegt: {root}")
    if not (root / ".obsidian").exists():
        print("# Hinweis: kein .obsidian/ — den Ordner in Obsidian noch als Vault "
              "öffnen ('Open folder as vault').", file=sys.stderr)

    # Any note that lives outside the folders this script creates means the vault
    # already has a structure of its own. Adding a second one next to it is the
    # worst possible outcome, so refuse unless the user insists.
    own_folders = {f.split("/")[0] for f in FOLDERS}
    foreign = [q for q in root.rglob("*.md")
               if not {".obsidian", ".trash", ".git"} & set(q.parts)
               and q.relative_to(root).parts[0] not in own_folders]
    if foreign and not args.force and not args.dry_run:
        sample = ", ".join(str(q.relative_to(root)) for q in foreign[:3])
        raise SystemExit(
            f"Der Vault enthält bereits {len(foreign)} Notiz(en) außerhalb der "
            f"Skill-Ordner\n(z. B. {sample}).\n"
            "init_vault.py ist für einen leeren Vault gedacht und würde hier eine "
            "Parallelstruktur\nneben der bestehenden anlegen.\n\n"
            "Für einen bestehenden Vault stattdessen:\n"
            "    python3 vault_profile.py <vault>\n\n"
            "Wenn die Struktur wirklich zusätzlich entstehen soll: --force.")

    actions: list[str] = []

    for folder in FOLDERS:
        target = root / folder
        if target.exists():
            actions.append(f"vorhanden  {folder}/")
        else:
            actions.append(f"anlegen    {folder}/")
            if not args.dry_run:
                target.mkdir(parents=True)

    for name in sorted(p.name for p in TEMPLATES.glob("*.md")):
        target = root / "90-Meta" / "Vorlagen" / name
        if target.exists() and not args.force:
            actions.append(f"vorhanden  90-Meta/Vorlagen/{name}")
            continue
        actions.append(f"kopieren   90-Meta/Vorlagen/{name}")
        if not args.dry_run:
            shutil.copy2(TEMPLATES / name, target)

    today = date.today().isoformat()
    for template, destination in META_NOTES.items():
        target = root / destination
        if target.exists() and not args.force:
            actions.append(f"vorhanden  {destination}  (unverändert gelassen)")
            continue
        actions.append(f"anlegen    {destination}")
        if not args.dry_run:
            text = (TEMPLATES / template).read_text(encoding="utf-8")
            text = text.replace("updated:\n", f"updated: {today}\n", 1)
            target.write_text(text, encoding="utf-8")

    print("\n".join(actions))
    if args.dry_run:
        print("\n(dry run — nichts geschrieben)")
    else:
        print(f"\nFertig. Nächste Schritte:\n"
              f"  1. In Obsidian: Einstellungen → Dateien & Links → Standardort für "
              f"neue Notizen = 00-Inbox, Vorlagenordner = 90-Meta/Vorlagen\n"
              f"  2. Community-Plugin 'Dataview' installieren (für das Dashboard)\n"
              f"  3. {root / '90-Meta' / 'Suchprofil.md'} ausfüllen — "
              f"vor dem ersten Objekt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
