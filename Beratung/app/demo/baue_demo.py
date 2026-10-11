"""Baut die Klick-Demo der Beratungs-App: echte Oberfläche aus Beratung/app/web, Server ersetzt durch js/demo.js.
Aufruf: python3 demo/baue_demo.py demo/beispieldaten.json <ausgabe-ordner außerhalb des Repos>
beispieldaten.json: erfundene Familie Muster, erzeugt mit einem Browser-Durchlauf gegen den lokalen Server."""
import json, re, shutil, sys
from pathlib import Path
import segno

HIER = Path(__file__).parent
WEB = HIER.parent / "web"
seed, aus = Path(sys.argv[1]), Path(sys.argv[2])
if aus.exists():
    shutil.rmtree(aus)
shutil.copytree(WEB, aus)
(aus / "index.html").rename(aus / "anmeldung.html")
(aus / "manifest.webmanifest").unlink()

def pfade(t):
    t = re.sub(r'<link rel="manifest"[^>]*>\n?', "", t)
    for alt, neu in [('"/css/', '"css/'), ('"/js/', '"js/'), ('"/img/', '"img/'), ('"/data/', '"data/'), ('"/vendor/', '"vendor/'),
                     ('"/kunde.html', '"kunde.html'), ('"/kunde_sie.html', '"kunde_sie.html'), ('"/berater.html', '"berater.html'),
                     ('location.href = "/"', 'location.href = "anmeldung.html"'), ('href="/"', 'href="anmeldung.html"')]:
        t = t.replace(alt, neu)
    return t

for f in list(aus.rglob("*.html")) + list(aus.rglob("*.js")):
    t = pfade(f.read_text())
    if f.suffix == ".html" and "js/api.js" in t:
        t = t.replace('<script src="js/api.js"></script>', '<script src="js/demo.js"></script>\n<script src="js/api.js"></script>')
        t = re.sub(r"<title>([^<]*)</title>", r"<title>\1 · Demo</title>", t)
    if f.name in ("kunde_check.js", "kunde_check_sie.js"):
        alt = 'const m = location.hash.match(/einladung=([\\w-]+)/);'
        assert alt in t
        t = t.replace(alt, 'const m = location.hash.match(/einladung=([\\w-]+)/) || (window.DEMO && DEMO.offeneEinladung());')
    f.write_text(t)

rest = [str(f.relative_to(aus)) for f in aus.rglob("*") if f.is_file() and f.suffix in (".html", ".js", ".css") and re.search(r'"/(?!api/)[a-z]', f.read_text(errors="ignore"))]
assert not rest, f"absolute Pfade übrig: {rest}"

qr = segno.make("otpauth://totp/Beratungs-App%20Demo?secret=DEMODEMODEMODEMODEMODEMODEMODEMO&issuer=Demo", error="m")
qr_data = qr.svg_data_uri(scale=6, border=2)
demo = (HIER / "demo.js").read_text()
demo = demo.replace("/*SEED*/null", json.dumps(json.loads(seed.read_text()), ensure_ascii=False)).replace('/*QR*/""', json.dumps(qr_data))
# nur ASCII: unabhängig davon, mit welchem Zeichensatz die Seite das Skript lädt
demo = "".join(c if ord(c) < 128 else "\\u%04x" % ord(c) if ord(c) < 0x10000 else "\\u{%x}" % ord(c) for c in demo)
(aus / "js" / "demo.js").write_text(demo)
shutil.copy(HIER / "start.html", aus / "start.html")
# Steuerzeichen in pdf.js (nur in Zeichenketten) als \xNN schreiben: bedeutungsgleich, und die Veröffentlichung nimmt die Datei an
for f in (aus / "vendor").rglob("*.mjs"):
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", lambda m: "\\x%02x" % ord(m.group()), t)
    f.write_text(t, encoding="utf-8")
print("Demo gebaut:", aus, sum(f.stat().st_size for f in aus.rglob("*") if f.is_file()), "Bytes")
