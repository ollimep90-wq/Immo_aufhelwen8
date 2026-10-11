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

def sv(b, kv="gkv", zb=0.029, alter=40, kinder=0, sachsen=False, pkv=0, eltern=False):
    bkv, brv = min(b, 69750), min(b, 101400)
    rv, av = brv * 0.093, brv * 0.013
    if kv == "pkv":
        k = pkv * 12; return dict(kv=k, pv=0, rv=rv, av=av, kv_vsp=k)
    k = bkv * (0.073 + zb / 2)
    kvsp = bkv * (0.07 + zb / 2)
    s = 0.018 + (0.005 if sachsen else 0)
    if kinder == 0 and not eltern and alter >= 23: s += 0.006
    if kinder >= 2: s -= 0.0025 * (min(kinder, 5) - 1)
    return dict(kv=k, pv=bkv * s, rv=rv, av=av, kv_vsp=kvsp)

def zve(b, entl=0, **kw):
    s = sv(b, **kw)
    kvpv = s["kv_vsp"] + s["pv"]
    vsp = s["rv"] + kvpv + max(0, min(s["av"], 1900 - kvpv))
    return max(0, b - 1230 - 36 - vsp - entl), s

def soli(e, fg):
    return min(e * 0.055, (e - fg) * 0.119) if e > fg else 0

def netto(personen, verheiratet, kinder, kirche, land="NW", allein=False):
    kist = (0.08 if land in ("BY", "BW") else 0.09) if kirche else 0
    e_ab = 4260 if (allein and not verheiratet) else 0
    rows = [zve(p["brutto"], entl=e_ab, **{k: v for k, v in p.items() if k != "brutto"}) for p in personen]
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
# Alleinerziehende und Eltern erwachsener Kinder
for b1, k, eltern in itertools.product([20000, 45000, 90000], [0, 1, 2], [False, True]):
    FAELLE.append(dict(personen=[dict(brutto=b1, kv="gkv", alter=50, kinder_u25=k, eltern=eltern)], verheiratet=False,
                       kinder=k, kirche=False, bundesland="NW", alleinerziehend=k > 0))

# Netto-Rente: eigene Abschrift der Regeln (KVdR § 247/§ 249a SGB V, PV § 59 SGB XI, PKV-Zuschuss § 106 SGB VI,
# Besteuerungsanteil § 22 Nr. 1 S. 3 a aa EStG i. d. F. Wachstumschancengesetz, § 9a S. 1 Nr. 3, § 10c EStG)
def anteil(jahr):
    return min(1.0, max(0.825, 0.825 + 0.005 * (jahr - 2023)))

def rente_zve(b, jahr, kv="gkv", zb=0.029, pkv=0, kinderlos=False):
    j = b * 12
    if kv == "pkv":
        beitrag = pkv * 12; zu = min(j * (0.146 + 0.029) / 2, beitrag / 2)
        abz = dict(kv=beitrag, pv=0, zu=zu); vsp = max(0, beitrag - zu)
    else:
        k = j * (0.146 + zb) / 2; pv = j * (0.036 + (0.006 if kinderlos else 0))
        abz = dict(kv=k, pv=pv, zu=0); vsp = k + pv
    return max(0, j * anteil(jahr) - 102 - 36 - vsp), abz

def netto_rente(b, jahr, verh=False, partner=0, kirche=False, land="NW", **kw):
    z, abz = rente_zve(b, jahr, **kw)
    kist = (0.08 if land in ("BY", "BW") else 0.09) if kirche else 0
    if verh and partner > 0:
        z2, _ = rente_zve(partner, jahr, **kw)
        g = 2 * tarif_2026((z + z2) / 2); s = soli(g, 40700); a = z / (z + z2) if z + z2 > 0 else 0.5
        e, so = g * a, s * a
    else:
        e = tarif_2026(z); so = soli(e, 20350)
    return (b * 12 - abz["kv"] - abz["pv"] + abz["zu"] - e - so - e * kist) / 12

def js_rente(fall):
    code = f"""const R=require('{HIER/'rechenkern.js'}');
console.log(JSON.stringify(R.nettoRente({json.dumps(fall)})));"""
    return json.loads(subprocess.check_output(["node", "-e", code]))

RENTEN = []
for b, jahr, kv, kinderlos, verh, partner, kirche in itertools.product(
        [0, 800, 1500, 2200, 3500], [2030, 2045, 2058, 2070], ["gkv", "pkv"], [False, True], [False, True], [0, 900], [False, True]):
    RENTEN.append(dict(brutto_monat=b, rentenbeginn_jahr=jahr, kv=kv, zusatzbeitrag=0.029, pkv_beitrag_monat=650 if kv == "pkv" else 0,
                       kinderlos=kinderlos, verheiratet=verh, partner_brutto_monat=partner, kirche=kirche, bundesland="NW"))

