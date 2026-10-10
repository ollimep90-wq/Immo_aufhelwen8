"""Baut die Privat-Unterlagen: Bedarfsanalyse (A4) und Präsentationen (16:9).

Zahlen kommen ausschließlich aus zahlen.py (⟦Z:schluessel⟧), Pflichtangaben und Marke aus shared/brand.py.
Aufruf: python3 build.py
"""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "shared"))
from brand import marke, marke_icon, KONTAKT_OLIVER, PFLICHTHINWEIS_DU, R, A, render  # noqa: E402
from zahlen import Z  # noqa: E402

DECK_HEAD = (ROOT / "assets" / "deck_head.html").read_text()
DOC_HEAD = """<style>
@page{size:210mm 297mm;margin:0}
:root{--acc:#2E7D32;--acc-l:#E8F3E6}
.page{width:210mm;height:297mm;padding:14mm 15mm 13mm}
.foot{left:15mm;right:15mm}
h1{font-size:20pt}
.q{margin:0 0 1.5mm 0;padding-left:4mm;position:relative;font-size:9.3pt}
.q::before{content:"›";position:absolute;left:0;color:var(--acc);font-weight:700}
.say{background:var(--acc-l);border-left:3px solid var(--acc);padding:2mm 3mm;margin:2mm 0;font-size:9.3pt;font-style:italic;border-radius:0 2mm 2mm 0}
.why{font-size:8.2pt;color:var(--mute)}
.phase{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid var(--ink);margin:4mm 0 2mm;padding-bottom:1mm}
.phase h2{margin:0}
.phase span{font-size:8.5pt;color:var(--mute)}
table.form td{height:7mm;border-bottom:1px solid #B8C0D0;font-size:8.6pt}
table.form td.l{width:38%;color:var(--ink2)}
.amp{display:inline-block;width:3.2mm;height:3.2mm;border-radius:50%;vertical-align:-.5mm;margin-right:1mm}
.ar{background:#D64545}.ag{background:#E8A93B}.agr{background:#3E9B4F}
.box{display:inline-block;width:3mm;height:3mm;border:1px solid #8A93A8;border-radius:.6mm;vertical-align:-.4mm;margin-right:1mm}
</style>"""
BASE_CSS = '<link rel="stylesheet" href="../../Finanzanlagen/assets/base.css">'

FOOT_KUNDE = "Ganzheitliche Finanzberatung · Oliver Rosenbaum und Jan Schnichels (Endlich Besser Beraten)"
FOOT_JAN = "Ganzheitliche Finanzberatung · Jan Schnichels, Endlich Besser Beraten"
FOOT_INTERN = "Bedarfsanalyse Privat · intern"

TOKENS = {
    "⟦MARKE_HELL⟧": marke("#FFFFFF", "#9BD77F", "OLIVER ROSENBAUM · JAN SCHNICHELS", 64),
    "⟦MARKE_HELL_INTERN⟧": marke("#FFFFFF", "#9BD77F", "NAME FOLGT · ARBEITSTITEL", 70),
    "⟦MARKE⟧": marke(subline="OLIVER ROSENBAUM · JAN SCHNICHELS", h=48),
    "⟦MARKE_ICON⟧": marke_icon(),
    "⟦KONTAKT-OLIVER⟧": KONTAKT_OLIVER,
    "⟦PFLICHTHINWEIS⟧": PFLICHTHINWEIS_DU,
    "⟦R⟧": R, "⟦A⟧": A,
}

# (Quelle, Ausgabe, Titel, Art, Fußzeile, Kundendokument?)
DOCS = [
    ("bedarfsanalyse", "01_Bedarfsanalyse_Privat", "Bedarfsanalyse Privat", "doc", FOOT_INTERN, False),
    ("kennenlernen", "02_Kennenlernen_Unser_Weg", "Unser Weg mit dir", "deck", FOOT_KUNDE, True),
    ("risiko", "03_Risikoabsicherung", "Risikoabsicherung", "deck", FOOT_JAN, True),
    ("vermoegen", "04_Vermoegensaufbau", "Vermögensaufbau", "deck", FOOT_KUNDE, True),
    ("alter", "05_Altersvorsorge", "Altersvorsorge", "deck", FOOT_KUNDE, True),
    ("immobilien", "06_Immobilien_und_Finanzierung", "Immobilien und Finanzierung", "deck", FOOT_KUNDE, True),
]

def fill(body, foot, art):
    body = re.sub(r"⟦Z:(\w+)⟧", lambda m: Z[m.group(1)], body)
    for k, v in TOKENS.items():
        body = body.replace(k, v)
    n = 0
    def numbered(_):
        nonlocal n
        n += 1
        return f'<div class="foot"><span>{foot}</span><span>{n + 1}</span></div>'
    return re.sub(r"⟦FOOT⟧", numbered, body)

only = set(sys.argv[1:])
for src, out, title, art, foot, kunde in DOCS:
    if only and src not in only:
        continue
    p = ROOT / "src" / f"{src}.html"
    if not p.exists():
        continue
    body = fill(p.read_text(), foot, art)
    head = (DECK_HEAD if art == "deck" else BASE_CSS + DOC_HEAD)
    html = f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{title}</title>{head}</head><body>{body}</body></html>' if art == "doc" else \
           f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{title}</title>{head.split("</style>")[0]}</style></head><body>{head.split("</style>",1)[1]}{body}</body></html>'
    seiten = render(html, ROOT / f"{out}.pdf", title, forbid_tags=kunde)
    print(out, seiten, "Seiten")
