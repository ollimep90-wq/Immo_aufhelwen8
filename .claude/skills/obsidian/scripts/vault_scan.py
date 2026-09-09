#!/usr/bin/env python3
"""Index the property notes of an Obsidian vault.

Cheap way to load the whole picture into context before answering anything:

    python3 vault_scan.py /pfad/zum/vault --table
    python3 vault_scan.py /pfad/zum/vault --json
    python3 vault_scan.py /pfad/zum/vault --id OBJ-2026-001 --long

Reads frontmatter only (plus a count of open checkboxes), never writes.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frontmatter import (as_number, field, load_profile, note_tags,  # noqa: E402
                         read_note)

SKIP_DIRS = {".obsidian", ".trash", ".git", "node_modules", ".smart-env",
             "Vorlagen", "Templates", "_templates"}  # Vorlagen sind keine Objekte

# fields whose absence blocks a serious assessment
CRITICAL = ["living_area_m2", "year_built", "bundesland", "energy_value_kwh_m2a",
            "heating_year", "condition"]


def iter_notes(root: Path):
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def is_object(rel: str, fm: dict[str, Any], tags: set[str],
              profile: dict[str, Any]) -> bool:
    """Does this note describe a property? With a profile, the vault's own
    conventions decide; without one, the skill's `type: objekt`."""
    if not profile:
        return fm.get("type") == "objekt"
    folder = profile.get("objects_folder")
    if folder is not None and (folder == "" or rel.startswith(str(folder) + "/")):
        return True
    if fm.get("type") in set(profile.get("object_type_values") or []):
        return True
    if tags & set(profile.get("object_tags") or []):
        return True
    return fm.get("type") == "objekt"


def load(root: Path, profile: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for path in iter_notes(root):
        try:
            fm, body = read_note(path)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"# übersprungen: {path} ({exc})", file=sys.stderr)
            continue
        rel = str(path.relative_to(root))
        tags = note_tags(fm, body[:4000])
        if not fm.get("type") and not is_object(rel, fm, tags, profile):
            continue
        fm["_path"] = rel
        fm["_is_object"] = is_object(rel, fm, tags, profile)
        fm["_open_tasks"] = body.count("- [ ]")
        fm["_archived"] = path.parts[len(root.parts)].startswith("99")
        records.append(fm)
    return records


def derived(rec: dict[str, Any], profile: dict[str, Any] | None = None
            ) -> dict[str, Any]:
    price = as_number(field(rec, "price_agreed", profile)
                      or field(rec, "price_offered", profile)
                      or field(rec, "price_asking", profile))
    area = as_number(field(rec, "living_area_m2", profile))
    rent = as_number(field(rec, "rent_cold_month", profile))
    out = {
        "price": price,
        "area": area,
        "eur_m2": price / area if price and area else None,
        "rent": rent,
        "factor": price / (rent * 12) if price and rent else None,
        "missing": [f for f in CRITICAL if field(rec, f, profile) in (None, "")],
    }
    return out


def fmt(value: Any, width: int, decimals: int = 0, align: str = ">") -> str:
    if value is None or value == "":
        text = "—"
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        text = f"{value:,.{decimals}f}"
        text = text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    else:
        text = str(value)
    if len(text) > width:
        text = text[: width - 1] + "…"
    return f"{text:{align}{width}}"


def table(objects: list[dict[str, Any]], profile: dict[str, Any] | None = None) -> str:
    head = (f"{'ID':<14}{'Status':<14}{'Ort':<18}{'Preis':>11}{'m²':>7}"
            f"{'€/m²':>8}{'Miete':>8}{'Faktor':>8}{'Lücken':>8}{'ToDo':>6}")
    rows = [head, "-" * len(head)]
    for rec in objects:
        d = derived(rec, profile)
        rows.append(
            fmt(field(rec, "id", profile) or Path(rec["_path"]).stem, 14, align="<")
            + fmt(field(rec, "status", profile), 14, align="<")
            + fmt(field(rec, "city", profile) or field(rec, "title", profile), 18,
                  align="<")
            + fmt(d["price"], 11)
            + fmt(d["area"], 7)
            + fmt(d["eur_m2"], 8)
            + fmt(d["rent"], 8)
            + fmt(d["factor"], 8, 1)
            + fmt(len(d["missing"]) or None, 8)
            + fmt(rec.get("_open_tasks") or None, 6))
    return "\n".join(rows)


