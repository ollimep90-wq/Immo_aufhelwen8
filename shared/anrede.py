"""Anrede du/Sie für Kundenunterlagen.

Die Quellen sind in der du-Form geschrieben. Die Sie-Fassung entsteht aus der Tabelle shared/sie.json:
  - "bausteine": Textbaustein zwischen zwei HTML-Tags (exakt wie in der Quelle) -> Sie-Fassung
  - "ersetzen":  [alt, neu] für Stellen, die über Tags hinweggehen (z. B. „dein <b>Leben</b>“); jede muss genau einmal passen
Der Build bricht ab, wenn in der Sie-Fassung noch eine du-Form steht, die nicht als Ausnahme erlaubt ist.

Aufruf zum Pflegen: python3 shared/anrede.py fehlend <quelle.html> ...   (listet Bausteine mit du-Form ohne Sie-Fassung)
"""
import json, pathlib, re, sys

TABELLE = json.loads((pathlib.Path(__file__).parent / "sie.json").read_text())
# du-Formen, die in einer Sie-Fassung nicht mehr vorkommen dürfen
DU = re.compile(r"\b(du|dich|dir|dein|deine|deinen|deinem|deiner|deines|Du|Dich|Dir|Dein|Deine|Deinen|Deinem|Deiner|Deines|"
                r"hast|bist|kannst|willst|musst|möchtest|brauchst|bekommst|siehst|weißt|findest|zahlst|sparst|machst|lädst|trägst)\b")
# erlaubte Ausnahmen: Zitate in der Ich-Form, Bezüge auf Dritte, interne Hinweise über die Anrede selbst
AUSNAHMEN = [re.compile(x) for x in TABELLE.get("ausnahmen", [])]


def _knoten(html):
    """Positionen der Textbausteine außerhalb von style/script/Kommentaren."""
    sperr = [(m.start(), m.end()) for m in re.finditer(r"<(style|script)\b.*?</\1>|<!--.*?-->", html, flags=re.S | re.I)]
    for m in re.finditer(r">([^<]+)<", html):
        if any(a <= m.start() < b for a, b in sperr):
            continue
        yield m.start(1), m.end(1), m.group(1)


def zu_sie(html):
    teile, pos = [], 0
    bausteine = TABELLE["bausteine"]
    for a, b, text in _knoten(html):
        kern = text.strip()
        if kern in bausteine:
            vorne = text[: len(text) - len(text.lstrip())]
            hinten = text[len(text.rstrip()):]
            teile.append(html[pos:a]); teile.append(vorne + bausteine[kern] + hinten); pos = b
    html = "".join(teile) + html[pos:]
    for alt, neu in TABELLE.get("ersetzen", []):
        if html.count(alt) == 1:
            html = html.replace(alt, neu)
    return html


def reste(html):
    """du-Formen, die nach der Umstellung noch übrig sind (ohne erlaubte Ausnahmen)."""
    out = []
    for _, _, text in _knoten(html):
        t = text.strip()
        if DU.search(t) and not any(x.search(t) for x in AUSNAHMEN):
            out.append(t)
    return out


def pruefe(html, name):
    r = reste(html)
    if r:
        raise SystemExit(f"{name}: {len(r)} Stellen ohne Sie-Fassung (shared/sie.json ergänzen):\n  " + "\n  ".join(r[:30]))
    return html


IMPERATIV = re.compile(r"\b(Trag|trag|Wähl|wähl|Prüf|prüf|Lade|lade sie|Melde|melde dich|Schreib|schreib|Versuch|versuch|Bring|bring|Lass|lass uns|Frag|frag|Nimm|nimm|Leg|leg|Tipp auf|tipp auf|Stimme zu|stimme zu)\b")
_LITERAL = re.compile(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'|`((?:[^`\\]|\\.)*)`', re.S)


def js_zu_sie(js, datei):
    """JavaScript-Texte des Kundenbereichs: Paare aus sie.json["js"][datei], jedes muss vorkommen."""
    for alt, neu in TABELLE.get("js", {}).get(datei, []):
        if alt not in js:
            raise SystemExit(f"{datei}: Text für die Sie-Fassung nicht gefunden (sie.json anpassen): {alt}")
        js = js.replace(alt, neu)
    return js


def js_pruefe(js, datei):
    """Zeichenketten mit du-Form oder du-Imperativ, die nach der Umstellung noch übrig sind."""
    r = []
    for m in _LITERAL.finditer(js):
        t = next(g for g in m.groups() if g is not None)
        if (DU.search(t) or IMPERATIV.search(t)) and not any(x.search(t) for x in AUSNAHMEN):
            r.append(t[:160])
    if r:
        raise SystemExit(f"{datei}: {len(r)} Texte ohne Sie-Fassung (sie.json „js“ ergänzen):\n  " + "\n  ".join(r))
    return js


if __name__ == "__main__" and sys.argv[1:2] == ["fehlend"]:
    for f in sys.argv[2:]:
        for t in reste(zu_sie(pathlib.Path(f).read_text())):
            print(f"{f}: {t}")
