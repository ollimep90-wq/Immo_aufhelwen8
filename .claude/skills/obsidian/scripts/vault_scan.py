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
from frontmatter import as_number, read_note  # noqa: E402

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


def load(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in iter_notes(root):
        try:
            fm, body = read_note(path)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"# übersprungen: {path} ({exc})", file=sys.stderr)
            continue
        if not fm.get("type"):
            continue
        fm["_path"] = str(path.relative_to(root))
        fm["_open_tasks"] = body.count("- [ ]")
        fm["_archived"] = path.parts[len(root.parts)].startswith("99")
        records.append(fm)
    return records


def derived(rec: dict[str, Any]) -> dict[str, Any]:
    price = as_number(rec.get("price_agreed") or rec.get("price_offered")
                      or rec.get("price_asking"))
    area = as_number(rec.get("living_area_m2"))
    rent = as_number(rec.get("rent_cold_month"))
    out = {
        "price": price,
        "area": area,
        "eur_m2": price / area if price and area else None,
        "rent": rent,
        "factor": price / (rent * 12) if price and rent else None,
        "missing": [f for f in CRITICAL if rec.get(f) in (None, "")],
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


def table(objects: list[dict[str, Any]]) -> str:
    head = (f"{'ID':<14}{'Status':<14}{'Ort':<18}{'Preis':>11}{'m²':>7}"
            f"{'€/m²':>8}{'Miete':>8}{'Faktor':>8}{'Lücken':>8}{'ToDo':>6}")
    rows = [head, "-" * len(head)]
    for rec in objects:
        d = derived(rec)
        rows.append(
            fmt(rec.get("id"), 14, align="<")
            + fmt(rec.get("status"), 14, align="<")
            + fmt(rec.get("city") or rec.get("title"), 18, align="<")
            + fmt(d["price"], 11)
            + fmt(d["area"], 7)
            + fmt(d["eur_m2"], 8)
            + fmt(d["rent"], 8)
            + fmt(d["factor"], 8, 1)
            + fmt(len(d["missing"]) or None, 8)
            + fmt(rec.get("_open_tasks") or None, 6))
    return "\n".join(rows)


def long_form(rec: dict[str, Any]) -> str:
    d = derived(rec)
    lines = [f"### {rec.get('id')} — {rec.get('title') or rec.get('_path')}",
             f"Datei: {rec['_path']}"]
    for key in ("status", "data_asof", "property_type", "usage_intent", "street",
                "zip", "city", "district", "bundesland", "living_area_m2",
                "plot_area_m2", "rooms", "year_built", "condition",
                "energy_value_kwh_m2a", "energy_class", "heating_type",
                "heating_year", "price_asking", "price_offered", "price_agreed",
                "commission_pct", "hausgeld_month", "grundsteuer_year",
                "rent_cold_month", "rented", "sources"):
        if rec.get(key) not in (None, ""):
            lines.append(f"  {key}: {rec[key]}")
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

    records = load(root)
    if args.type != "alle":
        records = [r for r in records if r.get("type") == args.type]
    if args.status:
        records = [r for r in records if r.get("status") == args.status]
    if args.id:
        records = [r for r in records if r.get("id") == args.id]
        args.long = True
    if not args.include_archived and not args.id:
        records = [r for r in records if not r.get("_archived")]

    records.sort(key=lambda r: str(r.get("id") or r.get("_path")))

    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False, default=str))
        return 0
    if not records:
        print("Keine passenden Notizen gefunden.")
        return 0
    if args.long:
        print("\n\n".join(long_form(r) for r in records))
        return 0

    print(table(records))
    print()
    by_status: dict[str, int] = {}
    for rec in records:
        by_status[str(rec.get("status") or "ohne Status")] = \
            by_status.get(str(rec.get("status") or "ohne Status"), 0) + 1
    print(f"{len(records)} Objekte — "
          + ", ".join(f"{k}: {v}" for k, v in sorted(by_status.items())))
    gaps = [r.get("id") for r in records if derived(r)["missing"]]
    if gaps:
        print("Unvollständige Datensätze (Spalte 'Lücken'): " + ", ".join(map(str, gaps)))
        print("→ Vor jeder Bewertung die fehlenden Angaben klären.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
