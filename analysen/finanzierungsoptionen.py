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
    "vd_zins_pct":            4.0,   # Verkäuferdarlehen, tilgungsfrei unterstellt
    "teilungskosten":      15_000,   # Abgeschlossenheit + Plan + Notar + Grundbuch
    "wert_faktor":             12,   # Projektansatz (Reihenfolge-der-Optimierungen)
    "sicherheitsabschlag_pct": 10,   # NUR für die Gegenrechnung "was wäre wenn"
    "kappung_559e_eur_m2":   0.50,   # § 559e Abs. 3 BGB, in sechs Jahren
    "umlage_559e_pct":         10,   # § 559e Abs. 1 BGB (§ 559: 8 %)
    # BEG-EM ab 21.07.2026 — Rechtsprüfung 2026-09-12, vor Antragstellung bestätigen
    "beg_grundfoerderung_pct":  30,
    "beg_hoechst_erste_we": 28_000,
    "beg_hoechst_we_2_6":   15_000,
    "beg_hoechst_ab_we_7":   8_000,
    "beg_hoechst_erste_we_alt": 30_000,   # Projektstand vor dem 21.07.2026
    "beg_effizienzbonus_alt_pct":   5,   # entfallen zum 21.07.2026
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


def nebenkosten_quote(a) -> float:
    kn = a["kaufnebenkosten"]
    return (kn["grunderwerbsteuer_pct"] + kn["notar_pct"]
            + kn["grundbuch_pct"] + kn["makler_pct"]) / 100 + 1.0


