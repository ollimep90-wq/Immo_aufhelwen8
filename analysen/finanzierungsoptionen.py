#!/usr/bin/env python3
"""Rechenkern für drei Finanzierungsoptionen: Nachbeleihung, Verkäuferdarlehen,
WEG-Teilung.

    python3 analysen/finanzierungsoptionen.py --annahmen <Strategie>/annahmen.json

**Eingabewerte kommen aus `annahmen.json`** — das ist nach CLAUDE.md die einzige
zulässige Quelle. Ohne `--annahmen` läuft das Skript mit Platzhaltern und sagt
bei jedem einzelnen Wert, dass er ein Platzhalter ist. Ein Ergebnis aus
Platzhaltern gehört in keine Entscheidung.

Alles, was das Skript zusätzlich braucht und was **nicht** in annahmen.json
steht — Sicherheitsabschlag der Bank, Zinsstaffel nach Beleihungsauslauf,
Kapitalisierungszinssatz, Bewirtschaftungskosten, Teilungskosten — sind
Bankkonditionen und Bewertungsparameter. Sie stehen unten als `PARAMETER`,
sind als Annahme gekennzeichnet und gehören bei der Bank erfragt.

Standardbibliothek only. Keine Rechts-, Steuer- oder Anlageberatung.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Platzhalter. Greifen NUR, wenn annahmen.json den Wert nicht hergibt.
# Die belegten stammen aus CLAUDE.md ("Stand der Entscheidungen").
# ---------------------------------------------------------------------------
PLATZHALTER = {
    "kaufpreis":      (740_000, "belegt: CLAUDE.md, Zielpreis"),
    "kaufpreis_max":  (800_000, "belegt: CLAUDE.md, Obergrenze"),
    "eigenkapital":   (120_000, "belegt: CLAUDE.md"),
    "grest_pct":      (6.5,     "Referenz: kaufnebenkosten-de.md, NRW, Stand Mai 2026 — prüfen"),
    "notar_pct":      (1.5,     "Referenz: Planungsgröße Skill"),
    "grundbuch_pct":  (0.5,     "Referenz: Planungsgröße Skill"),
    "makler_pct":     (0.0,     "PLATZHALTER: Direktkauf ohne Makler unterstellt"),
    "zins_pct":       (3.8,     "PLATZHALTER: Sollzins — bei der Bank erfragen"),
    "tilgung_pct":    (2.0,     "PLATZHALTER: Anfangstilgung"),
    "zinsbindung_j":  (10,      "PLATZHALTER: Zinsbindung in Jahren"),
    "kaltmiete_monat":(None,    "PLATZHALTER: unbekannt — ohne diesen Wert keine Ertragswertaussage"),
}

# Schlüssel, unter denen ein Wert in annahmen.json stehen könnte.
ALIASE = {
    "kaufpreis":       ["kaufpreis", "kaufpreis_ziel", "zielpreis", "price", "kp"],
    "kaufpreis_max":   ["kaufpreis_max", "obergrenze", "preisobergrenze", "max_preis"],
    "eigenkapital":    ["eigenkapital", "ek", "equity", "equity_total"],
    "grest_pct":       ["grunderwerbsteuer_pct", "grest_pct", "grest", "grunderwerbsteuer"],
    "notar_pct":       ["notar_pct", "notar"],
    "grundbuch_pct":   ["grundbuch_pct", "grundbuch"],
    "makler_pct":      ["makler_pct", "maklerprovision", "commission"],
    "zins_pct":        ["zins_pct", "sollzins", "zins", "rate", "zinssatz"],
    "tilgung_pct":     ["tilgung_pct", "tilgung", "repayment"],
    "zinsbindung_j":   ["zinsbindung_jahre", "zinsbindung", "fixed_years"],
    "kaltmiete_monat": ["kaltmiete_monat", "nettokaltmiete", "miete_monat", "rent"],
}

# --------------------------------------------------------------- PARAMETER
# Bankkonditionen und Bewertungsparameter. ALLE Annahme — bei der Bank bzw.
# im Gutachten verifizieren. Sie gehören bewusst NICHT in annahmen.json,
# solange sie nicht von der Bank bestätigt sind.
PARAMETER = {
    "sicherheitsabschlag_pct": 10.0,   # Beleihungswert ggü. Kaufpreis
    "kapitalisierung_pct":      5.0,   # Ertragswertverfahren
    "restnutzungsdauer_j":       40,
    "bewirtschaftungskosten_pct": 22.0,
    "teilungskosten":        15_000,   # Abgeschlossenheit + Plan + Notar + Grundbuch
    "vd_zins_pct":              4.0,   # Verkäuferdarlehen
    # Zinsstaffel: (Beleihungsauslauf bis %, Sollzins %)
    "zinsstaffel": [(60, 3.50), (80, 3.65), (90, 3.95), (95, 4.35),
                    (100, 4.80), (105, 5.20)],
}


# ------------------------------------------------------------------ Laden
def lade(pfad: str | None) -> tuple[dict, dict]:
    """Werte + Herkunft je Wert. Herkunft ist Teil des Ergebnisses, nicht Deko."""
    roh: dict = {}
    if pfad:
        p = Path(pfad)
        if not p.is_file():
            sys.exit(f"annahmen.json nicht gefunden: {p}")
        roh = json.loads(p.read_text(encoding="utf-8"))
        flach: dict = {}

        def platt(d, prefix=""):
            for k, v in d.items():
                if isinstance(v, dict):
                    platt(v, prefix)
                else:
                    flach.setdefault(str(k).lower(), v)
        platt(roh)
        roh = flach

    werte, herkunft = {}, {}
    for feld, aliase in ALIASE.items():
        treffer = next((roh[a] for a in aliase if a in roh
                        and isinstance(roh[a], (int, float))), None)
        if treffer is not None:
            werte[feld] = treffer
            herkunft[feld] = f"annahmen.json ({pfad})"
        else:
            wert, note = PLATZHALTER[feld]
            werte[feld] = wert
            herkunft[feld] = note
    return werte, herkunft


# ------------------------------------------------------------------ Mathe
def eur(x) -> str:
    return "—" if x is None else f"{x:,.0f}".replace(",", ".")


def nebenkosten(w) -> float:
    return w["kaufpreis"] * (w["grest_pct"] + w["notar_pct"]
                             + w["grundbuch_pct"] + w["makler_pct"]) / 100


def annuitaet(darlehen, zins, tilgung) -> float:
    return darlehen * (zins + tilgung) / 100


def restschuld(darlehen, jahre, zins, tilgung) -> float:
    """Restschuld nach `jahre` bei monatlicher Zahlung und Anfangstilgung."""
    r = zins / 100 / 12
    rate = annuitaet(darlehen, zins, tilgung) / 12
    n = jahre * 12
    q = (1 + r) ** n
    return darlehen * q - rate * (q - 1) / r


def vervielfaeltiger(p_pct, jahre) -> float:
    p = p_pct / 100
    return (1 - (1 + p) ** (-jahre)) / p


def zins_fuer_auslauf(auslauf_pct) -> float:
    for grenze, zins in PARAMETER["zinsstaffel"]:
        if auslauf_pct <= grenze:
            return zins
    return PARAMETER["zinsstaffel"][-1][1]


def kopf(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


# ----------------------------------------------------------------- Blöcke
def basis(w):
    kopf("0  AUSGANGSLAGE")
    nk = nebenkosten(w)
    gesamt = w["kaufpreis"] + nk
    darlehen = gesamt - w["eigenkapital"]
    bw = w["kaufpreis"] * (1 - PARAMETER["sicherheitsabschlag_pct"] / 100)
    print(f"  Kaufpreis                          {eur(w['kaufpreis']):>12}")
    print(f"  Nebenkosten                        {eur(nk):>12}   <- nicht beleihbar")
    print(f"  Gesamtinvestition                  {eur(gesamt):>12}")
    print(f"  ./. Eigenkapital                   {eur(w['eigenkapital']):>12}")
    print(f"  = Darlehensbedarf                  {eur(darlehen):>12}")
    print()
    print(f"  davon deckt Eigenkapital die Nebenkosten:  {eur(min(w['eigenkapital'], nk)):>12}")
    print(f"  echte Anzahlung auf den Kaufpreis:         "
          f"{eur(max(0, w['eigenkapital'] - nk)):>12}")
    print()
    print(f"  Beleihungswert (KP ./. {PARAMETER['sicherheitsabschlag_pct']:.0f} %)       {eur(bw):>12}")
    print(f"  Beleihungsauslauf auf Kaufpreis            {darlehen / w['kaufpreis'] * 100:>11.1f} %")
    print(f"  Beleihungsauslauf auf Beleihungswert       {darlehen / bw * 100:>11.1f} %")
    a = annuitaet(darlehen, w["zins_pct"], w["tilgung_pct"])
    print(f"  Annuität {w['zins_pct']}+{w['tilgung_pct']} %                    "
          f"{eur(a):>12} p.a. = {eur(a / 12)} /Monat")
    print(f"  Restschuld nach {w['zinsbindung_j']} Jahren             "
          f"{eur(restschuld(darlehen, w['zinsbindung_j'], w['zins_pct'], w['tilgung_pct'])):>12}")
    return darlehen, bw


def option1(w, darlehen, bw):
    kopf("1  NACHBELEIHUNG — wann entsteht überhaupt Spielraum?")
    ziel = 90
    print(f"  Zielauslauf {ziel} % des Beleihungswerts.\n")
    print(f"  {'Jahr':>5} {'Restschuld':>13} " + "".join(
        f"{'BW +' + str(z) + '%':>14}" for z in (0, 10, 20)))
    for j in (3, 5, 7, 10):
        rs = restschuld(darlehen, j, w["zins_pct"], w["tilgung_pct"])
        zeile = f"  {j:>5} {eur(rs):>13}"
        for z in (0, 10, 20):
            zeile += f"{eur(bw * (1 + z / 100) * ziel / 100 - rs):>14}"
        print(zeile)
    print("  (Spielraum in EUR; negativ = keiner)")

    monate = next((m for m in range(1, 481)
                   if restschuld(darlehen, m / 12, w["zins_pct"], w["tilgung_pct"])
                   <= bw * ziel / 100), None)
    if monate:
        print(f"\n  Ohne Wertzuwachs faellt die Restschuld nach {monate} Monaten "
              f"(= {monate / 12:.1f} Jahre) auf {ziel} %")
        print(f"  des Beleihungswerts ({eur(bw * ziel / 100)}). Vorher gibt es nichts nachzubeleihen.")
    else:
        print(f"\n  Ohne Wertzuwachs wird {ziel} % des Beleihungswerts binnen 40 Jahren nicht erreicht.")

    print(f"\n  Der Test, auf den es ankommt: eine finanzierte Maßnahme verbessert den")
    print(f"  Auslauf nur, wenn sie den Beleihungswert um mehr hebt als die Schuld.\n")
    v = vervielfaeltiger(PARAMETER["kapitalisierung_pct"], PARAMETER["restnutzungsdauer_j"])
    bwk = PARAMETER["bewirtschaftungskosten_pct"] / 100
    print(f"  Vervielfältiger {v:.2f} bei {PARAMETER['kapitalisierung_pct']} % / "
          f"{PARAMETER['restnutzungsdauer_j']} J, Bewirtschaftungskosten "
          f"{PARAMETER['bewirtschaftungskosten_pct']:.0f} %\n")
    print(f"  {'Maßnahme':>10} {'Zuschuss':>9} {'d Schuld':>11} {'nötige Mehrmiete/Monat':>24}")
    for kosten in (30_000, 60_000, 100_000, 150_000):
        for quote in (0.0, 0.5):
            d_schuld = kosten * (1 - quote)
            miete = (d_schuld / v) / (1 - bwk) / 12
            print(f"  {eur(kosten):>10} {quote * 100:>7.0f} % {eur(d_schuld):>11} {eur(miete):>22} EUR")


def option2(w, bw):
    kopf("2  VERKÄUFERDARLEHEN — der Vergleich ist der Grenzzins, nicht der Mischzins")
    nk = nebenkosten(w)
    gesamt = w["kaufpreis"] + nk
    voll = gesamt - w["eigenkapital"]
    basis_z = zins_fuer_auslauf(voll / bw * 100)
    print(f"  ohne VD: Auslauf {voll / bw * 100:.1f} % -> Zins {basis_z:.2f} % auf {eur(voll)}"
          f" = {eur(voll * basis_z / 100)} EUR Zins p.a.\n")
    print(f"  {'VD':>9} {'Bankdarlehen':>13} {'Auslauf':>9} {'Zins':>7} "
          f"{'Zins ges. p.a.':>15} {'Differenz':>11} {'break-even':>11}")
    for vd in (50_000, 100_000, 150_000):
        bank = gesamt - w["eigenkapital"] - vd
        a = bank / bw * 100
        z = zins_fuer_auslauf(a)
        ges_zins = bank * z / 100 + vd * PARAMETER["vd_zins_pct"] / 100
        alt = voll * basis_z / 100
        be = (alt - bank * z / 100) / vd * 100
        print(f"  {eur(vd):>9} {eur(bank):>13} {a:>8.1f} % {z:>6.2f} % "
              f"{eur(ges_zins):>15} {ges_zins - alt:>+11,.0f} {be:>10.2f} %".replace(",", "."))
    print(f"\n  VD-Zins in der Rechnung: {PARAMETER['vd_zins_pct']} % (Annahme).")
    print("  break-even = VD-Zins, bis zu dem sich das VD rein zinsseitig noch lohnt.")

    print("\n  Gegenprobe über 10 Jahre — ein endfälliges VD stundet Tilgung, es spart sie nicht:\n")
    print(f"  {'Variante':<40} {'Zahlung 10 J':>14} {'Restschuld':>13} {'Summe':>13}")
    z_, t_, j_ = w["zins_pct"], w["tilgung_pct"], 10
    zahl = annuitaet(voll, z_, t_) * j_
    rs = restschuld(voll, j_, z_, t_)
    print(f"  {'ohne VD':<40} {eur(zahl):>14} {eur(rs):>13} {eur(zahl + rs):>13}")
    for vd in (50_000, 100_000, 150_000):
        bank = gesamt - w["eigenkapital"] - vd
        vz = PARAMETER["vd_zins_pct"]
        ze = (annuitaet(bank, z_, t_) + vd * vz / 100) * j_
        re = restschuld(bank, j_, z_, t_) + vd
        print(f"  {'VD ' + eur(vd) + ', endfällig':<40} {eur(ze):>14} {eur(re):>13} {eur(ze + re):>13}")
        zt = (annuitaet(bank, z_, t_) + annuitaet(vd, vz, 2.0)) * j_
        rt = restschuld(bank, j_, z_, t_) + restschuld(vd, j_, vz, 2.0)
        print(f"  {'VD ' + eur(vd) + ', mit 2 % Tilgung':<40} {eur(zt):>14} {eur(rt):>13} {eur(zt + rt):>13}")
    print("\n  (hier ohne Zinsstaffel, um den reinen Stundungseffekt zu isolieren)")


def preisaufschlag(w, bw):
    """Stephan bietet ein VD und will dafuer Preis. Was kostet das wirklich?"""
    kopf("2b PREISAUFSCHLAG GEGEN VERKAEUFERDARLEHEN")
    vd = 100_000
    z_, t_ = w["zins_pct"], w["tilgung_pct"]
    basis_nk = nebenkosten(w)
    basis_dar = w["kaufpreis"] + basis_nk - w["eigenkapital"]
    basis_kd = annuitaet(basis_dar, z_, t_)
    print(f"  Referenz: Kaufpreis {eur(w['kaufpreis'])} ohne VD -> Darlehen {eur(basis_dar)},")
    print(f"  Kapitaldienst {eur(basis_kd)} p.a.   VD in der Rechnung: {eur(vd)}, endfaellig.\n")
    print(f"  {'Aufschlag':>10} {'Kaufpreis':>11} {'Mehr-NK einmalig':>18} "
          f"{'Kapitaldienst p.a.':>20} {'Differenz':>11}")
    nk_pct = (w["grest_pct"] + w["notar_pct"] + w["grundbuch_pct"] + w["makler_pct"]) / 100
    for auf in (20_000, 40_000, 60_000):
        kp2 = w["kaufpreis"] + auf
        ges2 = kp2 * (1 + nk_pct)
        bank2 = ges2 - w["eigenkapital"] - vd
        kd2 = annuitaet(bank2, z_, t_) + vd * PARAMETER["vd_zins_pct"] / 100
        mehr_nk = auf * nk_pct
        print(f"  {'+' + eur(auf):>10} {eur(kp2):>11} {eur(mehr_nk):>18} "
              f"{eur(kd2):>20} {kd2 - basis_kd:>+11,.0f}".replace(",", "."))
    print("\n  Der Kapitaldienst taeuscht: der hoehere Preis erhoeht dauerhaft die")
    print("  Grunderwerbsteuer-Bemessungsgrundlage, die Restschuld und den Betrag,")
    print("  den ein spaeterer Verkauf erst wieder einspielen muss.")


def auslaufkosten(w, darlehen):
    """Was kostet ein hoher Auslauf an Zinsen -- auf demselben Darlehen?"""
    kopf("5  WAS EIN HOHER AUSLAUF KOSTET")
    print(f"  Dasselbe Darlehen {eur(darlehen)}, nur andere Zinsscheibe:\n")
    print(f"  {'Auslauf':>9} {'Zins':>8} {'Annuitaet p.a.':>16} {'Zinsanteil Jahr 1':>19}")
    for grenze, z in PARAMETER["zinsstaffel"]:
        a = annuitaet(darlehen, z, w["tilgung_pct"])
        print(f"  {grenze:>7} % {z:>7.2f} % {eur(a):>16} {eur(darlehen * z / 100):>19}")
    z80 = zins_fuer_auslauf(80)
    z95 = zins_fuer_auslauf(95)
    print(f"\n  Differenz Zinsanteil Jahr 1 zwischen {z80:.2f} % (80 %) und "
          f"{z95:.2f} % (95 %): {eur(darlehen * (z95 - z80) / 100)} EUR p.a.")
    print("  Mehr Volumen ist nicht gratis. 'Wieviel kann ich finanzieren' ist nicht")
    print("  dieselbe Frage wie 'wieviel sollte ich finanzieren'.")


def option3(w, bw):
    kopf("3  WEG-TEILUNG — Mehrvolumen gegen Teilungskosten")
    tk = PARAMETER["teilungskosten"]
    print(f"  Beleihungswert als Ganzes {eur(bw)}, Teilungskosten {eur(tk)} (Annahme)\n")
    print(f"  {'Aufschlag':>10} {'BW in Summe':>14} {'95 % davon':>13} "
          f"{'Mehrvolumen':>13} {'nach Kosten':>13}")
    for auf in (0, 5, 10, 15, 20):
        neu = bw * (1 + auf / 100)
        mehr = (neu - bw) * 0.95
        print(f"  {auf:>8} % {eur(neu):>14} {eur(neu * 0.95):>13} "
              f"{eur(mehr):>13} {eur(mehr - tk):>13}")
    print("\n  Der Aufteilungsaufschlag ist eine MARKTgröße beim Einzelverkauf an")
    print("  Selbstnutzer. Ob die Bank ihn in den BELEIHUNGSwert übernimmt, während")
    print("  du alle Einheiten hältst und vermietest, ist eine andere Frage — und die")
    print("  entscheidet über diese Option. Vorab klären, nicht unterstellen.")


def bezugsgroesse(w):
    kopf("4  '95 % BELEIHUNGSAUSLAUF' — worauf bezogen?")
    kp = w["kaufpreis"]
    for sa in (0, 10, 15):
        b = kp * (1 - sa / 100)
        print(f"  Sicherheitsabschlag {sa:>2} %  ->  BW {eur(b):>9}  ->  95 % = {eur(b * 0.95):>9}"
              f"  = {b * 0.95 / kp * 100:.1f} % des Kaufpreises")
    print("\n  Dieselbe Prozentzahl bedeutet je nach Bezugsgröße gut 100.000 EUR")
    print("  Unterschied. Vor jedem Bankgespräch klären, worauf sich ihre Zahl bezieht.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--annahmen", help="Pfad zu annahmen.json (die einzige zulässige Quelle)")
    args = ap.parse_args()

    w, herkunft = lade(args.annahmen)

    kopf("EINGABEWERTE UND IHRE HERKUNFT")
    ohne_quelle = 0
    for feld in ALIASE:
        q = herkunft[feld]
        if q.startswith("PLATZHALTER"):
            ohne_quelle += 1
        v = w[feld]
        if v is None:
            gezeigt = "—"
        elif feld.endswith("_pct"):
            gezeigt = f"{v:g} %"          # Prozente NIE als Euro runden
        elif feld.endswith("_j"):
            gezeigt = f"{v:g} J"
        else:
            gezeigt = eur(v)
        print(f"  {feld:<18} {gezeigt:>10}   {q}")
    if not args.annahmen:
        print("\n  !! Ohne --annahmen läuft alles auf Platzhaltern. Kein Ergebnis aus")
        print("     diesem Lauf gehört in eine Entscheidung.")
    elif ohne_quelle:
        print(f"\n  !! {ohne_quelle} Wert(e) standen nicht in annahmen.json und laufen auf")
        print("     Platzhaltern. Vor Verwendung dort ergänzen.")

    print("\n  PARAMETER (durchweg Annahme — bei Bank/Gutachter verifizieren):")
    for k, v in PARAMETER.items():
        print(f"    {k:<28} {v}")

    darlehen, bw = basis(w)
    bezugsgroesse(w)
    option1(w, darlehen, bw)
    option2(w, bw)
    preisaufschlag(w, bw)
    option3(w, bw)
    auslaufkosten(w, darlehen)
    print("\n" + "=" * 74)
    print("Keine Rechts-, Steuer- oder Anlageberatung. Bankkonditionen sind Annahmen.")
    print("=" * 74)


if __name__ == "__main__":
    main()
