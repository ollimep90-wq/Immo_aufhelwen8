#!/usr/bin/env python3
"""Drei Finanzierungsoptionen: Nachbeleihung, Verkäuferdarlehen, WEG-Teilung.

    python3 analysen/finanzierungsoptionen.py --strategie <Vault>/.../Strategie

Dieses Skript rechnet **nichts selbst**, was `modell.py` schon kann. Es
importiert `modell.py` aus dem Strategie-Ordner und liest `annahmen.json` von
dort — beides ist nach CLAUDE.md die einzige zulässige Quelle für Zahlen und
Finanzmathematik. Ohne `--strategie` läuft es nicht; Platzhalter wären hier
genau die Fehlerquelle, die das Projekt vermeiden will.

Was es hinzufügt, sind drei Auswertungen, die `modell.py` nicht kennt:
Nachbeleihungsspielraum über die Zeit, Wirkung eines Verkäuferdarlehens auf
den Eigenkapitalbedarf, und die Rechnung zur WEG-Teilung.

Die Parameter unten sind Annahmen für genau diese drei Fragen und stehen
bewusst nicht in annahmen.json, solange die Bank sie nicht bestätigt hat.

Keine Rechts-, Steuer- oder Anlageberatung.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

# --------------------------------------------------------------- PARAMETER
# Annahmen für diese drei Fragen. Bei der Bank zu erfragen, dann nach
# annahmen.json überführen.
PARAMETER = {
    "vd_zins_pct":            4.0,   # Verkäuferdarlehen
    "teilungskosten":      15_000,   # Abgeschlossenheit + Plan + Notar + Grundbuch
    "wert_faktor":             12,   # Projektansatz für Wertzuwachs aus Mehrmiete
    "nebengebaeude_jahr":   4_200,   # Reihenfolge-der-Optimierungen.md, Rang 1
    "kappung_559e_eur_m2":   0.50,   # § 559e Abs. 3 BGB, in sechs Jahren
    # BEG-EM ab 21.07.2026 — Rechtsprüfung 2026-09-12
    "beg_grundfoerderung_pct":  30,
    "beg_hoechst_erste_we": 28_000,
    "beg_hoechst_we_2_6":   15_000,
    "beg_hoechst_ab_we_7":   8_000,
}


def lade_modell(strategie: Path):
    """modell.py aus dem Strategie-Ordner importieren."""
    mp = strategie / "modell.py"
    if not mp.is_file():
        sys.exit(f"modell.py nicht gefunden in {strategie}\n"
                 f"--strategie muss auf den Ordner mit annahmen.json und modell.py zeigen.")
    spec = importlib.util.spec_from_file_location("modell", mp)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(strategie))
    spec.loader.exec_module(mod)
    return mod


def eur(x) -> str:
    return "—" if x is None else f"{x:,.0f}".replace(",", ".")


def kopf(t):
    print("\n" + "=" * 76)
    print(t)
    print("=" * 76)


# ----------------------------------------------------------------- Blöcke
def basis(modell, a, kp):
    kopf("0  AUSGANGSLAGE — gerechnet von modell.py")
    r = modell.rechne(kp, a=a, vk_miete_eur_m2=a["mieten"]["haus_a_verkaeufermiete_eur_m2"])
    f = a["finanzierung"]
    print(f"  Kaufpreis                              {eur(r['kaufpreis']):>12}")
    print(f"  Kaufnebenkosten {r['nk_pct']:.1f} %                {eur(r['nebenkosten']):>12}")
    print(f"  Gesamtbedarf                           {eur(r['gesamtbedarf']):>12}")
    print()
    print(f"  Bankdarlehen ({f['beleihungsauslauf_max_pct']} % des Kaufpreises)  {eur(r['darlehen']):>12}")
    print(f"  Eigenkapital benötigt                  {eur(r['ek_benoetigt']):>12}")
    print(f"  Restliquidität aus {eur(f['eigenkapital'])} EK          {eur(r['restliquiditaet']):>12}")
    print()
    print(f"  Volltilger {f['laufzeit_jahre']} J zu {f['sollzins_pct']} %, Annuität {r['annuitaet_pct']:.3f} %")
    print(f"    Rate                                 {eur(r['rate_monat']):>12} /Monat")
    print(f"    Zins Jahr 1 / Tilgung Jahr 1         {eur(r['zins_j1']):>12} / {eur(r['tilgung_j1'])}")
    print()
    print(f"  Miete                                  {eur(r['miete_monat']):>12} /Monat")
    print(f"  NOI                                    {eur(r['noi']):>12} p.a.")
    print(f"  Cashflow                               {eur(r['cashflow']):>12} p.a."
          f" = {eur(r['cashflow_monat'])}/Monat")
    print(f"  Faktor {r['faktor']:.1f}, Bruttorendite {r['bruttorendite']:.2f} %, "
          f"Nettorendite {r['nettorendite']:.2f} %")
    print()
    print("  ! Der Beleihungsauslauf bezieht sich hier auf den KAUFPREIS. Ob die Bank")
    print("    so rechnet oder auf einen Beleihungswert mit Sicherheitsabschlag, ist")
    print("    eine Annahme in annahmen.json — und die offene Frage an Wüstenrot aus")
    print("    Finanzierung-und-Sensitivitaet.md. Bei 10 % Abschlag läge derselbe")
    print(f"    Betrag bei {r['darlehen'] / (kp * 0.9) * 100:.1f} % statt "
          f"{f['beleihungsauslauf_max_pct']} %.")
    return r


def option1(modell, a, r, kp):
    kopf("1  NACHBELEIHUNG")
    f = a["finanzierung"]
    quote = f["beleihungsauslauf_max_pct"] / 100
    print(f"  Spielraum = {quote * 100:.0f} % des Werts minus Restschuld.\n")
    print(f"  {'Jahr':>5} {'Restschuld':>13} " + "".join(
        f"{'Wert +' + str(x) + '%':>13}" for x in (0, 5, 10, 15)))
    for j in (1, 3, 5, 7, 10):
        rs = r["plan"][j - 1]["restschuld"]
        z = f"  {j:>5} {eur(rs):>13}"
        for x in (0, 5, 10, 15):
            z += f"{eur(kp * (1 + x / 100) * quote - rs):>13}"
        print(z)

    print("\n  Der Test, auf den es ankommt: hebt eine Maßnahme den Wert um mehr,")
    print("  als sie die Schuld erhöht?\n")
    fak = PARAMETER["wert_faktor"]
    neben = PARAMETER["nebengebaeude_jahr"]
    print(f"  a) Nebengebäude separat vermieten (Reihenfolge-der-Optimierungen, Rang 1)")
    print(f"     Mehrmiete {eur(neben)} p.a., Investition 0 EUR")
    print(f"     Wertzuwachs bei Faktor {fak}:        {eur(neben * fak):>10}")
    print(f"     davon {quote * 100:.0f} % Beleihungskapazität:  {eur(neben * fak * quote):>10}")
    print(f"     Mehrschuld:                      {eur(0):>10}")
    print(f"     -> Netto {eur(neben * fak * quote)} zusätzlicher Spielraum.")

    inv = a["investitionen"]
    paket = (inv["wp_haus_a"] + inv["wp_haus_b"] + inv["heizkoerper_typ33_haus_b"]
             + inv["hydraulik_speicher_ww"] + inv["entsorgung_kessel_tanks"])
    zuschuss = PARAMETER["beg_grundfoerderung_pct"] / 100
    netto = paket * (1 - zuschuss)
    umlage = a["modernisierungsfinanzierung"]["modernisierungsumlage_haus_b_jahr"]
    print(f"\n  b) Heizungspaket (WP beide Häuser, Heizkörper, Hydraulik, Entsorgung)")
    print(f"     Kosten brutto:                   {eur(paket):>10}")
    print(f"     ./. {PARAMETER['beg_grundfoerderung_pct']} % Grundförderung:        {eur(netto):>10}  = Mehrschuld")
    print(f"     Modernisierungsumlage:           {eur(umlage):>10} p.a.")
    print(f"     Wertzuwachs bei Faktor {fak}:        {eur(umlage * fak):>10}")
    print(f"     davon {quote * 100:.0f} % Beleihungskapazität:  {eur(umlage * fak * quote):>10}")
    print(f"     -> Differenz {eur(umlage * fak - netto)}. Die Maßnahme VERBRAUCHT Spielraum.")
    print("\n  Und bis 2028/2029 ist der Bestand ohnehin eingefroren: die Kappungs-")
    print("  grenze des § 558 Abs. 3 BGB ist ausgeschöpft (Mietstruktur.md).")


def option2(modell, a, r, kp):
    kopf("2  VERKÄUFERDARLEHEN")
    f = a["finanzierung"]
    print(f"  Das Bankdarlehen ist bei {f['beleihungsauslauf_max_pct']} % des Kaufpreises gedeckelt.")
    print("  Ein Verkäuferdarlehen kann es also nicht verbilligen — es ersetzt")
    print("  EIGENKAPITAL und wirkt damit auf die Restliquidität.\n")
    print(f"  {'VD':>9} {'EK benötigt':>13} {'Restliquidität':>15} "
          f"{'VD-Zins':>10} {'Cashflow danach':>16}")
    for vd in (0, 20_000, 50_000, 100_000):
        ek = r["ek_benoetigt"] - vd
        rest = f["eigenkapital"] - ek
        zins = vd * PARAMETER["vd_zins_pct"] / 100
        print(f"  {eur(vd):>9} {eur(ek):>13} {eur(rest):>15} "
              f"{eur(zins):>10} {eur(r['cashflow'] - zins):>16}")
    print(f"\n  VD-Zins: {PARAMETER['vd_zins_pct']} % (Annahme). Die Regel aus")
    print("  Reihenfolge-der-Optimierungen: der Puffer darf nie unter zwei")
    print("  Monatsmieten (rund 10.700 EUR) fallen.")

    print("\n  Die andere Verwendung — höherer Kaufpreis bei gleichem Eigenkapital:\n")
    mx = modell.max_kaufpreis_ek(0.0, a=a)
    print(f"  {'VD':>9} {'tragbarer Kaufpreis':>21} {'Hebel':>12}")
    print(f"  {eur(0):>9} {eur(mx):>21} {'—':>12}")
    import copy
    for vd in (20_000, 50_000):
        a2 = copy.deepcopy(a)
        a2["finanzierung"]["eigenkapital"] = f["eigenkapital"] + vd
        mx2 = modell.max_kaufpreis_ek(0.0, a=a2)
        print(f"  {eur(vd):>9} {eur(mx2):>21} {'+' + eur(mx2 - mx):>12}")
    print("\n  Jeder Euro hebt den tragbaren Preis um rund 7,70 EUR, weil nur 5 %")
    print("  Eigenanteil plus 8,5 % Nebenkosten aus Eigenkapital kommen müssen.")
    print("  Das ist ein Grund für PUFFER, nicht für ein höheres Gebot: der Zielpreis")
    print("  740.000 EUR steht im Entscheidungsregister und ist aus Mängeln und")
    print("  Restliquidität hergeleitet, nicht aus dem, was die Bank noch mitmacht.")


def option3(modell, a, r, kp):
    kopf("3  WEG-TEILUNG")
    f = a["finanzierung"]
    quote = f["beleihungsauslauf_max_pct"] / 100
    tk = PARAMETER["teilungskosten"]
    we = a["objekt"]["einheiten"]
    rs = r["plan"][2]["restschuld"]
    print(f"  Restschuld Jahr 3 {eur(rs)}, Teilungskosten {eur(tk)} (Annahme).\n")
    print(f"  {'Aufschlag':>10} {'Wert':>12} {'{:.0f} % davon'.format(quote * 100):>13} "
          f"{'./. Restschuld':>16} {'./. Kosten':>13}")
    for auf in (0, 5, 10, 15, 20):
        w = kp * (1 + auf / 100)
        frei = w * quote - rs
        print(f"  {auf:>8} % {eur(w):>12} {eur(w * quote):>13} {eur(frei):>16} {eur(frei - tk):>13}")

    neben = PARAMETER["nebengebaeude_jahr"] * PARAMETER["wert_faktor"] * quote
    print(f"\n  Zum Vergleich: die Nebengebäude bringen {eur(neben)} Beleihungskapazität")
    print("  für 0 EUR, ohne Teilung, ohne Steuerrisiko, ab Übergabe.")
    print(f"\n  Steuerlich: das Objekt hat {we} Einheiten (Zielzustand 9). Jede WEG-Einheit")
    print("  ist ein eigenes Objekt i.S.d. Drei-Objekt-Grenze (BMF 26.03.2004,")
    print("  BFH GrS 1/98). Aus einem Objekt würden sieben bis neun — bei einer")
    print("  Umqualifizierung entfallen AfA und § 23 EStG, dazu Gewerbesteuer.")
    print("  Das kollidiert mit der Entscheidung 'Erwerb privat'.")


def foerderung(a):
    kopf("4  FÖRDERUNG — Projektstand gegen BEG-EM ab 21.07.2026")
    P = PARAMETER
    def grenze(we, erste):
        return erste + min(max(we - 1, 0), 5) * 15_000 + max(we - 6, 0) * 8_000
    we = a["objekt"]["einheiten"]
    alt_1, neu_1 = grenze(we, 30_000), grenze(we, P["beg_hoechst_erste_we"])
    alt_2 = grenze(6, 30_000) + grenze(1, 30_000)
    neu_2 = grenze(6, P["beg_hoechst_erste_we"]) + grenze(1, P["beg_hoechst_erste_we"])
    print(f"  {'Konstellation':<32} {'Projektstand':>14} {'ab 21.07.2026':>15} {'Diff':>10}")
    print(f"  {'Ein Wohngebäude, ' + str(we) + ' WE':<32} {eur(alt_1):>14} {eur(neu_1):>15} {eur(neu_1 - alt_1):>10}")
    print(f"  {'Zwei Wohngebäude (6 + 1 WE)':<32} {eur(alt_2):>14} {eur(neu_2):>15} {eur(neu_2 - alt_2):>10}")
    print(f"\n  annahmen.json führt hoechstgrenze_ein_gebaeude: "
          f"{eur(a['foerderung']['hoechstgrenze_ein_gebaeude'])}")
    fo = a["foerderung"]
    inv = a["investitionen"]
    paket = (inv["wp_haus_a"] + inv["wp_haus_b"] + inv["heizkoerper_typ33_haus_b"]
             + inv["hydraulik_speicher_ww"] + inv["entsorgung_kessel_tanks"])
    alt_satz = fo["grundfoerderung_pct"] + fo["effizienzbonus_pct"]
    neu_satz = P["beg_grundfoerderung_pct"]
    print(f"\n  Fördersatz auf ein Paket von {eur(paket)}:")
    print(f"    annahmen.json {alt_satz} % (30 + {fo['effizienzbonus_pct']} Effizienzbonus): "
          f"{eur(paket * alt_satz / 100)}")
    print(f"    ab 21.07.2026 {neu_satz} % (Effizienzbonus entfallen):  {eur(paket * neu_satz / 100)}")
    print(f"    Differenz: {eur(paket * (alt_satz - neu_satz) / 100)} weniger Zuschuss")
    print("\n  Und: der Höchstbetrag der ersten WE sinkt ab 01.02.2027 halbjährlich")
    print("  um 750 EUR. Maßgeblich ist der Zeitpunkt der Antragstellung — das")
    print("  kollidiert mit 'Umsetzung gebündelt nach dem Auszug'.")


def umlage_kappung(a):
    kopf("5  MODERNISIERUNGSUMLAGE gegen § 559e Abs. 3 BGB")
    o = a["objekt"]
    kap = PARAMETER["kappung_559e_eur_m2"]
    umlage = a["modernisierungsfinanzierung"]["modernisierungsumlage_haus_b_jahr"]
    print(f"  Kappung {kap:.2f} EUR/m² in sechs Jahren.\n")
    for name, m2, u in [("Anbau (Haus B)", o["wohnflaeche_haus_b_m2"], umlage),
                        ("Altbestand (Haus A)", o["wohnflaeche_haus_a_m2"], None)]:
        deckel = m2 * kap * 12
        print(f"  {name}, {m2:.0f} m²")
        print(f"    Kappungsgrenze            {eur(deckel):>10} p.a.")
        if u:
            print(f"    annahmen.json setzt an    {eur(u):>10} p.a. = {u / 12 / m2:.3f} EUR/m²")
            print(f"    -> {'unter der Kappung, plausibel' if u <= deckel else 'ÜBER der Kappung'}")
        else:
            print("    Hier gilt die Indexmiete (§ 557b BGB). Sie sperrt § 559 grundsätzlich,")
            print("    ABER § 557b Abs. 2 S. 2 enthält eine Rückausnahme für Maßnahmen nach")
            print("    § 555b Nr. 1a (Heizungseinbau). Die Wärmepumpe ist also umlagefähig —")
            print(f"    gekappt bei {eur(deckel)} EUR p.a. Alles andere (Dämmung, FBH) nicht.")
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strategie", required=True,
                    help="Ordner mit annahmen.json und modell.py")
    ap.add_argument("--kaufpreis", type=float,
                    help="Kaufpreis (Vorgabe: Zielpreis 740.000)")
    args = ap.parse_args()

    strategie = Path(args.strategie).expanduser().resolve()
    modell = lade_modell(strategie)
    a = modell.annahmen()
    kp = args.kaufpreis or 740_000

    print(f"Quelle: {strategie}")
    print(f"annahmen.json, Stand {a.get('stand', '?')}")
    print(f"Finanzmathematik: modell.py (Regel 1 — nicht im Kopf, nicht hier nachgebaut)")

    r = basis(modell, a, kp)
    option1(modell, a, r, kp)
    option2(modell, a, r, kp)
    option3(modell, a, r, kp)
    foerderung(a)
    umlage_kappung(a)
    print("\n" + "=" * 76)
    print("Keine Rechts-, Steuer- oder Anlageberatung.")
    print("=" * 76)


if __name__ == "__main__":
    main()