def heizungspaket(a) -> tuple[float, float]:
    """Der Planwert aus Heizung-und-Energetische-Sanierung.md: alle sechs
    Positionen einschließlich Fußbodenheizung Altbestand. Der Vault trägt
    dafür 103.500 EUR brutto und 72.450 EUR Eigenanteil nach 30 %."""
    inv = a["investitionen"]
    paket = (inv["wp_haus_a"] + inv["wp_haus_b"] + inv["heizkoerper_typ33_haus_b"]
             + inv["fbh_haus_a"] + inv["hydraulik_speicher_ww"]
             + inv["entsorgung_kessel_tanks"])
    netto = paket * (1 - PARAMETER["beg_grundfoerderung_pct"] / 100)
    return paket, netto


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
    m = a["mieten"]
    print("  Die Miete ist zu einem Viertel unbelegt:")
    print(f"    Anbau, bestaetigt              {eur(m['haus_b_ist_monat']):>10} /Monat")
    hoch = m["haus_a_verkaeufermiete_eur_m2"]
    tief = m["haus_a_bestandsniveau_eur_m2"]
    flaeche = a["objekt"]["wohnflaeche_haus_a_m2"]
    print(f"    Altbestand — noch zu vereinbaren, Korridor belegt,"
          f" Punkt darin nicht")
    korridor = m.get("haus_a_korridor_eur_m2", [tief, hoch])
    lo, hi = min(korridor), max(korridor)
    mitte = (lo + hi) / 2
    print(f"\n    {'Verkaeufermiete':<26} {'Miete/Monat':>13} {'Cashflow p.a.':>15} {'/Monat':>10}")
    ergebnisse = []
    for label, satz in [(f"{lo:.2f} EUR/m2 (untere Ecke)", lo),
                        (f"{mitte:.2f} EUR/m2 (Mitte)", mitte),
                        (f"{hi:.2f} EUR/m2 (obere Ecke)", hi)]:
        rr = modell.rechne(kp, a=a, vk_miete_eur_m2=satz)
        ergebnisse.append(rr)
        print(f"    {label:<26} {eur(rr['miete_monat']):>13} {eur(rr['cashflow']):>15} "
              f"{eur(rr['cashflow_monat']):>10}")
    d = ergebnisse[-1]["cashflow"] - ergebnisse[0]["cashflow"]
    print(f"    Spanne: {eur(d)} p.a. = {d / ergebnisse[-1]['cashflow'] * 100:.0f} % des Cashflows")
    print(f"    Bandbreite der Miete bei {flaeche:.0f} m2: "
          f"{eur(lo * flaeche)} bis {eur(hi * flaeche)} EUR/Monat")
    print(f"    (Flaeche selbst ist 140-150 m2, nie exakt gemessen)")
    print()
    print("  ! Der Beleihungsauslauf bezieht sich hier auf den KAUFPREIS. Ob die Bank")
    print("    so rechnet oder auf einen Beleihungswert mit Sicherheitsabschlag, ist")
    print("    eine Annahme in annahmen.json — und die offene Frage an Wüstenrot aus")
    print("    Finanzierung-und-Sensitivitaet.md. Bei 10 % Abschlag läge derselbe")
    sa = PARAMETER["sicherheitsabschlag_pct"]
    print(f"    Betrag bei {r['darlehen'] / (kp * (1 - sa / 100)) * 100:.1f} % statt "
          f"{f['beleihungsauslauf_max_pct']} % (Abschlag {sa} % = Annahme).")
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
    b = a["bewirtschaftung"]
    nb = a["ausbau"]["nebengebaeude"]
    anzahl = sum(n for _, n, _ in nb)
    brutto = sum(n * m * 12 for _, n, m in nb)
    print(f"  a) Nebengebäude separat vermieten (Reihenfolge-der-Optimierungen, Rang 1)")
    print(f"     {anzahl} freie Einheiten, Investition 0 EUR, Bruttomiete {eur(brutto)} p.a.")
    for name, n, mo in nb:
        print(f"       {name:<28} {n} x {mo:>3} EUR")
    nicht = a["ausbau"].get("nebengebaeude_nicht_hebbar", [])
    if nicht:
        print(f"     Nicht hebbar:")
        for name, grund in nicht:
            print(f"       {name:<28} {grund}")
    print()
    print(f"     Die Mietansätze sind UNBELEGT — sie stammen aus einer frühen")
    print(f"     Projektfassung, nicht vom Nutzer (annahmen.json, _quelle_nebengebaeude).")
    print(f"     Belegt ist nur, WELCHE Einheiten frei sind. Deshalb eine Spanne:")
    print()
    print(f"     {'Ansatz':<38} {'netto p.a.':>11} {'Kapazität':>12}")
    ausfall = brutto * b["mietausfallwagnis_pct"] / 100
    for label, verw_je in [("brutto, ohne jeden Abzug (Vault)", None),
                           (f"./. Mietausfallwagnis {b['mietausfallwagnis_pct']:.0f} %", 0),
                           (f"./. zusätzlich Verwaltung {b['verwaltung_eur_we_monat']} EUR/Einheit", b["verwaltung_eur_we_monat"])]:
        netto = brutto if verw_je is None else brutto - ausfall - anzahl * verw_je * 12
        print(f"     {label:<38} {eur(netto):>11} {eur(netto * fak * quote):>12}")
    print()
    print(f"     Mehrschuld in jedem Fall: 0 EUR. Das ist der Punkt — aber die Höhe")
    print(f"     der Kapazität ist zu klären, nicht die Größenordnung.")

    paket, netto = heizungspaket(a)
    umlage = a["modernisierungsfinanzierung"]["modernisierungsumlage_haus_b_jahr"]
    kap = umlage * fak * quote
    print(f"\n  b) Heizungspaket — Planwert aus dem Vault, alle sechs Positionen")
    print(f"     inkl. Fußbodenheizung Altbestand (Heizung-und-Energetische-Sanierung)")
    print(f"     Kosten brutto:                   {eur(paket):>10}")
    print(f"     ./. {PARAMETER['beg_grundfoerderung_pct']} % Grundförderung:        {eur(netto):>10}  = Mehrschuld")
    print(f"     Modernisierungsumlage:           {eur(umlage):>10} p.a.")
    print(f"     Wertzuwachs bei Faktor {fak}:        {eur(umlage * fak):>10}")
    print(f"     davon {quote * 100:.0f} % Beleihungskapazität:  {eur(kap):>10}")
    print(f"     -> Differenz {eur(kap - netto)}. Die Maßnahme VERBRAUCHT Spielraum.")

    print(f"\n  Und die härtere Zahl: was kostet das Paket laufend?")
    mf = a["modernisierungsfinanzierung"]
    ann = modell.annuitaet_pct(mf["zins_pct"], mf["laufzeit_jahre"])
    kd = netto * ann / 100
    print(f"     Modernisierungsdarlehen {mf['zins_pct']} % / {mf['laufzeit_jahre']} J -> Annuität {ann:.3f} %")
    print(f"     Kapitaldienst auf {eur(netto)}:     {eur(kd):>10} p.a.")
    print(f"     ./. Umlage                       {eur(umlage):>10} p.a.")
    print(f"     = Cashflow-Belastung             {eur(kd - umlage):>10} p.a.")
    print(f"     bei einem Gesamtcashflow von     {eur(r['cashflow']):>10} p.a.")
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
    for vd in (0, 20_000, 50_000):
        ek = r["ek_benoetigt"] - vd
        rest = f["eigenkapital"] - ek
        zins = vd * PARAMETER["vd_zins_pct"] / 100
        print(f"  {eur(vd):>9} {eur(ek):>13} {eur(rest):>15} "
              f"{eur(zins):>10} {eur(r['cashflow'] - zins):>16}")
    print(f"\n  Über {eur(r['ek_benoetigt'])} hinaus bringt ein Verkäuferdarlehen nichts mehr —")
    print(f"  mehr Eigenkapital als nötig ersetzt es nicht.")
    print(f"\n  VD-Zins {PARAMETER['vd_zins_pct']} %, TILGUNGSFREI unterstellt (Annahme): die Spalte")
    print(f"  Restliquidität ist damit gestreckt, nicht geschenkt. Die Regel aus")
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
    nk_q = nebenkosten_quote(a)
    ek_q = nk_q - f["beleihungsauslauf_max_pct"] / 100
    print(f"\n  Jeder Euro hebt den tragbaren Preis um {1 / ek_q:.2f} EUR: aus Eigenkapital")
    print(f"  kommen Kaufpreis plus {(nk_q - 1) * 100:.1f} % Nebenkosten minus "
          f"{f['beleihungsauslauf_max_pct']} % Beleihung")
    print(f"  = {ek_q * 100:.1f} % des Kaufpreises.")
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

    tk_schwelle = tk / (kp * quote) * 100
    print(f"\n  Inkrementell gerechnet: der Aufschlag muss {tk_schwelle:.2f} % erreichen,")
    print(f"  damit allein die Teilungskosten wieder hereinkommen. Die Spalte")
    print(f"  './. Restschuld' zählt die ohnehin erfolgte Tilgung mit und sieht")
    print(f"  deshalb günstiger aus, als die Maßnahme ist.")
    b = a["bewirtschaftung"]
    nb = a["ausbau"]["nebengebaeude"]
    brutto = sum(n * m * 12 for _, n, m in nb)
    netto = brutto - brutto * b["mietausfallwagnis_pct"] / 100
    neben = netto * PARAMETER["wert_faktor"] * quote
    print(f"\n  Zum Vergleich: die Nebengebäude bringen rund {eur(neben)} Beleihungs-")
    print(f"  kapazität für 0 EUR und ohne Steuerrisiko — allerdings erst ab dem")
    print(f"  Auszug der Verkäufer, nicht ab Übergabe (Fragen-an-den-Verkaeufer,")
    print(f"  abgehakt 2026-09-10). Dieselbe Wirkung erreicht die Teilung erst bei")
    print(f"  rund {(neben + tk) / (kp * quote) * 100:.1f} % Aufteilungsaufschlag.")
    print(f"\n  Steuerlich: das Objekt hat {we} Einheiten (Zielzustand 9). Jede WEG-Einheit")
    print("  ist ein eigenes Objekt i.S.d. Drei-Objekt-Grenze (BMF 26.03.2004,")
    print("  BFH GrS 1/98). Aus einem Objekt würden sieben bis neun — bei einer")
    print("  Umqualifizierung entfallen AfA und § 23 EStG, dazu Gewerbesteuer.")
    print("  Das kollidiert mit der Entscheidung 'Erwerb privat'.")


