"""Baut den Vorab-Check als eine Datei: ../07_Vorab-Check.html

Fügt rechenkern.js, fragen.js und die Wortmarke aus shared/brand.py ein,
entfernt interne Kommentare und Herkunftsangaben und prüft vorher den Rechenkern
gegen die Python-Gegenrechnung.

  python3 build.py                 Vorschau (ohne Versandadresse erlaubt)
  python3 build.py --live URL DS   Live-Fassung mit Empfangsadresse und Link zur Datenschutzerklärung
"""
import pathlib, re, subprocess, sys
HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER.parent.parent.parent / "shared"))
from brand import marke  # noqa: E402


def ohne_intern(js):
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)          # Blockkommentare
    js = re.sub(r"(?m)^\s*//.*\n", "", js)                  # ganze Kommentarzeilen
    js = re.sub(r'(?m)[ \t]+//[^"\n]*$', "", js)            # Kommentare am Zeilenende
    js = re.sub(r'\s*quelle:\s*"[^"]*",', "", js)          # Herkunft der Fragen
    return js


subprocess.run([sys.executable, str(HIER / "test_rechenkern.py")], check=True)
html = (HIER / "vorab.html").read_text()
live = "--live" in sys.argv
if live:
    url, ds = sys.argv[sys.argv.index("--live") + 1: sys.argv.index("--live") + 3]
    assert url.startswith("https://") and ds.startswith("https://"), "Live braucht https-Adressen"
    alt = 'const VERSAND = { url: "", ds_url: "" };'
    assert html.count(alt) == 1
    html = html.replace(alt, f'const VERSAND = {{ url: "{url}", ds_url: "{ds}" }};')

for token, inhalt in [("/*RECHENKERN*/", ohne_intern((HIER / "rechenkern.js").read_text())),
                      ("/*FRAGEN*/", ohne_intern((HIER / "fragen.js").read_text())),
                      ("<!--MARKE-->", marke(h=34))]:
    assert html.count(token) == 1, token
    html = html.replace(token, inhalt)

# interne Kommentare der Seite selbst
html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
html = re.sub(r"/\*.*?\*/", "", html, flags=re.S)

for intern in ("Prototyp", "Masterarbeit", "STATUS", "QUELLEN", "quelle:", "Befund"):
    assert intern not in html, f"interner Begriff in der Ausgabe: {intern}"
if live:
    assert "in dieser Vorschau" not in html or 'url: ""' not in html
    assert "[Datenschutz" not in html and "[Impressum]" not in html and "[Adresse]" not in html, \
        "Platzhalter für Impressum/Datenschutz/Adresse noch offen"

ziel = HIER.parent / ("07_Vorab-Check.html" if not live else "07_Vorab-Check_live.html")
ziel.write_text(html)
print(ziel.name, len(html) // 1024, "KB", "(live)" if live else "(Vorschau)")
