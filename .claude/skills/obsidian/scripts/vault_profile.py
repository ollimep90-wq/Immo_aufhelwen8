#!/usr/bin/env python3
"""Analyse an EXISTING Obsidian vault and propose a mapping onto the skill.

The skill has canonical field names, but the vault belongs to the user. This
script reads the vault, reports how it is actually organised, and proposes a
profile that maps the skill's canonical fields onto the user's real ones. Nothing
in the vault is renamed, moved or written unless --write is given.

    python3 vault_profile.py /pfad/zum/vault              # nur Bericht
    python3 vault_profile.py /pfad/zum/vault --json
    python3 vault_profile.py /pfad/zum/vault --write ~/.config/claude-obsidian/vault-profile.md

Read-only by default. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frontmatter import read_note  # noqa: E402

SKIP_DIRS = {".obsidian", ".trash", ".git", "node_modules", ".smart-env", ".stfolder"}
MAX_BYTES = 400_000

# Words that suggest a note is about buying property. Lowercased, matched against
# frontmatter keys, the filename and the first part of the body.
SIGNALS = [
    "kaufpreis", "wohnfläche", "wohnflaeche", "hausgeld", "exposé", "expose",
    "makler", "grundbuch", "teilungserklärung", "teilungserklaerung",
    "energieausweis", "besichtigung", "grunderwerbsteuer", "eigentümerversammlung",
    "eigentuemerversammlung", "nebenkosten", "immobilie", "eigentumswohnung",
    "kaltmiete", "erbbau", "bebauungsplan", "notartermin", "zinsbindung",
    "annuität", "annuitaet", "tilgung", "beleihung", "objekt", "grundriss",
    "instandhaltung", "wirtschaftsplan", "baujahr", "quadratmeter",
]

# canonical skill field -> candidate key names as they may appear in the vault
ALIASES: dict[str, list[str]] = {
    "id": ["id", "objekt_id", "objektnummer", "nummer", "kennung"],
    "title": ["title", "titel", "name", "bezeichnung"],
    "status": ["status", "phase", "stand", "zustand_prozess"],
    "street": ["street", "strasse", "straße", "adresse", "anschrift"],
    "zip": ["zip", "plz", "postleitzahl"],
    "city": ["city", "ort", "stadt", "gemeinde"],
    "district": ["district", "stadtteil", "ortsteil", "viertel", "bezirk"],
    "bundesland": ["bundesland", "state", "land"],
    "property_type": ["property_type", "objektart", "typ", "art", "immobilientyp"],
    "usage_intent": ["usage_intent", "nutzung", "verwendung", "nutzungsart"],
    "living_area_m2": ["living_area_m2", "wohnflaeche", "wohnfläche", "flaeche",
                       "fläche", "qm", "m2", "quadratmeter", "size"],
    "plot_area_m2": ["plot_area_m2", "grundstueck", "grundstück",
                     "grundstuecksflaeche", "grundstücksfläche"],
    "rooms": ["rooms", "zimmer", "zimmeranzahl", "anzahl_zimmer"],
    "floor": ["floor", "etage", "geschoss", "stockwerk"],
    "year_built": ["year_built", "baujahr", "bj", "erbaut"],
    "year_renovated": ["year_renovated", "sanierung", "saniert", "modernisiert",
                       "letzte_sanierung"],
    "condition": ["condition", "zustand"],
    "energy_value_kwh_m2a": ["energy_value_kwh_m2a", "energiekennwert",
                             "energieverbrauch", "energiebedarf", "kwh"],
    "energy_class": ["energy_class", "energieklasse", "effizienzklasse"],
    "heating_type": ["heating_type", "heizung", "heizungsart", "heizart"],
    "heating_year": ["heating_year", "heizung_baujahr", "heizung_bj",
                     "heizungsalter"],
    "price_asking": ["price_asking", "kaufpreis", "preis", "angebotspreis",
                     "kaufpreis_angebot"],
    "price_offered": ["price_offered", "gebot", "angebot", "mein_gebot"],
    "price_agreed": ["price_agreed", "kaufpreis_vereinbart", "endpreis",
                     "vereinbarter_preis"],
    "commission_pct": ["commission_pct", "provision", "maklerprovision",
                       "courtage"],
    "hausgeld_month": ["hausgeld_month", "hausgeld", "wohngeld"],
    "grundsteuer_year": ["grundsteuer_year", "grundsteuer"],
    "rent_cold_month": ["rent_cold_month", "kaltmiete", "nettokaltmiete", "miete",
                        "mieteinnahmen"],
    "rented": ["rented", "vermietet"],
    "listing_url": ["listing_url", "url", "link", "inserat", "exposé_url"],
    "data_asof": ["data_asof", "stand", "aktualisiert", "updated"],
    "sources": ["sources", "quelle", "quellen"],
}

CANONICAL_TYPES = {
    "objekt": ["objekt", "immobilie", "property", "objekte", "wohnung", "haus",
               "kaufobjekt"],
    "besichtigung": ["besichtigung", "viewing", "termin"],
    "kontakt": ["kontakt", "contact", "person"],
    "dokument": ["dokument", "document", "unterlage"],
    "entscheidung": ["entscheidung", "decision"],
    "standort": ["standort", "lage", "ort", "location"],
}

TAG_RE = re.compile(r"(?<![\w/#])#([A-Za-zÄÖÜäöüß][\w/\-äöüÄÖÜß]*)")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def obsidian_config(root: Path) -> dict[str, Any]:
    cfg_dir = root / ".obsidian"
    out: dict[str, Any] = {"present": cfg_dir.is_dir()}
    if not out["present"]:
        return out
    app = read_json(cfg_dir / "app.json") or {}
    out["new_file_location"] = app.get("newFileLocation")
    out["new_file_folder"] = app.get("newFileFolderPath")
    out["attachment_folder"] = app.get("attachmentFolderPath")
    templates = read_json(cfg_dir / "templates.json") or {}
    out["templates_folder"] = templates.get("folder")
    daily = read_json(cfg_dir / "daily-notes.json") or {}
    out["daily_folder"] = daily.get("folder")
    out["community_plugins"] = read_json(cfg_dir / "community-plugins.json") or []
    for key in ("dataview", "templater-obsidian", "obsidian-tasks-plugin",
                "obsidian-local-rest-api"):
        out[f"has_{key}"] = key in out["community_plugins"]
    return out


def scan(root: Path) -> dict[str, Any]:
    notes: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            fm, body = read_note(path)
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(root)
        haystack = " ".join([
            str(rel).lower(),
            " ".join(str(k).lower() for k in fm),
            " ".join(str(v).lower() for v in fm.values() if isinstance(v, str)),
            body[:4000].lower(),
        ])
        score = sum(1 for word in SIGNALS if word in haystack)
        tags = set()
        raw_tags = fm.get("tags")
        if isinstance(raw_tags, str):
            tags.update(t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip())
        elif isinstance(raw_tags, list):
            tags.update(str(t).lstrip("#") for t in raw_tags)
        tags.update(TAG_RE.findall(body[:4000]))
        notes.append({
            "path": str(rel), "dir": str(rel.parent) if str(rel.parent) != "." else "",
            "top": rel.parts[0] if len(rel.parts) > 1 else "",
            "fm": fm, "type": fm.get("type"), "tags": sorted(tags),
            "score": score, "has_fm": bool(fm),
        })
    return {"notes": notes}


def analyse(root: Path) -> dict[str, Any]:
    data = scan(root)
    notes = data["notes"]
    cfg = obsidian_config(root)

    key_counter: Counter[str] = Counter()
    type_counter: Counter[str] = Counter()
    tag_counter: Counter[str] = Counter()
    dir_notes: dict[str, int] = defaultdict(int)
    dir_score: dict[str, int] = defaultdict(int)
    dir_hits: dict[str, int] = defaultdict(int)

    for note in notes:
        for key in note["fm"]:
            key_counter[str(key)] += 1
        if note["type"]:
            type_counter[str(note["type"])] += 1
        for tag in note["tags"]:
            tag_counter[tag] += 1
        dir_notes[note["dir"]] += 1
        dir_score[note["dir"]] += note["score"]
        if note["score"] >= 3:
            dir_hits[note["dir"]] += 1

    candidates = sorted(
        ({"dir": d, "notes": dir_notes[d], "treffer": dir_hits[d],
          "score": dir_score[d]} for d in dir_notes if dir_hits[d]),
        key=lambda c: (c["treffer"], c["score"]), reverse=True)

    objects_dir = candidates[0]["dir"] if candidates else None

    # which frontmatter keys are used inside the likely object folder
    in_scope_keys: Counter[str] = Counter()
    for note in notes:
        if objects_dir is not None and not note["dir"].startswith(objects_dir):
            continue
        if note["score"] < 3:
            continue
        for key in note["fm"]:
            in_scope_keys[str(key)] += 1

    lookup = {k.lower(): k for k in (in_scope_keys or key_counter)}
    field_map: dict[str, str] = {}
    ambiguous: dict[str, list[str]] = {}
    rank: dict[str, int] = {}  # canonical -> how specific the match was
    for canonical, names in ALIASES.items():
        hits, positions = [], []
        for position, name in enumerate(names):
            if name in lookup and lookup[name] not in hits:
                hits.append(lookup[name])
                positions.append(position)
        if not hits:
            continue
        field_map[canonical] = hits[0]
        rank[canonical] = positions[0]
        if len(hits) > 1:
            ambiguous[canonical] = hits

    # One vault key must not stand for two different canonical fields. Keep the
    # more specific match (earlier in the alias list) and report the rest instead
    # of silently producing a wrong mapping.
    conflicts: dict[str, list[str]] = {}
    owners: dict[str, list[str]] = defaultdict(list)
    for canonical, actual in field_map.items():
        owners[actual].append(canonical)
    for actual, claimants in owners.items():
        if len(claimants) < 2:
            continue
        winner = sorted(claimants, key=lambda c: (rank[c], c))[0]
        conflicts[actual] = sorted(claimants)
        for loser in claimants:
            if loser != winner:
                del field_map[loser]

    type_values: list[str] = []
    for value, _ in type_counter.most_common():
        if any(alias in value.lower() for alias in CANONICAL_TYPES["objekt"]):
            type_values.append(value)
    # A tag counts as an object tag only if its LAST segment names an object and
    # no segment names a different note type — otherwise #hauskauf/besichtigung
    # would later make viewing notes look like properties.
    other_type_words = {w for key, words in CANONICAL_TYPES.items()
                        if key != "objekt" for w in words}
    object_tags = []
    for tag, _ in tag_counter.most_common():
        segments = [seg.lower() for seg in tag.split("/")]
        if any(seg in other_type_words for seg in segments):
            continue
        if any(alias in segments[-1] for alias in CANONICAL_TYPES["objekt"]):
            object_tags.append(tag)
    object_tags = object_tags[:5]

    return {
        "vault": str(root),
        "note_count": len(notes),
        "notes_with_frontmatter": sum(1 for n in notes if n["has_fm"]),
        "obsidian": cfg,
        "top_level_folders": sorted({n["top"] for n in notes if n["top"]}),
        "object_folder_candidates": candidates[:8],
        "objects_folder": objects_dir,
        "object_type_values": type_values,
        "object_tags": object_tags,
        "all_types": type_counter.most_common(15),
        "top_tags": tag_counter.most_common(15),
        "frontmatter_keys": key_counter.most_common(40),
        "keys_in_object_notes": in_scope_keys.most_common(40),
        "field_map": field_map,
        "unmapped_note": None,
        "ambiguous": ambiguous,
        "conflicts": conflicts,
        "unmapped_canonical": [c for c in ALIASES if c not in field_map],
    }


def report(a: dict[str, Any]) -> str:
    lines = [f"Vault: {a['vault']}",
             f"{a['note_count']} Notizen, davon {a['notes_with_frontmatter']} mit Frontmatter",
             ""]
    cfg = a["obsidian"]
    if cfg.get("present"):
        lines.append("Obsidian-Konfiguration:")
        for label, key in (("neue Notizen", "new_file_folder"),
                           ("Vorlagenordner", "templates_folder"),
                           ("Anhänge", "attachment_folder"),
                           ("Daily Notes", "daily_folder")):
            if cfg.get(key):
                lines.append(f"  {label}: {cfg[key]}")
        plugins = [p for p in ("dataview", "templater-obsidian",
                               "obsidian-tasks-plugin", "obsidian-local-rest-api")
                   if cfg.get(f"has_{p}")]
        lines.append(f"  relevante Plugins: {', '.join(plugins) if plugins else 'keine der geprüften'}")
        if not cfg.get("has_dataview"):
            lines.append("  ⚠️ Dataview ist nicht installiert — die Dashboards "
                         "des Skills funktionieren erst danach.")
    else:
        lines.append("⚠️ Kein .obsidian/ gefunden — ist das wirklich der Vault?")
    lines.append("")

    lines.append("Ordner mit Immobilien-Bezug (Treffer = Notizen mit ≥3 Signalwörtern):")
    if a["object_folder_candidates"]:
        for c in a["object_folder_candidates"]:
            lines.append(f"  {c['treffer']:>4} von {c['notes']:>4} Notizen   "
                         f"{c['dir'] or '(Vault-Wurzel)'}")
    else:
        lines.append("  keine gefunden — Objektordner bitte selbst benennen")
    lines.append("")

    if a["all_types"]:
        lines.append("Vorhandene type-Werte: "
                     + ", ".join(f"{v} ({n})" for v, n in a["all_types"]))
    if a["top_tags"]:
        lines.append("Häufigste Tags: "
                     + ", ".join(f"#{v} ({n})" for v, n in a["top_tags"][:10]))
    lines.append(f"Objektnotizen erkannt über: type "
                 f"{a['object_type_values'] or '—'}, Tags "
                 f"{['#' + t for t in a['object_tags']] or '—'}, Ordner "
                 f"{a['objects_folder'] if a['objects_folder'] is not None else '—'}")
    lines.append("")

    lines.append("Feldzuordnung (Skill-Feld → dein Feld):")
    for canonical, actual in sorted(a["field_map"].items()):
        note = ""
        if canonical in a["ambiguous"]:
            note = f"   ⚠️ mehrdeutig, auch möglich: {', '.join(a['ambiguous'][canonical][1:])}"
        lines.append(f"  {canonical:<22} → {actual}{note}")
    if not a["field_map"]:
        lines.append("  keine bekannten Feldnamen erkannt")
    lines.append("")
    if a["conflicts"]:
        lines.append("⚠️ Ein Feld deines Vaults passte auf mehrere Skill-Felder — "
                     "nur die spezifischere Zuordnung wurde übernommen:")
        for actual, claimants in sorted(a["conflicts"].items()):
            kept = [c for c in claimants if a["field_map"].get(c) == actual]
            dropped = [c for c in claimants if c not in kept]
            lines.append(f"  `{actual}` → {kept[0] if kept else '—'} "
                         f"(verworfen: {', '.join(dropped)})")
        lines.append("  Bitte bestätigen — sonst rechnet der Skill mit dem falschen Feld.")
        lines.append("")
    if a["unmapped_canonical"]:
        lines.append("Ohne Entsprechung im Vault (der Skill fragt danach, statt zu raten):")
        lines.append("  " + ", ".join(a["unmapped_canonical"]))
        lines.append("")

    lines.append("Nichts wurde verändert. Vorschlag prüfen, dann mit --write "
                 "als Profil speichern.")
    return "\n".join(lines)


def profile_note(a: dict[str, Any]) -> str:
    fm = ["---", "type: vault-profil", f"vault_path: {a['vault']}",
          f"generated: {date.today().isoformat()}"]
    if a["objects_folder"] is not None:
        fm.append(f"objects_folder: \"{a['objects_folder']}\"")
    if a["obsidian"].get("templates_folder"):
        fm.append(f"templates_folder: \"{a['obsidian']['templates_folder']}\"")
    if a["obsidian"].get("attachment_folder"):
        fm.append(f"attachments_folder: \"{a['obsidian']['attachment_folder']}\"")
    fm.append(f"dataview: {str(bool(a['obsidian'].get('has_dataview'))).lower()}")
    if a["object_type_values"]:
        fm.append("object_type_values:")
        fm += [f"  - {v}" for v in a["object_type_values"]]
    if a["object_tags"]:
        fm.append("object_tags:")
        fm += [f"  - {v}" for v in a["object_tags"]]
    fm.append("field_map:")
    for canonical, actual in sorted(a["field_map"].items()):
        fm.append(f"  {canonical}: {actual}")
    fm.append("---")

    body = ["", "# Vault-Profil", "",
            "> [!info] Von `vault_profile.py` vorgeschlagen, vom Nutzer bestätigt.",
            "> Der Skill liest dieses Profil und arbeitet damit in der bestehenden",
            "> Struktur des Vaults. Bei Änderungen am Vault erneut erzeugen oder",
            "> das Frontmatter oben von Hand anpassen.", "",
            "## Erkannt", ""]
    body.append(f"- Notizen gesamt: {a['note_count']}")
    if a["objects_folder"] is not None:
        body.append(f"- Objektordner: `{a['objects_folder'] or '(Vault-Wurzel)'}`")
    if a["object_folder_candidates"]:
        body.append("- Weitere Kandidaten: "
                    + ", ".join(f"`{c['dir'] or '(Wurzel)'}` ({c['treffer']})"
                                for c in a["object_folder_candidates"][1:4]))
    body += ["", "## Zu klären", ""]
    if a["ambiguous"]:
        for canonical, hits in sorted(a["ambiguous"].items()):
            body.append(f"- [ ] `{canonical}`: gewählt `{hits[0]}`, "
                        f"ebenfalls vorhanden {', '.join(f'`{h}`' for h in hits[1:])}")
    for actual, claimants in sorted(a["conflicts"].items()):
        kept = [c for c in claimants if a["field_map"].get(c) == actual]
        body.append(f"- [ ] `{actual}` passte auf {', '.join(claimants)} — "
                    f"übernommen als `{kept[0] if kept else '—'}`. Stimmt das?")
    if a["unmapped_canonical"]:
        body.append("- [ ] Ohne Entsprechung: "
                    + ", ".join(f"`{c}`" for c in a["unmapped_canonical"]))
        body.append("      → entweder im Vault ergänzen oder im Skill ignorieren.")
    if not a["ambiguous"] and not a["conflicts"] and not a["unmapped_canonical"]:
        body.append("- keine offenen Punkte")
    body += ["", "## Regeln für den Skill", "",
             "- Bestehende Ordner und Notizen werden **nicht** umbenannt oder verschoben.",
             "- Neue Notizen entstehen im Objektordner oben, nach der dort",
             "  vorhandenen Namenskonvention.",
             "- Fehlt ein Feld im `field_map`, wird danach gefragt statt geraten.", ""]
    return "\n".join(fm + body)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("vault")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", metavar="PFAD",
                   help="Profilnotiz hierhin schreiben (einzige Schreiboperation)")
    p.add_argument("--force", action="store_true", help="vorhandenes Profil ersetzen")
    args = p.parse_args()

    root = Path(args.vault).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"Kein Verzeichnis: {root}")

    result = analyse(root)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print(report(result))

    if args.write:
        target = Path(args.write).expanduser()
        if target.exists() and not args.force:
            raise SystemExit(f"\n{target} existiert bereits — --force zum Ersetzen.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(profile_note(result), encoding="utf-8")
        print(f"\nProfil geschrieben: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
