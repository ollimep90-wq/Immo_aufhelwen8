"""Baut die Gewerbe-Unterlagen: Bedarfsanalyse (A4, intern) und Präsentationen (16:9), je in du- und Sie-Fassung.

Gleicher Aufbau wie Beratung/Privat/build.py:
- Zahlen kommen ausschließlich aus zahlen.py (⟦Z:schluessel⟧), jede mit Quelle dort.
- Pflichtangaben und Marke aus shared/brand.py, Sie-Fassung über shared/anrede.py und shared/sie.json.
Aufruf: python3 build.py            (alle Dokumente, du und Sie)
        python3 build.py betrieb    (nur ein Dokument)
"""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "shared"))
from brand import marke, marke_icon, KONTAKT_OLIVER, PFLICHTHINWEIS, PFLICHTHINWEIS_DU, R, A, render  # noqa: E402
import anrede  # noqa: E402
from zahlen import Z  # noqa: E402

PRIVAT = ROOT.parent / "Privat"
DECK_HEAD = (PRIVAT / "assets" / "deck_head.html").read_text()
# Kopf der A4-Dokumente: derselbe wie in der Bedarfsanalyse Privat
_privat_build = (PRIVAT / "build.py").read_text()
DOC_HEAD = re.search(r'DOC_HEAD = """(.*?)"""', _privat_build, re.S).group(1)
BASE_CSS = '<link rel="stylesheet" href="../../Finanzanlagen/assets/base.css">'

FOOT_KUNDE = "Ganzheitliche Finanzberatung · Oliver Rosenbaum in Kooperation mit Endlich Besser Beraten"
FOOT_JAN = "Ganzheitliche Finanzberatung · Jan Schnichels, Endlich Besser Beraten, in Kooperation mit Oliver Rosenbaum"
FOOT_INTERN = "Bedarfsanalyse Gewerbe · intern"

TOKENS = {
    "⟦MARKE_HELL⟧": marke("#FFFFFF", "#9BD77F", "ZWEI EIGENSTÄNDIGE PARTNER IN KOOPERATION", 64),
    "⟦MARKE_HELL_INTERN⟧": marke("#FFFFFF", "#9BD77F", "NAME FOLGT · ARBEITSTITEL", 70),
    "⟦MARKE⟧": marke(subline="ZWEI EIGENSTÄNDIGE PARTNER IN KOOPERATION", h=48),
    "⟦MARKE_ICON⟧": marke_icon(),
    "⟦KONTAKT-OLIVER⟧": KONTAKT_OLIVER,
    "⟦PFLICHTHINWEIS⟧": PFLICHTHINWEIS_DU,
    "⟦R⟧": R, "⟦A⟧": A,
}

# (Quelle, Ausgabe, Titel du, Titel Sie, Art, Fußzeile, Kundendokument?)
DOCS = [
    ("bedarfsanalyse", "01_Bedarfsanalyse_Gewerbe", "Bedarfsanalyse Gewerbe", "Bedarfsanalyse Gewerbe", "doc", FOOT_INTERN, False),
    ("kennenlernen", "02_Unser_Weg_mit_deinem_Unternehmen", "Unser Weg mit deinem Unternehmen", "Unser Weg mit Ihrem Unternehmen", "deck", FOOT_KUNDE, True),
    ("betrieb", "03_Betrieb_absichern", "Betrieb absichern", "Betrieb absichern", "deck", FOOT_JAN, True),
    ("unternehmer", "04_Unternehmer_absichern_und_vorsorgen", "Unternehmer: absichern und vorsorgen", "Unternehmer: absichern und vorsorgen", "deck", FOOT_KUNDE, True),
    ("mitarbeiter", "05_Mitarbeiter_bAV_und_bKV", "Mitarbeiter: betriebliche Altersversorgung und Krankenversicherung", "Mitarbeiter: betriebliche Altersversorgung und Krankenversicherung", "deck", FOOT_JAN, True),
]


def fill(body, foot, sie=False):
    body = re.sub(r"⟦Z:(\w+)⟧", lambda m: Z[m.group(1)], body)
    for k, v in TOKENS.items():
        body = body.replace(k, PFLICHTHINWEIS if (sie and k == "⟦PFLICHTHINWEIS⟧") else v)
    n = 0

    def numbered(_):
        nonlocal n
        n += 1
        return f'<div class="foot"><span>{foot}</span><span>{n + 1}</span></div>'
    return re.sub(r"⟦FOOT⟧", numbered, body)


only = set(sys.argv[1:])
for src, out, titel, titel_sie, art, foot, kunde in DOCS:
    if only and src not in only:
        continue
    p = ROOT / "src" / f"{src}.html"
    if not p.exists():
        continue
    for sie in (False, True):
        quelle = p.read_text()
        if sie:
            quelle = anrede.pruefe(anrede.zu_sie(quelle), src)
        t = titel_sie if sie else titel
        body = fill(quelle, foot, sie)
        if art == "doc":
            html = f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{t}</title>{BASE_CSS}{DOC_HEAD}</head><body>{body}</body></html>'
        else:
            kopf, rest = DECK_HEAD.split("</style>", 1)
            html = f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{t}</title>{kopf}</style></head><body>{rest}{body}</body></html>'
        name = (out.replace("deinem", "Ihrem") if sie else out) + ("_Sie" if sie else "")
        autor = "Jan Schnichels, Endlich Besser Beraten" if foot == FOOT_JAN else "Oliver Rosenbaum"
        seiten = render(html, ROOT / f"{name}.pdf", t, author=autor, forbid_tags=kunde)
        print(name, seiten, "Seiten")
