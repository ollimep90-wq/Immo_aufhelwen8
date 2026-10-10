"""Unabhängige Python-Umsetzung des Rechenkerns und Vergleich mit rechenkern.js.

Aufruf: python3 test_rechenkern.py   (braucht node)
"""
import json, math, subprocess, pathlib, itertools

HIER = pathlib.Path(__file__).parent

# Rechengrößen 2026 (eigene Abschrift, Quellen in QUELLEN.md)
GFB = 12348
def tarif_2026(zve):
    x = math.floor(max(0, zve))
    if x <= GFB: return 0
    if x <= 17799:
        y = (x - GFB) / 10000; return math.floor((914.51 * y + 1400) * y)
    if x <= 69878:
        z = (x - 17799) / 10000; return math.floor((173.10 * z + 2397) * z + 1034.87)
    if x <= 277825: return math.floor(0.42 * x - 11135.63)
    return math.floor(0.45 * x - 19470.38)

def sv(b, kv="gkv", zb=0.029, alter=40, kinder=0, sachsen=False, pkv=0):
    bkv, brv = min(b, 69750), min(b, 101400)
    rv, av = brv * 0.093, brv * 0.013
    if kv == "pkv":
        k = pkv * 12; return dict(kv=k, pv=0, rv=rv, av=av, kv_vsp=k)
    k = bkv * (0.073 + zb / 2)
    kvsp = bkv * (0.07 + zb / 2)
    s = 0.018 + (0.005 if sachsen else 0)
    if kinder == 0 and alter >= 23: s += 0.006
    if kinder >= 2: s -= 0.0025 * (min(kinder, 5) - 1)
    return dict(kv=k, pv=bkv * s, rv=rv, av=av, kv_vsp=kvsp)

def zve(b, **kw):
    s = sv(b, **kw)
    kvpv = s["kv_vsp"] + s["pv"]
    vsp = s["rv"] + kvpv + max(0, min(s["av"], 1900 - kvpv))
    return max(0, b - 1230 - 36 - vsp), s

def soli(e, fg):
    return min(e * 0.055, (e - fg) * 0.119) if e > fg else 0

def netto(personen, verheiratet, kinder, kirche, land="NW"):
    kist = (0.08 if land in ("BY", "BW") else 0.09) if kirche else 0
    rows = [zve(p["brutto"], **{k: v for k, v in p.items() if k != "brutto"}) for p in personen]
    abz = [sum(v for k, v in s.items() if k != "kv_vsp") for _, s in rows]
    if verheiratet:
        z = sum(r[0] for r in rows)
        e = 2 * tarif_2026(z / 2)
        ek = 2 * tarif_2026(max(0, z - kinder * 9756) / 2)
        st = e + soli(ek, 40700) + ek * kist
        return sum(p["brutto"] for p in personen) - sum(abz) - st
    tot = 0
    for p, (z, _), a in zip(personen, rows, abz):
        e = tarif_2026(z)
        ek = tarif_2026(max(0, z - kinder * 9756 / 2))
        tot += p["brutto"] - a - e - soli(ek, 20350) - ek * kist
    return tot

def js(fall):
    code = f"""const R=require('{HIER/'rechenkern.js'}');
const f={json.dumps(fall)};
console.log(JSON.stringify(R.nettoHaushalt(f)));"""
    return json.loads(subprocess.check_output(["node", "-e", code]))

FAELLE = []
for b1, b2, verh, kinder, kirche, land in itertools.product(
        [0, 14000, 30000, 52000, 84000, 120000, 300000], [0, 48000], [False, True], [0, 2, 3], [False, True], ["NW", "BY"]):
    if b1 == 0 and b2 == 0: continue
    pers = [dict(brutto=b1, kv="gkv", alter=38, kinder_u25=kinder), dict(brutto=b2, kv="gkv", alter=36, kinder_u25=kinder)]
    FAELLE.append(dict(personen=pers, verheiratet=verh, kinder=kinder, kirche=kirche, bundesland=land))

if __name__ == "__main__":
    # Tarif stetig an den Zonengrenzen
    for g in (12348, 17799, 69878, 277825):
        assert abs(tarif_2026(g) - tarif_2026(g + 1)) <= 1, g
    maxdiff = 0
    for f in FAELLE:
        pers = [dict(brutto=p["brutto"], alter=p["alter"], kinder=p["kinder_u25"]) for p in f["personen"] if p["brutto"] > 0]
        py = netto(pers, f["verheiratet"], f["kinder"], f["kirche"], f["bundesland"])
        j = js(f)["netto_jahr"]
        maxdiff = max(maxdiff, abs(py - j))
        assert abs(py - j) < 0.05, (f, py, j)
    print(f"{len(FAELLE)} Fälle, größte Abweichung JS/Python {maxdiff:.4f} €")
