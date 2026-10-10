"""Alle Rechenbeispiele der Privat-Unterlagen. Einzige Quelle für Zahlen in den Präsentationen.

Jede Zahl ist ein Rechenbeispiel auf Basis der unten stehenden Annahmen, keine Prognose.
Aufruf zur Kontrolle: python3 zahlen.py
"""

def fv_sparplan(rate, jahre, rendite, kosten=0.0):
    """Endwert monatlicher Einzahlung, Zins (r - c)/12, nachschüssig (wie STATUS.md)."""
    i = (rendite - kosten) / 12
    n = jahre * 12
    return rate * ((1 + i) ** n - 1) / i

def rente_barwert(jahresbetrag, jahre, zins):
    """Kapital für eine nachschüssige Monatsrente (Jahresbetrag/12) über n Jahre."""
    i = zins / 12
    n = jahre * 12
    return jahresbetrag / 12 * (1 - (1 + i) ** -n) / i

def sparrate_fuer(ziel, jahre, rendite):
    i = rendite / 12
    n = jahre * 12
    return ziel * i / ((1 + i) ** n - 1)

def annuitaet(darlehen, zins, tilgung):
    return darlehen * (zins + tilgung) / 12

def restschuld(darlehen, zins, rate_monat, jahre):
    i = zins / 12
    rest = darlehen
    for _ in range(jahre * 12):
        rest = rest * (1 + i) - rate_monat
    return rest

def eur(x):
    return f"{round(x):,}".replace(",", ".") + " €"

# Annahmen
RENDITE = 0.06          # Rendite vor Kosten p. a. (Annahme, wie STATUS.md)
KOSTEN = 0.013          # Strategiedepot 1,0 % + ca. 0,3 % Fonds (STATUS.md)
INFLATION = 0.02        # Annahme
ENTNAHME_REAL = 0.01    # reale Rendite in der Entnahmephase (Annahme)

Z = {}
# Arbeitskraft
Z["ak_netto"] = eur(3000)
Z["ak_wert"] = eur(3000 * 12 * 35)
# Zinseszins / Warten
Z["zz_einzahlung"] = eur(200 * 12 * 30)
Z["zz_endwert"] = eur(fv_sparplan(200, 30, RENDITE, KOSTEN))
ab30 = fv_sparplan(200, 37, RENDITE, KOSTEN)
ab40 = fv_sparplan(200, 27, RENDITE, KOSTEN)
Z["warten_ab30"] = eur(ab30)
Z["warten_ab40"] = eur(ab40)
Z["warten_diff"] = eur(ab30 - ab40)
Z["warten_einz_diff"] = eur(200 * 12 * 10)
Z["warten_bar"] = f"{560 * ab40 / ab30:.1f}"          # Balkenbreite in px, 560 = ab30
Z["zz_bar"] = f"{560 * 200 * 12 * 30 / fv_sparplan(200, 30, RENDITE, KOSTEN):.1f}"
Z["warten_txt"] = f"{140 + float(Z['warten_bar']) + 10:.0f}"
Z["zz_txt"] = f"{140 + float(Z['zz_bar']) + 10:.0f}"
# Kostenvergleich (vermoegen.html): 200 €/Monat, 30 Jahre
kv = {"03": 0.003, "08": 0.008, "13": 0.013, "20": 0.020}
kv_end = {k: fv_sparplan(200, 30, RENDITE, c) for k, c in kv.items()}
for k, v in kv_end.items():
    Z[f"kv_end{k}"] = eur(v)
    Z[f"kv_bar{k}"] = f"{476 * v / kv_end['03']:.1f}"
    Z[f"kv_txt{k}"] = f"{190 + 476 * v / kv_end['03'] + 10:.0f}"
# Rentenlücke in heutiger Kaufkraft
netto, ziel_quote, gesetzl = 3000, 0.8, 1300
luecke = netto * ziel_quote - gesetzl
Z["rl_netto"], Z["rl_ziel"], Z["rl_gesetzl"], Z["rl_luecke"] = eur(netto), eur(netto * ziel_quote), eur(gesetzl), eur(luecke)
Z["rl_luecke_nominal"] = eur(luecke * (1 + INFLATION) ** 30)
kapital_real = rente_barwert(luecke * 12, 25, ENTNAHME_REAL)
Z["rl_kapital"] = eur(kapital_real)
real_anspar = (1 + RENDITE - KOSTEN) / (1 + INFLATION) - 1
Z["rl_sparrate"] = eur(sparrate_fuer(kapital_real, 30, real_anspar))
Z["rl_real_anspar"] = f"{real_anspar*100:.1f} %".replace(".", ",")
# Notreserve
Z["nr_ausgaben"] = eur(2500)
Z["nr_von"], Z["nr_bis"] = eur(2500 * 3), eur(2500 * 6)
# Finanzierung
d, zins, tilg = 400000, 0.038, 0.02
rate = annuitaet(d, zins, tilg)
Z["fin_darlehen"], Z["fin_rate"] = eur(d), eur(rate)
Z["fin_rest10"] = eur(restschuld(d, zins, rate, 10))
Z["fin_zins"] = f"{zins*100:.1f} %".replace(".", ",")
Z["fin_tilg"] = f"{tilg*100:.0f} %"
def laufzeit(darlehen, zins, rate_monat):
    assert rate_monat > darlehen * zins / 12, "Rate deckt die Zinsen nicht"
    r, n = darlehen, 0
    while r > 0:
        r = r * (1 + zins / 12) - rate_monat
        n += 1
    return n / 12
Z["fin_lz2"] = f"{laufzeit(d, zins, rate):.0f}"
rate3 = annuitaet(d, zins, 0.03)
Z["fin_rate3"] = eur(rate3)
Z["fin_rest10_3"] = eur(restschuld(d, zins, rate3, 10))
Z["fin_lz3"] = f"{laufzeit(d, zins, rate3):.0f}"
kp = 450000
Z["nk_kaufpreis"] = eur(kp)
Z["nk_grest"] = eur(kp * 0.065)
Z["nk_notar"] = eur(kp * 0.02)
Z["nk_makler"] = eur(kp * 0.0357)
Z["nk_summe"] = eur(kp * (0.065 + 0.02 + 0.0357))
Z["nk_quote"] = f"{(0.065+0.02+0.0357)*100:.2f} %".replace(".", ",")
Z["fin_gesamt"] = eur(kp * (1 + 0.065 + 0.02 + 0.0357))
Z["fin_ek"] = eur(kp * (1 + 0.065 + 0.02 + 0.0357) - d)
Z["fin_ek_ueber_nk"] = eur(kp - d)
# Kaufpreisfaktor
Z["kpf_miete"], Z["kpf_preis"] = eur(1250), eur(300000)
Z["kpf_faktor"] = f"{300000/(1250*12):.0f}"
Z["kpf_rendite"] = f"{1250*12/300000*100:.1f} %".replace(".", ",")

if __name__ == "__main__":
    for k, v in Z.items():
        print(f"{k:20s} {v}")