def long_form(rec: dict[str, Any], profile: dict[str, Any] | None = None) -> str:
    d = derived(rec, profile)
    label = field(rec, "id", profile) or Path(rec["_path"]).stem
    lines = [f"### {label} — {field(rec, 'title', profile) or rec['_path']}",
             f"Datei: {rec['_path']}"]
    shown: set[str] = set()
    for key in ("status", "data_asof", "property_type", "usage_intent", "street",
                "zip", "city", "district", "bundesland", "living_area_m2",
                "plot_area_m2", "rooms", "year_built", "condition",
                "energy_value_kwh_m2a", "energy_class", "heating_type",
                "heating_year", "price_asking", "price_offered", "price_agreed",
                "commission_pct", "hausgeld_month", "grundsteuer_year",
                "rent_cold_month", "rented", "sources"):
        value = field(rec, key, profile)
        if value not in (None, ""):
            mapped = (profile or {}).get("field_map", {}).get(key)
            shown.add(mapped or key)
            origin = f"  [{mapped}]" if mapped and mapped != key else ""
            lines.append(f"  {key}: {value}{origin}")
    extra = [k for k in rec
             if not k.startswith("_") and k not in shown and k != "type"]
    if extra:
        lines.append(f"  weitere Felder in der Notiz: {', '.join(sorted(extra))}")
    if d["eur_m2"]:
        lines.append(f"  → €/m²: {d['eur_m2']:,.0f}".replace(",", "."))
    if d["factor"]:
        lines.append(f"  → Kaufpreisfaktor: {d['factor']:.1f}")
    if d["missing"]:
        lines.append(f"  ⚠️ fehlt: {', '.join(d['missing'])}")
    if rec.get("_open_tasks"):
        lines.append(f"  ☐ offene Aufgaben in der Notiz: {rec['_open_tasks']}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("vault", help="Pfad zum Vault-Wurzelverzeichnis")
    p.add_argument("--type", default="objekt",
                   help="Notiztyp (Standard: objekt; 'alle' für alles)")
    p.add_argument("--status", help="nur dieser Status")
    p.add_argument("--id", help="nur dieses Objekt (impliziert --long)")
    p.add_argument("--include-archived", action="store_true")
    p.add_argument("--profile", help="Pfad zum Vault-Profil; ohne Angabe wird "
                                     "im Vault und in ~/.config/claude-obsidian gesucht")
    p.add_argument("--table", action="store_true", help="Tabelle (Standard)")
    p.add_argument("--long", action="store_true", help="alle Felder je Objekt")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    root = Path(args.vault).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"Kein Verzeichnis: {root}")
    if not (root / ".obsidian").exists():
        print(f"# Hinweis: {root} enthält kein .obsidian/ — sicher der Vault?",
              file=sys.stderr)

    profile = load_profile(args.profile, vault=root)
    if profile:
        print(f"# Vault-Profil: {profile.get('_path')}", file=sys.stderr)

    records = load(root, profile)
    if args.type == "objekt":
        records = [r for r in records if r.get("_is_object")]
    elif args.type != "alle":
        records = [r for r in records if r.get("type") == args.type]
    if args.status:
        records = [r for r in records
                   if field(r, "status", profile) == args.status]
    if args.id:
        records = [r for r in records
                   if field(r, "id", profile) == args.id
                   or Path(r["_path"]).stem == args.id]
        args.long = True
    if not args.include_archived and not args.id:
        records = [r for r in records if not r.get("_archived")]

    records.sort(key=lambda r: str(field(r, "id", profile) or r.get("_path")))

    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False, default=str))
        return 0
    if not records:
        print("Keine passenden Notizen gefunden.")
        return 0
    if args.long:
        print("\n\n".join(long_form(r, profile) for r in records))
        return 0

    print(table(records, profile))
    print()
    by_status: dict[str, int] = {}
    for rec in records:
        key = str(field(rec, "status", profile) or "ohne Status")
        by_status[key] = by_status.get(key, 0) + 1
    print(f"{len(records)} Objekte — "
          + ", ".join(f"{k}: {v}" for k, v in sorted(by_status.items())))
    gaps = [field(r, "id", profile) or Path(r["_path"]).stem
            for r in records if derived(r, profile)["missing"]]
    if gaps:
        print("Unvollständige Datensätze (Spalte 'Lücken'): " + ", ".join(map(str, gaps)))
        print("→ Vor jeder Bewertung die fehlenden Angaben klären.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
