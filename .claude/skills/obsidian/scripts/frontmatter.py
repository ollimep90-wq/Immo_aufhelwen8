"""Minimal YAML frontmatter reader for the obsidian skill.

Uses PyYAML when available, otherwise a small parser that covers the flat schema
documented in references/frontmatter.md (scalars, block lists, inline lists).
Standard library only.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:  # pragma: no cover - depends on the machine
    import yaml  # type: ignore

    _HAVE_YAML = True
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore
    _HAVE_YAML = False


_NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _coerce(raw: str) -> Any:
    """Turn a scalar token into a Python value, mirroring YAML's basics."""
    value = raw.strip()
    if not value:
        return None
    if value[0] in "\"'" and value[-1] == value[0] and len(value) >= 2:
        return value[1:-1]
    lowered = value.lower()
    if lowered in ("null", "~"):
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _DATE_RE.match(value):
        return value
    if _NUM_RE.match(value):
        return float(value) if "." in value else int(value)
    return value


def _parse_flat(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    key: str | None = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and line.lstrip().startswith("- "):
            if key is not None:
                data.setdefault(key, [])
                if isinstance(data[key], list):
                    data[key].append(_coerce(line.lstrip()[2:]))
            continue
        if line.startswith("- "):
            if key is not None:
                data.setdefault(key, [])
                if isinstance(data[key], list):
                    data[key].append(_coerce(line[2:]))
            continue
        if ":" not in line:
            continue
        raw_key, _, raw_value = line.partition(":")
        key = raw_key.strip()
        stripped = raw_value.strip()
        if not stripped:
            data[key] = []  # a block list may follow; overwritten if a scalar comes
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            inner = stripped[1:-1].strip()
            data[key] = [_coerce(p) for p in inner.split(",")] if inner else []
            continue
        data[key] = _coerce(stripped)
    # keys that got an empty list but never any items are really unset
    return {k: (None if v == [] else v) for k, v in data.items()}


def split_note(text: str) -> tuple[str, str]:
    """Return (frontmatter_text, body). Empty frontmatter if the note has none."""
    if not text.startswith("---"):
        return "", text
    lines = text.splitlines(keepends=True)
    if lines[0].strip() != "---":
        return "", text
    for index in range(1, len(lines)):
        if lines[index].strip() in ("---", "..."):
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    return "", text


def parse_frontmatter(text: str) -> dict[str, Any]:
    fm_text, _ = split_note(text)
    if not fm_text.strip():
        return {}
    if _HAVE_YAML:
        try:
            loaded = yaml.safe_load(fm_text)
            if isinstance(loaded, dict):
                return {str(k): v for k, v in loaded.items()}
            return {}
        except Exception:
            pass  # malformed YAML: fall back rather than crash on the user's note
    return _parse_flat(fm_text)


def read_note(path: str | Path) -> tuple[dict[str, Any], str]:
    text = Path(path).read_text(encoding="utf-8")
    fm_text, body = split_note(text)
    if not fm_text.strip():
        return {}, body
    return parse_frontmatter(text), body


def as_number(value: Any) -> float | None:
    """Accept 485000, '485000', '485.000 €' and return a float, else None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("€", "").replace("EUR", "").replace("%", "").strip()
    text = text.replace(" ", "").replace(" ", "")
    if "," in text and "." in text:  # 485.000,50 -> 485000.50
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    elif text.count(".") == 1:
        whole, _, frac = text.partition(".")
        if len(frac) == 3 and len(whole) <= 3:  # 485.000 is a thousands separator
            text = whole + frac
    else:
        text = text.replace(".", "")
    try:
        return float(text)
    except ValueError:
        return None