def foerderung(a):
    kopf("4  FÖRDERUNG — Projektstand gegen BEG-EM ab 21.07.2026")
    P = PARAMETER
    def grenze(we, erste):
        return (erste + min(max(we - 1, 0), 5) * P["beg_hoechst_we_2_6"]
                + max(we - 6, 0) * P["beg_hoechst_ab_we_7"])
    we = a["objekt"]["einheiten"]
    alt, neu = P["beg_hoechst_erste_we_alt"], P["beg_hoechst_erste_we"]
    paket, _ = heizungspaket(a)
    fo = a["foerderung"]
    satz = P["beg_grundfoerderung_pct"] / 100

    print(f"  Planpaket: {eur(paket)}\n")
    print(f"  {'Konstellation':<30} {'Deckel alt':>12} {'neu':>11} "
          f"{'Zuschuss alt':>14} {'neu':>11}")
    for label, kombi in [(f"Ein Wohngebäude, {we} WE", [we]), ("Zwei Wohngebäude (6 + 1 WE)", [6, 1])]:
        d_alt = sum(grenze(x, alt) for x in kombi)
        d_neu = sum(grenze(x, neu) for x in kombi)
        z_alt = min(paket, d_alt) * satz
        z_neu = min(paket, d_neu) * satz
        print(f"  {label:<30} {eur(d_alt):>12} {eur(d_neu):>11} "
              f"{eur(z_alt):>14} {eur(z_neu):>11}")
    print(f"\n  -> Das Planpaket liegt unter JEDEM dieser Deckel. Die Absenkung der")
    print(f"     Höchstgrenze kostet damit 0 EUR, solange der Umfang nicht wächst.")
    print(f"     Erst ab {eur(grenze(we, neu))} Maßnahmenumfang wird sie spürbar.")
    print(f"\n  annahmen.json führt hoechstgrenze_ein_gebaeude: "
          f"{eur(fo['hoechstgrenze_ein_gebaeude'])} — zu korrigieren auf {eur(grenze(we, neu))}.")

    neu_satz = P["beg_grundfoerderung_pct"]
    alt_satz = neu_satz + P["beg_effizienzbonus_alt_pct"]
    ist = fo["grundfoerderung_pct"] + fo["effizienzbonus_pct"]
    print(f"\n  Die einzige Änderung mit echter Euro-Wirkung ist der Effizienzbonus:")
    print(f"    Projektstand vor dem 21.07.2026, {alt_satz} % (30 + "
          f"{P['beg_effizienzbonus_alt_pct']}): {eur(paket * alt_satz / 100)} Zuschuss")
    print(f"    ab 21.07.2026, {neu_satz} % (Bonus entfallen):      "
          f"{eur(paket * neu_satz / 100)} Zuschuss")
    print(f"    entgangene Chance: {eur(paket * (alt_satz - neu_satz) / 100)}")
    stand = "korrigiert" if ist == neu_satz else f"NOCH NICHT korrigiert ({ist} %)"
    print(f"    annahmen.json: {stand}")
    print(f"\n    ABER: Der Vault-Eigenanteil von {eur(paket * (1 - neu_satz / 100))} EUR ist bereits")
    print(f"    mit {neu_satz} % gerechnet. Der Wegfall ändert ihn NICHT — er nimmt nur")
    print(f"    den besseren Fall. Und der Bonus galt ohnehin nur 'bei passender")
    print(f"    Technik' (Heizung-und-Energetische-Sanierung), war also nie sicher.")
    print("\n  Der Höchstbetrag der ersten WE sinkt ab 01.02.2027 halbjährlich um")
    print("  750 EUR. Maßgeblich ist der ANTRAGSzeitpunkt, nicht die Umsetzung —")
    print("  und der Vault plant den Antrag ohnehin auf Mitte 2027, die Umsetzung")
    print("  auf Winter 2027/28. Die Absenkung erzeugt also KEINEN Druck auf den")
    print("  Auszugstermin. Wirkung beim Planpaket, das unter jedem Deckel liegt:")
    print(f"  0 EUR. Sie wird erst relevant, wenn der Umfang an den Deckel stößt.")


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
            print(f"    -> {'unter der Kappung' if u <= deckel else 'ÜBER der Kappung'}")
            # Der Vault leitet die Umlage aus § 559 (8 %) ab. Nach der eigenen
            # Rechtsanalyse ist bei Förderung § 559e (10 %) die speziellere Norm.
            pct = PARAMETER["umlage_559e_pct"]
            basis = u / 0.08
            roh = basis * pct / 100
            print(f"\n    Der Vault leitet die {eur(u)} aus § 559 (8 %) auf rund")
            print(f"    {eur(basis)} umlagefähige Kosten ab. Bei Förderung ist aber")
            print(f"    § 559e ({pct} %) die speziellere Norm:")
            print(f"      {pct} % auf {eur(basis)}      = {eur(roh)} p.a.")
            print(f"      Kappung                  = {eur(deckel)} p.a.")
            print(f"      -> maßgeblich {eur(min(roh, deckel))} p.a., also "
                  f"{eur(min(roh, deckel) - u)} mehr als angesetzt.")
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