if __name__ == "__main__":
    # Tarif stetig an den Zonengrenzen
    for g in (12348, 17799, 69878, 277825):
        assert abs(tarif_2026(g) - tarif_2026(g + 1)) <= 1, g
    maxdiff = 0
    for f in FAELLE:
        pers = [dict(brutto=p["brutto"], alter=p["alter"], kinder=p["kinder_u25"], eltern=p.get("eltern", False)) for p in f["personen"] if p["brutto"] > 0]
        py = netto(pers, f["verheiratet"], f["kinder"], f["kirche"], f["bundesland"], f.get("alleinerziehend", False))
        j = js(f)["netto_jahr"]
        maxdiff = max(maxdiff, abs(py - j))
        assert abs(py - j) < 0.05, (f, py, j)
    print(f"{len(FAELLE)} Fälle, größte Abweichung JS/Python {maxdiff:.4f} €")
    assert anteil(2023) == 0.825 and anteil(2058) == 1.0 and anteil(2026) == 0.84
    maxr = 0
    for f in RENTEN:
        py = netto_rente(f["brutto_monat"], f["rentenbeginn_jahr"], f["verheiratet"], f["partner_brutto_monat"], f["kirche"], f["bundesland"],
                         kv=f["kv"], zb=f["zusatzbeitrag"], pkv=f["pkv_beitrag_monat"], kinderlos=f["kinderlos"])
        j = js_rente(f)["netto_monat"]
        maxr = max(maxr, abs(py - j)); assert abs(py - j) < 0.01, (f, py, j)
    print(f"{len(RENTEN)} Rentenfälle, größte Abweichung JS/Python {maxr:.4f} €")
    # Vorzeitige Rente: eigene Rechnung
    def vorzeitig(bisher, hoch, alter, beginn, j45=False, rag=67):
        if beginn >= rag or alter >= rag: return hoch
        ohne = bisher + (hoch - bisher) / (rag - alter) * max(0, beginn - alter)
        ab = 0 if (j45 and beginn >= 65) else min(round((rag - beginn) * 12), 48) * 0.003
        return round(ohne * (1 - ab), 2)
    for bisher, hoch, alter, beginn, j45 in itertools.product([600, 900], [1500, 2100], [30, 38, 55], [63, 64, 65, 66, 67], [False, True]):
        j = json.loads(subprocess.check_output(["node", "-e", f"const R=require('{HIER/'rechenkern.js'}');console.log(JSON.stringify(R.renteVorzeitig({json.dumps(dict(bisher=bisher, hochrechnung=hoch, alter=alter, beginn_alter=beginn, versicherungsjahre_45=j45))})))"]))
        assert abs(j["brutto"] - vorzeitig(bisher, hoch, alter, beginn, j45)) < 0.01, (bisher, hoch, alter, beginn, j45, j)
    print("Vorzeitige Rente: 120 Fälle gleich")
    # Weitere Einkünfte: eigene Abschrift (Abgeltung § 32d Abs. 1, Günstigerprüfung § 32d Abs. 6, Sparer-Pauschbetrag § 20 Abs. 9,
    # Teilfreistellung § 20 InvStG, bAV-Beiträge § 226 Abs. 2 / § 248 SGB V, Ertragsanteil § 22 Nr. 1 S. 3 a bb EStG)
    def st_tarif(zves, verh, kist):
        if verh:
            z = sum(zves); e = 2 * tarif_2026(z / 2); return e + soli(e, 40700) + e * kist
        return sum(tarif_2026(z) + soli(tarif_2026(z), 20350) + tarif_2026(z) * kist for z in zves)
    def py_mehr(basis, tarif, kapital, verh, kist):
        tz = [max(0, b + t) for b, t in zip(basis, tarif)]
        ohne, mit = st_tarif(basis, verh, kist), st_tarif(tz, verh, kist)
        if verh: rest = [max(0, sum(kapital) - 1000 * len(basis))] + [0] * (len(basis) - 1)
        else: rest = [max(0, k - 1000) for k in kapital]
        abg = sum(rest) / (4 + kist) * (1 + 0.055 + kist)
        tk = st_tarif([z + r for z, r in zip(tz, rest)], verh, kist) - mit
        return mit - ohne + (min(abg, tk) if sum(rest) > 0 else 0)
    n = 0
    for b1, b2, t, k, verh, kist in itertools.product([0, 9000, 20000, 60000], [0, 15000], [0, 6000, -3000], [0, 800, 5000, 40000], [False, True], [0, 0.09]):
        basis = [b1, b2] if b2 else [b1]; tarif = [t] + [0] * (len(basis) - 1); kap = [k] + [0] * (len(basis) - 1)
        m = dict(basis=basis, tarif=tarif, kapital=kap, verheiratet=verh, kinder=0, kirche=kist > 0, bundesland="NW")
        j = json.loads(subprocess.check_output(["node", "-e", f"const R=require('{HIER/'rechenkern.js'}');console.log(JSON.stringify(R.mehrsteuer({json.dumps(m)})))"]))
        py = py_mehr(basis, tarif, kap, verh, kist)
        assert abs(j["gesamt"] - py) < 0.02, (m, j, py); n += 1
    print(f"Weitere Einkünfte, Mehrsteuer: {n} Fälle gleich")
    # Haushalt im Alter: eigene Rechnung aus rente_zve und py_mehr
    def py_haushalt(pers, verh, kist):
        rows = []
        for b, jahr, kv, pkv, w in pers:
            z, abz = rente_zve(b, jahr, kv=kv, pkv=pkv)
            bav = w.get("bav", 0)
            kvb = 0 if kv == "pkv" else max(0, bav - 197.75) * (0.146 + 0.029) * 12
            pvb = 0 if kv == "pkv" or bav <= 197.75 else bav * 0.036 * 12
            rows.append((b, z, abz, w, kvb, pvb))
        basis = [r[1] for r in rows]
        grund = st_tarif(basis, verh, kist)
        mehr = py_mehr(basis, [r[3].get("tarif", 0) - r[4] - r[5] for r in rows], [r[3].get("kapital", 0) for r in rows], verh, kist)
        return (sum(b * 12 - abz["kv"] - abz["pv"] + abz["zu"] + w.get("cash", 0) - kvb - pvb for b, z, abz, w, kvb, pvb in rows) - grund - mehr) / 12
    n = 0
    for b1, b2, verh, kist, w1 in itertools.product([900, 1600, 2400], [0, 700, 1500], [False, True], [0, 0.09],
            [{}, dict(cash=10800, tarif=10800), dict(cash=3000, kapital=2600), dict(cash=3120, tarif=3120, bav=260)]):
        pers = [(b1, 2050, "gkv", 0, w1)] + ([(b2, 2053, "gkv", 0, {})] if b2 else [])
        h = dict(verheiratet=verh, kirche=kist > 0, bundesland="NW", kinderlos=False, personen=[dict(brutto_monat=b, rentenbeginn_jahr=j, kv=kv,
            weitere=dict(cash=w.get("cash", 0), tarif=w.get("tarif", 0), kapital=w.get("kapital", 0), bav_monat=w.get("bav", 0))) for b, j, kv, pkv, w in pers])
        j = json.loads(subprocess.check_output(["node", "-e", f"const R=require('{HIER/'rechenkern.js'}');console.log(JSON.stringify(R.nettoRenteHaushalt({json.dumps(h)})))"]))
        py = py_haushalt(pers, verh, kist)
        assert abs(j["netto_monat"] - py) < 0.05, (h, j["netto_monat"], py); n += 1
    print(f"Haushalt im Alter: {n} Fälle gleich")
    def ek(e, z):
        return json.loads(subprocess.check_output(["node", "-e", f"const R=require('{HIER/'rechenkern.js'}');console.log(JSON.stringify(R.einkunft({json.dumps(e)}, '{z}')))"]))
    r = ek(dict(art="kapital", kapart="aktien", waehrung="USD", kurs=1.1206, betrag=1200), "heute")
    assert abs(r["cash"] - 1200 / 1.1206) < 1e-6 and abs(r["kapital"] - 1200 / 1.1206) < 1e-6
    r = ek(dict(art="kapital", kapart="aktienfonds", betrag=1800), "heute"); assert abs(r["kapital"] - 1260) < 1e-6
    r = ek(dict(art="miete", modus="euer", miete=12000, kosten=1500, zinsen=3000, tilgung=4000, afa=2400), "heute")
    assert r["tarif"] == 12000 - 1500 - 3000 - 2400 and r["cash"] == 12000 - 1500 - 3000 - 4000
    r = ek(dict(art="miete", modus="pauschal", betrag=450, betrag_alter=900), "alter"); assert r["cash"] == r["tarif"] == 10800
    r = ek(dict(art="bav", betrag=260), "heute"); assert not r["gilt"]
    r = ek(dict(art="privatrente", betrag=500, beginn_alter=65), "alter"); assert r["tarif"] == 500 * 12 * 0.18
    r = ek(dict(art="privatrente", betrag=500, beginn_alter=50), "alter"); assert r["fehler"] == "ertragsanteil"
    r = ek(dict(art="kapital", waehrung="USD", betrag=100), "heute"); assert r["fehler"] == "kurs"
    print("Einkunftsarten: Umrechnung, EÜR, Teilfreistellung, Ertragsanteil geprüft")
    # Beispiel Günstigerprüfung: kleine Rente, Dividenden 6.000 €
    j = json.loads(subprocess.check_output(["node", "-e", f"const R=require('{HIER/'rechenkern.js'}');console.log(JSON.stringify(R.mehrsteuer({{basis:[9000],tarif:[0],kapital:[6000],verheiratet:false,kinder:0}})))"]))
    print("Beispiel zvE 9.000 € + 6.000 € Dividenden:", j)
    for b in (1500, 2200):
        r = js_rente(dict(brutto_monat=b, rentenbeginn_jahr=2051, kv="gkv", kinderlos=False))
        print(f"Beispiel {b} € brutto, Beginn 2051, GKV, Eltern: netto {r['netto_monat']} € (KV {r['kv_monat']}, PV {r['pv_monat']}, Steuer {r['steuer_monat']}, Anteil {r['besteuerungsanteil']:.3f})")
