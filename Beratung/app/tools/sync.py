"""Übernimmt Rechenkern und Kurzcheck-Fragen aus Privat/vorab-check in die App (eine Quelle)."""
import pathlib, shutil
HIER = pathlib.Path(__file__).resolve().parent.parent
QUELLE = HIER.parent / "Privat/vorab-check"
for name in ("rechenkern.js", "fragen.js"):
    shutil.copyfile(QUELLE / name, HIER / "web/js" / name)
(HIER / "web/data").mkdir(exist_ok=True)
shutil.copyfile(HIER / "data/fragen_voll.json", HIER / "web/data/fragen_voll.json")
print("synchronisiert")
