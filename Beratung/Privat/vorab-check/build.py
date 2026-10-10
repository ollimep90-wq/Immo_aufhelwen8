"""Baut den Vorab-Check als eine Datei: ../07_Vorab-Check.html

Fügt rechenkern.js, fragen.js und die Wortmarke aus shared/brand.py ein und
prüft vorher den Rechenkern gegen die Python-Gegenrechnung.
"""
import pathlib, subprocess, sys
HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER.parent.parent.parent / "shared"))
from brand import marke  # noqa: E402

subprocess.run([sys.executable, str(HIER / "test_rechenkern.py")], check=True)
html = (HIER / "vorab.html").read_text()
for token, inhalt in [("/*RECHENKERN*/", (HIER / "rechenkern.js").read_text()),
                      ("/*FRAGEN*/", (HIER / "fragen.js").read_text()),
                      ("<!--MARKE-->", marke(h=34))]:
    assert html.count(token) == 1, token
    html = html.replace(token, inhalt)
ziel = HIER.parent / "07_Vorab-Check.html"
ziel.write_text(html)
print(ziel.name, len(html) // 1024, "KB")
