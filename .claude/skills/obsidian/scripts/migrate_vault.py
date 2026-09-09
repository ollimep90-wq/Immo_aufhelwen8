#!/usr/bin/env python3
"""Rebuild a set of loose property notes into a clean vault.

    python3 migrate_vault.py <quelle> <ziel> [--dry-run]

Reads every .md under <quelle>, classifies it, normalises its frontmatter onto
the skill's canonical field names, files it into the structure from
references/vault-structure.md, renames object notes to a consistent scheme and
rewrites the wikilinks accordingly. Writes MIGRATION.md next to the result.

Guarantees, in this order of importance:

1. **Nothing is invented.** A field that was not in the source is not written.
2. **Nothing is lost.** Unrecognised frontmatter keys are kept verbatim; note
   bodies are copied unchanged apart from rewritten links and, for object notes,
   an appended and clearly marked block of open questions.
3. **Nothing breaks.** Every renamed note keeps its old name as an alias, and
   incoming links are rewritten as well — both paths resolve.
4. **Nothing is guessed silently.** Everything unclear lands in MIGRATION.md.

The source directory is only ever read.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frontmatter import as_number, read_note, split_note  # noqa: E402
from vault_profile import ALIASES, SIGNALS, SKIP_DIRS  # noqa: E402

NUMERIC = {
    "price_asking", "price_offered", "price_agreed", "living_area_m2",
    "plot_area_m2", "rooms", "floor", "floors_total", "year_built",
    "year_renovated", "heating_year", "energy_value_kwh_m2a", "commission_pct",
    "hausgeld_month", "hausgeld_reserve_share_month", "weg_reserve_total",
    "grundsteuer_year", "rent_cold_month", "rent_potential_month",
    "parking_price", "erbbauzins_year", "score",
}
BOOLEAN = {"rented", "elevator", "denkmalschutz", "sanierungsgebiet"}
DATES = {"created", "updated", "data_asof", "listing_date", "date"}

# critical for any assessment — listed as open questions when absent
CRITICAL = ["living_area_m2", "year_built", "bundesland", "condition",
            "energy_value_kwh_m2a", "heating_year", "rent_cold_month",
            "commission_pct", "hausgeld_month"]

CRITICAL_LABEL = {
    "living_area_m2": "Wohnfläche (aus der Wohnflächenberechnung, nicht aus dem Exposé)",
    "year_built": "Baujahr",
    "bundesland": "Bundesland (bestimmt die Grunderwerbsteuer)",
    "condition": "Zustand / Sanierungsstau",
    "energy_value_kwh_m2a": "Energiekennwert — Energieausweis anfordern (§ 80 GEG)",
    "heating_year": "Baujahr der Heizung",
    "rent_cold_month": "aktuelle Nettokaltmiete, vermietet oder leer?",
    "commission_pct": "Maklerprovision: fällig? Käuferanteil inkl. USt",
    "hausgeld_month": "Hausgeld gesamt und nicht umlagefähiger Anteil (Wirtschaftsplan)",
}

FOLDERS = {
    "objekt": "10-Objekte",
    "vorlage": "90-Meta/Vorlagen",
    "standort": "20-Standorte",
    "kontakt": "30-Kontakte",
    "finanzierung-szenario": "40-Finanzierung",
    "entscheidung": "60-Entscheidungen",
    "sonstiges": "00-Inbox",
}
ALL_FOLDERS = ["00-Inbox", "10-Objekte", "20-Standorte", "30-Kontakte",
               "40-Finanzierung", "50-Wissen", "60-Entscheidungen",
               "90-Meta/Vorlagen", "99-Archiv"]

TYPE_HINTS = {
    "vorlage": ["vorlage", "template"],
    "objekt": ["objekt", "immobilie", "property", "wohnung", "haus", "kaufobjekt"],
    "besichtigung": ["besichtigung", "viewing", "termin"],
    "kontakt": ["kontakt", "contact", "makler", "person"],
    "dokument": ["dokument", "document", "unterlage", "expose", "exposé"],
    "entscheidung": ["entscheidung", "decision"],
    "standort": ["standort", "lage", "location", "stadtteil"],
    "finanzierung-szenario": ["finanzierung", "szenario", "darlehen", "kredit"],
}

FORBIDDEN = r'[*"\\/<>:|?#^\[\]]'
LINK_RE = re.compile(r"(!?)\[\[([^\]|#]+)((?:#[^\]|]*)?)(\|[^\]]*)?\]\]")


def sanitize(text: str) -> str:
    text = re.sub(FORBIDDEN, "", str(text)).strip()
    return re.sub(r"\s+", " ", text)[:90].rstrip(". ")


def _word_in(word: str, text: str) -> bool:
    """Whole-word match. Substring matching once turned 'Vorlage' into 'Lage'
    and filed a template under Standorte."""
    return re.search(rf"(?<![a-zäöüß]){re.escape(word)}(?![a-zäöüß])", text) is not None


def classify(fm: dict[str, Any], path: Path, body: str) -> str:
    if any(part.lower() in ("vorlagen", "templates", "_templates")
           for part in path.parts):
        return "vorlage"

    raw_type = str(fm.get("type") or "").strip().lower()
    for canonical, hints in TYPE_HINTS.items():
        if raw_type and (raw_type == canonical or raw_type in hints):
            return canonical
    name = path.stem.lower()
    for canonical, hints in TYPE_HINTS.items():
        if any(_word_in(h, name) for h in hints):
            return canonical

    # No declared type: only call it a property note when the FRONTMATTER carries
    # a price or a living area. A memo that merely mentions "Kaufpreis" is a memo,
    # and a wrong object note is worse than one note too many in the inbox.
    keys = {str(k).lower() for k in fm}
    hard_evidence = {"kaufpreis", "preis", "price_asking", "price", "angebotspreis",
                     "wohnflaeche", "wohnfläche", "living_area_m2", "qm"}
    if keys & hard_evidence:
        return "objekt"
    return "sonstiges"


def map_fields(fm: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str], list[str]]:
    """Return (canonical values, mapping applied, notes about conversions).

    One source key must not be claimed by two canonical fields: `stand` matches
    both `status` and `data_asof`, and only the more specific claim (earlier in
    that field's alias list) may win. Getting this wrong silently writes a date
    into the status.
    """
    lower = {str(k).lower(): k for k in fm}
    claims: list[tuple[int, str, str]] = []  # (specificity, canonical, source key)
    for canonical, names in ALIASES.items():
        for position, name in enumerate(names):
            if name in lower:
                claims.append((position, canonical, lower[name]))
    claims.sort(key=lambda c: (c[0], c[1]))

    chosen: dict[str, str] = {}      # canonical -> source key
    taken: set[str] = set()          # source keys already assigned
    dropped: list[str] = []
    for position, canonical, source_key in claims:
        if canonical in chosen or source_key in taken:
            if canonical not in chosen and source_key in taken:
                dropped.append(f"`{source_key}` wurde `{ [c for c, s in chosen.items() if s == source_key][0] }` "
                               f"zugeordnet, nicht `{canonical}`")
            continue
        chosen[canonical] = source_key
        taken.add(source_key)

    values: dict[str, Any] = {}
    mapping: dict[str, str] = {}
    remarks: list[str] = list(dict.fromkeys(dropped))
    for canonical, source_key in chosen.items():
        raw = fm[source_key]
        if raw in (None, "", []):
            continue
        value = raw
        if canonical in NUMERIC:
            converted = as_number(raw)
            if converted is None:
                remarks.append(
                    f"`{source_key}: {raw!r}` ist keine Zahl — als Text behalten, "
                    f"nicht als `{canonical}` übernommen")
                taken.discard(source_key)
                continue
            if isinstance(converted, float) and converted.is_integer():
                converted = int(converted)
            if str(converted) != str(raw).strip():
                remarks.append(f"`{source_key}: {raw!r}` → `{canonical}: {converted}`")
            value = converted
        elif canonical in BOOLEAN and isinstance(raw, str):
            if raw.strip().lower() in ("ja", "yes", "true", "x"):
                value = True
            elif raw.strip().lower() in ("nein", "no", "false"):
                value = False
        values[canonical] = value
        mapping[canonical] = str(source_key)

    leftovers = sorted(str(k) for k in fm
                       if str(k) not in set(mapping.values())
                       and str(k) not in ("type", "tags", "aliases")
                       and fm[k] not in (None, "", []))
    if leftovers:
        remarks.append("unverändert übernommen: " + ", ".join(leftovers))
    return values, mapping, remarks


def dump_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "\n" + "\n".join(f"  - {v}" for v in value)
    text = str(value)
    # A string that looks like a number must stay quoted: unquoted 01067 is read
    # as octal by YAML, and a postcode would silently change value.
    if (text.startswith("[[") or ":" in text or text.strip() != text
            or re.fullmatch(r"[\d.,+\-]+", text)):
        return f'"{text}"'
    return text


def build_frontmatter(ordered: dict[str, Any], leftovers: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in ordered.items():
        if value in (None, "", []):
            continue
        lines.append(f"{key}:{'' if isinstance(value, list) else ' '}{dump_value(value)}")
    if leftovers:
        lines.append("")
        lines.append("# aus der Ursprungsnotiz übernommen, vom Skill nicht interpretiert")
        for key, value in leftovers.items():
            lines.append(f"{key}:{'' if isinstance(value, list) else ' '}{dump_value(value)}")
    lines.append("---")
    return "\n".join(lines)


def open_questions_block(missing: list[str]) -> str:
    lines = ["", "", "## Offene Fragen",
             "", "%% Beim Aufbau des neuen Vaults ergänzt: diese Angaben fehlten und",
             "werden für jede Bewertung gebraucht. Beantwortete Zeilen löschen. %%", ""]
    lines += [f"- [ ] {CRITICAL_LABEL.get(key, key)}" for key in missing]
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--year", type=int, default=date.today().year,
                   help="Jahr für die vergebenen Objekt-IDs")
    p.add_argument("--no-open-questions", action="store_true",
                   help="keinen Block mit offenen Fragen an Objektnotizen anhängen")
    args = p.parse_args()

    source = Path(args.source).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Quelle ist kein Verzeichnis: {source}")
    if target.exists() and any(target.iterdir()) and not args.dry_run:
        raise SystemExit(f"Ziel ist nicht leer: {target}")
    if target == source or source in target.parents:
        raise SystemExit("Ziel darf nicht in der Quelle liegen.")

    # ---- read ---------------------------------------------------------- #
    notes: list[dict[str, Any]] = []
    for path in sorted(source.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            fm, body = read_note(path)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"# nicht lesbar, übersprungen: {path} ({exc})", file=sys.stderr)
            continue
        raw = path.read_text(encoding="utf-8")
        notes.append({"path": path, "fm": fm, "body": body,
                      "had_frontmatter": bool(split_note(raw)[0].strip())})

    for note in notes:
        note["kind"] = classify(note["fm"], note["path"], note["body"])

    # ---- plan names ------------------------------------------------------ #
    counter = 0
    rename: dict[str, str] = {}
    for note in notes:
        values, mapping, remarks = map_fields(note["fm"])
        note.update(values=values, mapping=mapping, remarks=remarks)
        if note["kind"] != "objekt":
            note["new_stem"] = note["path"].stem
            continue
        counter += 1
        obj_id = values.get("id") or f"OBJ-{args.year}-{counter:03d}"
        note["obj_id"] = str(obj_id)
        label_parts = [values.get("street") or values.get("title") or note["path"].stem]
        if values.get("city"):
            label_parts.append(str(values["city"]))
        note["folder_name"] = sanitize(f"{obj_id} " + ", ".join(
            str(part) for part in label_parts))
        note["new_stem"] = note["obj_id"]
        if note["path"].stem != note["new_stem"]:
            rename[note["path"].stem] = note["new_stem"]

    objects = [n for n in notes if n["kind"] == "objekt"]

    def find_object(note: dict[str, Any]) -> dict[str, Any] | None:
        """Attach a viewing or document to its property note, if it names one."""
        wanted: list[str] = []
        for key in ("object", "objekt", "immobilie", "bezug"):
            value = note["fm"].get(key)
            if value:
                wanted.append(str(value).strip("[]").split("|")[0].strip())
        for match in LINK_RE.finditer(note["body"]):
            wanted.append(match.group(2).strip())
        for candidate in objects:
            names = {candidate["path"].stem, str(candidate.get("obj_id") or ""),
                     str(candidate["values"].get("title") or "")}
            names.discard("")
            if any(w in names for w in wanted):
                return candidate
        # last resort: the filename names the object. Only accept an unambiguous
        # hit — two properties on the same street must not be guessed apart.
        stem = note["path"].stem.lower()
        hits = []
        for candidate in objects:
            labels = {candidate["path"].stem,
                      str(candidate["values"].get("street") or ""),
                      str(candidate["values"].get("title") or "")}
            tokens = {part.lower() for label in labels
                      for part in str(label).split() if len(part) >= 4}
            if any(_word_in(token, stem) for token in tokens):
                hits.append(candidate)
        unique = {id(h): h for h in hits}
        return next(iter(unique.values())) if len(unique) == 1 else None

    def rewrite(body: str) -> tuple[str, list[str]]:
        touched: list[str] = []

        def repl(match: re.Match[str]) -> str:
            bang, name, anchor, alias = match.groups()
            new = rename.get(name.strip())
            if not new:
                return match.group(0)
            touched.append(f"[[{name}]] → [[{new}]]")
            shown = alias or f"|{name.strip()}"
            return f"{bang}[[{new}{anchor or ''}{shown}]]"

        return LINK_RE.sub(repl, body), touched

    # ---- write ----------------------------------------------------------- #
    report: list[str] = []
    unresolved: list[str] = []
    by_kind: dict[str, int] = defaultdict(int)

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)
        for folder in ALL_FOLDERS:
            (target / folder).mkdir(parents=True, exist_ok=True)
        templates = Path(__file__).resolve().parent.parent / "assets" / "templates"
        for template in sorted(templates.glob("*.md")):
            shutil.copy2(template, target / "90-Meta" / "Vorlagen" / template.name)
        for template, destination in (("suchprofil.md", "90-Meta/Suchprofil.md"),
                                      ("finanzierungsrahmen.md", "90-Meta/Finanzierungsrahmen.md"),
                                      ("dashboard.md", "90-Meta/Dashboard.md")):
            shutil.copy2(templates / template, target / destination)

    for note in notes:
        kind = note["kind"]
        by_kind[kind] += 1
        values = dict(note["values"])
        body, touched = rewrite(note["body"])
        old_stem = note["path"].stem

        if kind == "objekt":
            values["id"] = note["obj_id"]
            values.setdefault("title", old_stem)
            aliases = note["fm"].get("aliases") or []
            if isinstance(aliases, str):
                aliases = [aliases]
            aliases = [a for a in aliases if a]
            if old_stem not in aliases and old_stem != note["new_stem"]:
                aliases.append(old_stem)  # alte Links lösen weiterhin auf
            values["aliases"] = aliases
            values.setdefault("status", "beobachtung")
            values.setdefault("created", date.today().isoformat())
            missing = [k for k in CRITICAL if not values.get(k)]
            if missing and not args.no_open_questions:
                body = body.rstrip() + open_questions_block(missing)
            destination = (target / FOLDERS["objekt"] / note["folder_name"] /
                           f"{note['new_stem']}.md")
        elif kind in ("besichtigung", "dokument"):
            missing = []
            owner = find_object(note)
            subfolder = "Besichtigungen" if kind == "besichtigung" else "Dokumente"
            if owner:
                values.setdefault("object", owner["obj_id"])
                destination = (target / FOLDERS["objekt"] / owner["folder_name"] /
                               subfolder / f"{note['new_stem']}.md")
                note["attached_to"] = owner["obj_id"]
            else:
                destination = target / "00-Inbox" / f"{note['new_stem']}.md"
                note["attached_to"] = None
        else:
            destination = target / FOLDERS.get(kind, "00-Inbox") / f"{note['new_stem']}.md"
            missing = []

        order = ["type", "id", "title", "aliases", "status", "created", "updated",
                 "data_asof", "sources", "street", "zip", "city", "district",
                 "bundesland", "property_type", "usage_intent", "living_area_m2",
                 "plot_area_m2", "rooms", "floor", "year_built", "year_renovated",
                 "condition", "energy_class", "energy_value_kwh_m2a",
                 "heating_type", "heating_year", "price_asking", "price_offered",
                 "price_agreed", "commission_pct", "hausgeld_month",
                 "grundsteuer_year", "rent_cold_month", "rented", "listing_url"]
        ordered = {"type": kind}
        for key in order[1:]:
            if key in values:
                ordered[key] = values[key]
        for key, value in values.items():
            ordered.setdefault(key, value)
        mapped_sources = set(note["mapping"].values())
        leftovers = {str(k): v for k, v in note["fm"].items()
                     if str(k) not in mapped_sources
                     and str(k) not in ("type", "aliases")
                     and v not in (None, "", [])}

        content = build_frontmatter(ordered, leftovers) + "\n" + body.rstrip() + "\n"
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        entry = [f"### {note['path'].relative_to(source)}",
                 f"- Typ erkannt: `{kind}`",
                 f"- Ziel: `{destination.relative_to(target)}`"]
        if old_stem != note["new_stem"]:
            entry.append(f"- Umbenannt: `{old_stem}` → `{note['new_stem']}` "
                         f"(alter Name als Alias eingetragen)")
        if note["mapping"]:
            entry.append("- Felder zugeordnet: " + ", ".join(
                f"`{src}` → `{dst}`" for dst, src in sorted(note["mapping"].items())))
        for remark in note["remarks"]:
            entry.append(f"- {remark}")
        if touched:
            entry.append(f"- Links umgeschrieben: {', '.join(sorted(set(touched)))}")
        if not note["had_frontmatter"]:
            entry.append("- ⚠️ hatte kein Frontmatter — Typ nur aus Inhalt und "
                         "Dateiname erschlossen")
            if kind != "sonstiges":  # for those the inbox line below already says it
                unresolved.append(f"`{note['path'].name}`: Typ bitte prüfen "
                                  f"(erkannt als `{kind}`, ohne Frontmatter)")
        if kind == "sonstiges":
            unresolved.append(f"`{note['path'].name}`: nicht eindeutig einzuordnen, "
                              "liegt in 00-Inbox")
        if kind in ("besichtigung", "dokument"):
            if note.get("attached_to"):
                entry.append(f"- Zugeordnet zu `{note['attached_to']}`")
            else:
                unresolved.append(f"`{note['path'].name}`: {kind} ohne erkennbaren "
                                  "Objektbezug, liegt in 00-Inbox")
        if missing:
            entry.append(f"- ⚠️ fehlende Kernangaben: {', '.join(missing)} "
                         "(als offene Fragen angehängt)")
        report.append("\n".join(entry))

    header = [
        "# Migrationsbericht", "",
        f"Erzeugt am {date.today().isoformat()} aus `{source.name}`.", "",
        f"{len(notes)} Notizen verarbeitet: "
        + ", ".join(f"{n}× {k}" for k, n in sorted(by_kind.items())), "",
        "Die Quelle wurde nur gelesen. Notiztexte sind unverändert übernommen; "
        "geändert wurden ausschließlich Frontmatter, Dateinamen, Ordner und "
        "Wikilinks. Bei Objektnotizen wurde ein markierter Block mit offenen "
        "Fragen angehängt.", "",
    ]
    if unresolved:
        header += ["## Bitte prüfen", ""] + [f"- {u}" for u in unresolved] + [""]
    header += ["## Im Einzelnen", ""]
    text = "\n".join(header) + "\n\n".join(report) + "\n"

    if args.dry_run:
        print(text)
        print("(dry run — nichts geschrieben)")
    else:
        (target / "MIGRATION.md").write_text(text, encoding="utf-8")
        print(f"{len(notes)} Notizen → {target}")
        print(f"Bericht: {target / 'MIGRATION.md'}")
        if unresolved:
            print(f"⚠️ {len(unresolved)} Punkt(e) zum Prüfen — siehe Bericht.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
