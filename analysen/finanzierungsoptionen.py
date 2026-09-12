#!/usr/bin/env python3
"""Rechenkern für drei Finanzierungsoptionen: Nachbeleihung, Verkäuferdarlehen,
WEG-Teilung.

    python3 analysen/finanzierungsoptionen.py --annahmen <Strategie>/annahmen.json

**Eingabewerte kommen aus `annahmen.json`** — das ist nach CLAUDE.md die einzige
zulässige Quelle. Ohne `--annahmen` läuft das Skript mit den in CLAUDE.md und
.claude/agents/widerspruchs-pruefer.md belegten Werten plus Platzhaltern und
sagt bei jedem einzelnen Wert, welcher Klasse er angehört.

Bankkonditionen und Bewertungsparameter stehen unten als `PARAMETER`. Sie
gehören bewusst NICHT in annahmen.json, solange die Bank sie nicht bestätigt
hat — sind aber damit ein zweiter Ort, an dem eine Zahl veralten kann. Nach
der Bankauskunft nach annahmen.json überführen.

Standardbibliothek only. Keine Rechts-, Steuer- oder Anlageberatung.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Eingabewerte. Greifen NUR, wenn annahmen.json den Wert nicht hergibt.
# Klasse: "belegt" | "referenz" | "platzhalter"
# ---------------------------------------------------------------------------
VORGABEN: dict[str, tuple] = {
    "kaufpreis":       (740_000, "belegt",      "CLAUDE.md, Zielpreis"),
    "kaufpreis_max":   (800_000, "belegt",      "CLAUDE.md, Obergrenze"),
    "eigenkapital":    (120_000, "belegt",      "CLAUDE.md"),
    "makler_pct":      (0.0,     "belegt",      "Privatverkauf ohne Makler (Nutzerfakt)"),
    "zins_pct":        (5.45,    "belegt",      "reales Angebot Wüstenrot (Nutzerfakt)"),
    "volltilger_j":    (34,      "belegt",      "reales Angebot Wüstenrot (Nutzerfakt)"),
    "grest_pct":       (6.5,     "referenz",    "kaufnebenkosten-de.md, NRW — Satz prüfen"),
    "notar_pct":       (1.5,     "referenz",    "Planungsgröße Skill"),
    "grundbuch_pct":   (0.5,     "referenz",    "Planungsgröße Skill"),
    "grundschuld_pct": (0.25,    "referenz",    "kaufnebenkosten-de.md: 0,2-0,3 % der Grundschuld"),
    "kaltmiete_monat": (None,    "platzhalter", "FEHLT — ohne sie keine Ertragswertaussage"),
}

ALIASE = {
    "kaufpreis":       ["kaufpreis", "kaufpreis_ziel", "zielpreis"],
    "kaufpreis_max":   ["kaufpreis_max", "obergrenze", "preisobergrenze"],
    "eigenkapital":    ["eigenkapital", "equity_total"],
    "makler_pct":      ["makler_pct", "maklerprovision"],
    "zins_pct":        ["finanzierung.zins_pct", "finanzierung.sollzins", "sollzins_pct"],
    "volltilger_j":    ["finanzierung.volltilger_jahre", "volltilger_jahre", "laufzeit_jahre"],
    "grest_pct":       ["grunderwerbsteuer_pct", "grest_pct"],
    "notar_pct":       ["notar_pct"],
    "grundbuch_pct":   ["grundbuch_pct"],
    "grundschuld_pct": ["grundschuld_pct"],
    "kaltmiete_monat": ["nettokaltmiete_monat", "kaltmiete_monat", "objekt.nettokaltmiete"],
}

# --------------------------------------------------------------- PARAMETER
PARAMETER = {
    # BelWertV § 12 Abs. 4: Wohnnutzung mind. 3,5 %, höchstens 5,5 %.
    # Aktuell angewandt 5,5 % (Korridor-Obergrenze), unverändert für 2026.
    "kapitalisierung_pct":        5.5,
    "restnutzungsdauer_j":         40,    # ANNAHME — Gutachten
    # BelWertV § 11 Abs. 2: Verwaltung + Instandhaltung + Mietausfall
    # zusammen mind. 15 % des Rohertrags. 20 % ist eine ANNAHME darüber.
    "bewirtschaftungskosten_pct": 20.0,
    "sicherheitsabschlag_pct":    10.0,   # ANNAHME — Bank
    "teilungskosten":          15_000,    # ANNAHME — Architekt/Notar
    "vd_zins_pct":                 4.0,   # ANNAHME — Verhandlung
    "zielauslauf_pct":            90.0,   # ANNAHME — was die Bank akzeptiert
    # Zinsstaffel: (Auslauf bis %, Sollzins %). Verankert am realen Angebot
    # 5,45 %, das beim heutigen Auslauf (~103 %) gilt. Die Scheiben darunter
    # sind ANNAHME — genau das ist bei der Bank als Staffel zu erfragen.
    "zinsstaffel": [(60, 3.95), (80, 4.15), (90, 4.55), (95, 4.95),
                    (100, 5.25), (110, 5.45)],
    # BelWertV § 24: Kleindarlehensgrenze, darunter vereinfachte Wertermittlung.
    "kleindarlehensgrenze":   600_000,
}


# ------------------------------------------------------------------ Laden
def lade(pfad: str | None) -> tuple[dict, dict, dict]:
    """Werte, Klasse und Herkunft je Feld. Die Herkunft ist Teil des Ergebnisses."""
    flach: dict = {}
    if pfad:
        p = Path(pfad)
        if not p.is_file():
            sys.exit(f"annahmen.json nicht gefunden: {p}")
        roh = json.loads(p.read_text(encoding="utf-8"))

        def platt(d, prefix=""):
            for k, v in d.items():
                pfad_k = f"{prefix}.{k}" if prefix else str(k)
                if isinstance(v, dict):
                    platt(v, pfad_k)
                else:
                    # bool ist in Python int — als Zahl wäre True == 1.
                    if isinstance(v, bool) or not isinstance(v, (int, float)):
                        continue
                    flach[pfad_k.lower()] = v
        platt(roh)

    werte, klasse, herkunft = {}, {}, {}
    for feld, aliase in ALIASE.items():
        treffer = {a: flach[a.lower()] for a in aliase if a.lower() in flach}
        # Ein unqualifizierter Alias darf auch als Blattname irgendwo tiefer
        # stehen — aber nur, wenn er dort EINDEUTIG ist.
        for a in aliase:
            if "." in a:
                continue
            tief = {k: v for k, v in flach.items() if k.split(".")[-1] == a.lower()}
            if len(tief) == 1:
                treffer.setdefault(a, next(iter(tief.values())))
            elif len(tief) > 1 and a not in treffer:
                sys.exit(f"annahmen.json: '{a}' steht mehrfach ({', '.join(sorted(tief))}). "
                         f"Bitte den Alias in ALIASE voll qualifizieren — "
                         f"sonst entscheidet der Zufall, welcher Zins gerechnet wird.")
        eindeutig = set(treffer.values())
        if len(eindeutig) > 1:
            sys.exit(f"annahmen.json: widersprüchliche Werte für '{feld}': {treffer}")
        if eindeutig:
            werte[feld] = next(iter(eindeutig))
            klasse[feld] = "belegt"
            herkunft[feld] = f"annahmen.json ({pfad})"
        else:
            wert, kl, note = VORGABEN[feld]
            werte[feld], klasse[feld], herkunft[feld] = wert, kl, note
    return werte, klasse, herkunft


# ------------------------------------------------------------------ Mathe
def eur(x) -> str:
    return "—" if x is None else f"{x:,.0f}".replace(",", ".")


def nebenkosten_pct(w) -> float:
    return w["grest_pct"] + w["notar_pct"] + w["grundbuch_pct"] + w["makler_pct"]


def rate_volltilger(darlehen, zins, jahre) -> float:
    """Monatsrate, die das Darlehen in `jahre` vollständig tilgt."""
    r = zins / 100 / 12
    n = jahre * 12
    return darlehen * r / (1 - (1 + r) ** -n)


def restschuld(darlehen, nach_jahren, zins, jahre) -> float:
    r = zins / 100 / 12
    rate = rate_volltilger(darlehen, zins, jahre)
    m = nach_jahren * 12
    q = (1 + r) ** m
    return darlehen * q - rate * (q - 1) / r


def vervielfaeltiger(p_pct, jahre) -> float:
    p = p_pct / 100
    return (1 - (1 + p) ** (-jahre)) / p


def zins_fuer_auslauf(auslauf_pct) -> float:
    for grenze, zins in PARAMETER["zinsstaffel"]:
        if auslauf_pct <= grenze:
            return zins
    return PARAMETER["zinsstaffel"][-1][1]


def miete_fuer_wertzuwachs(delta_bw) -> float:
    """Monatliche Kaltmiete, deren Kapitalisierung den Beleihungswert um
    delta_bw hebt. Der Sicherheitsabschlag wird auf die Maßnahme genauso
    angewandt wie auf den Bestand."""
    v = vervielfaeltiger(PARAMETER["kapitalisierung_pct"], PARAMETER["restnutzungsdauer_j"])
    bwk = PARAMETER["bewirtschaftungskosten_pct"] / 100
    delta_ertragswert = delta_bw / (1 - PARAMETER["sicherheitsabschlag_pct"] / 100)
    return (delta_ertragswert / v) / (1 - bwk) / 12


def kopf(t):
    print("\n" + "=" * 76)
    print(t)
    print("=" * 76)


# ----------------------------------------------------------------- Blöcke
def basis(w):
    kopf("0  AUSGANGSLAGE")
    kp = w["kaufpreis"]
    nk_kauf = kp * nebenkosten_pct(w) / 100
    zwischensumme = kp + nk_kauf
    # Grundschuldbestellung fällt auf die Grundschuld an, die etwa dem
    # Darlehen entspricht. Eine Runde Näherung genügt hier.
    darlehen_roh = zwischensumme - w["eigenkapital"]
    gs = darlehen_roh * w["grundschuld_pct"] / 100
    nk = nk_kauf + gs
    gesamt = kp + nk
    darlehen = gesamt - w["eigenkapital"]
    bw = kp * (1 - PARAMETER["sicherheitsabschlag_pct"] / 100)

    print(f"  Kaufpreis                                {eur(kp):>12}")
    print(f"  Kaufnebenkosten {nebenkosten_pct(w):.1f} %                  {eur(nk_kauf):>12}")
    print(f"  Grundschuldbestellung {w['grundschuld_pct']} %             {eur(gs):>12}")
    print(f"  = Nebenkosten gesamt                     {eur(nk):>12}   <- nicht beleihbar")
    print(f"  Gesamtinvestition                        {eur(gesamt):>12}")
    print(f"  ./. Eigenkapital                         {eur(w['eigenkapital']):>12}")
    print(f"  = Darlehensbedarf                        {eur(darlehen):>12}")
    print()
    print(f"  Eigenkapital deckt die Nebenkosten:      {eur(min(w['eigenkapital'], nk)):>12}")
    print(f"  echte Anzahlung auf den Kaufpreis:       {eur(max(0, w['eigenkapital'] - nk)):>12}")
    print()
    print(f"  Beleihungswert (KP ./. {PARAMETER['sicherheitsabschlag_pct']:.0f} %)             {eur(bw):>12}")
    print(f"  Beleihungsauslauf auf Kaufpreis                 {darlehen / kp * 100:>8.2f} %")
    print(f"  Beleihungsauslauf auf Beleihungswert            {darlehen / bw * 100:>8.2f} %")
    print()
    rate = rate_volltilger(darlehen, w["zins_pct"], w["volltilger_j"])
    tilg1 = (rate * 12 - darlehen * w["zins_pct"] / 100) / darlehen * 100
    print(f"  Volltilger {w['volltilger_j']} Jahre zu {w['zins_pct']} %")
    print(f"    Rate                                   {eur(rate):>12} /Monat")
    print(f"    Annuität                               {eur(rate * 12):>12} p.a.")
    print(f"    Zins Jahr 1                            {eur(darlehen * w['zins_pct'] / 100):>12}")
    print(f"    Anfangstilgung                              {tilg1:>8.2f} %")
    print()
    kdg = PARAMETER["kleindarlehensgrenze"]
    lage = "ÜBER" if darlehen > kdg else "unter"
    print(f"  BelWertV § 24 Kleindarlehensgrenze {eur(kdg)}: Darlehen liegt {lage} der Grenze")
    if darlehen > kdg:
        print(f"    -> Vollgutachten statt vereinfachter Wertermittlung. Kosten und")
        print(f"       Zeitbedarf gehören in die Kaufpreis- und Terminplanung.")
    return darlehen, bw, nk


def bezugsgroesse(w):
    kopf("1  '95 % BELEIHUNGSAUSLAUF' — worauf bezogen?")
    kp = w["kaufpreis"]
    for sa in (0, 10, 15):
        b = kp * (1 - sa / 100)
        print(f"  Sicherheitsabschlag {sa:>2} %  ->  BW {eur(b):>9}  ->  95 % = {eur(b * 0.95):>9}"
              f"  = {b * 0.95 / kp * 100:5.1f} % des Kaufpreises")
    print("\n  Über 100.000 EUR Unterschied, je nach Bezugsgröße. Vor jedem Bankgespräch")
    print("  klären. Zusatzfrage: BelWertV gilt rechtlich nur für Pfandbriefbanken —")
    print("  nach welchem Regelwerk bewertet diese Bank?")


def option1(w, darlehen, bw):
    kopf("2  NACHBELEIHUNG — wann entsteht überhaupt Spielraum?")
    ziel = PARAMETER["zielauslauf_pct"]
    z, j = w["zins_pct"], w["volltilger_j"]
    print(f"  Zielauslauf {ziel:.0f} % des Beleihungswerts, Volltilger {j} J zu {z} %.\n")
    print(f"  {'Jahr':>5} {'Restschuld':>13} " + "".join(
        f"{'BW +' + str(x) + '%':>14}" for x in (0, 10, 20)))
    for jahr in (3, 5, 7, 10, 15):
        rs = restschuld(darlehen, jahr, z, j)
        zeile = f"  {jahr:>5} {eur(rs):>13}"
        for x in (0, 10, 20):
            zeile += f"{eur(bw * (1 + x / 100) * ziel / 100 - rs):>14}"
        print(zeile)
    print("  (Spielraum in EUR; negativ = keiner)")

    m = next((m for m in range(1, j * 12 + 1)
              if restschuld(darlehen, m / 12, z, j) <= bw * ziel / 100), None)
    if m:
        print(f"\n  Ohne Wertzuwachs erreicht die Restschuld {ziel:.0f} % des Beleihungswerts")
        print(f"  ({eur(bw * ziel / 100)}) nach {m} Monaten = {m / 12:.1f} Jahren.")
    else:
        print(f"\n  Ohne Wertzuwachs wird {ziel:.0f} % des Beleihungswerts nie erreicht.")

    print("\n  Der Test, auf den es ankommt — zwei Kriterien, beide zeigen dasselbe:\n")
    v = vervielfaeltiger(PARAMETER["kapitalisierung_pct"], PARAMETER["restnutzungsdauer_j"])
    print(f"  Vervielfältiger {v:.2f} ({PARAMETER['kapitalisierung_pct']} % / "
          f"{PARAMETER['restnutzungsdauer_j']} J), Bewirtschaftungskosten "
          f"{PARAMETER['bewirtschaftungskosten_pct']:.0f} %,")
    print(f"  Sicherheitsabschlag {PARAMETER['sicherheitsabschlag_pct']:.0f} % auch auf die Maßnahme.\n")
    quote = darlehen / bw
    print(f"  {'Maßnahme':>10} {'Zuschuss':>9} {'d Schuld':>11} "
          f"{'Miete: Deckung':>16} {'Miete: Quote':>14}")
    for kosten in (30_000, 60_000, 100_000, 150_000):
        for q in (0.0, 0.3):
            d_schuld = kosten * (1 - q)
            # Kriterium 1 (streng): Beleihungswert muss um d Schuld steigen.
            m1 = miete_fuer_wertzuwachs(d_schuld)
            # Kriterium 2 (Quote bleibt gleich): d BW = d Schuld / Auslaufquote.
            m2 = miete_fuer_wertzuwachs(d_schuld / quote)
            print(f"  {eur(kosten):>10} {q * 100:>7.0f} % {eur(d_schuld):>11} "
                  f"{eur(m1):>14} EUR {eur(m2):>12} EUR")
    print("\n  'Deckung' = Beleihungswert steigt um die volle Mehrschuld.")
    print("  'Quote'   = Beleihungsauslauf bleibt unverändert (bei Auslauf über 100 %")
    print("              ist das die niedrigere Schwelle).")
    print("  Beides sind Schwellenrechnungen: so viel WÄRE nötig. Ob eine solche Miete")
    print("  erzielbar ist, sagt diese Rechnung nicht — dafür fehlt die Marktmiete.")


def option2(w, bw, nk):
    kopf("3  VERKÄUFERDARLEHEN — der Vergleich ist der Grenzzins, nicht der Mischzins")
    gesamt = w["kaufpreis"] + nk
    voll = gesamt - w["eigenkapital"]
    basis_z = zins_fuer_auslauf(voll / bw * 100)
    print(f"  ohne VD: Auslauf {voll / bw * 100:.2f} % -> Zins {basis_z:.2f} % auf {eur(voll)}")
    print(f"           = {eur(voll * basis_z / 100)} EUR Zins p.a.\n")

    print("  Die Scheibengrenzen und die Beträge, die sie genau erreichen:\n")
    print(f"  {'Grenze':>8} {'max. Darlehen':>15} {'nötiges VD':>13} {'Zins':>7} "
          f"{'Zins ges. p.a.':>16} {'Ersparnis':>12}")
    alt = voll * basis_z / 100
    for grenze, z in PARAMETER["zinsstaffel"]:
        max_dar = bw * grenze / 100
        vd = voll - max_dar
        if vd <= 0:
            continue
        ges = max_dar * z / 100 + vd * PARAMETER["vd_zins_pct"] / 100
        print(f"  {grenze:>6} % {eur(max_dar):>15} {eur(vd):>13} {z:>6.2f} % "
              f"{eur(ges):>16} {alt - ges:>+12,.0f}".replace(",", "."))
    print(f"\n  VD-Zins in der Rechnung: {PARAMETER['vd_zins_pct']} % (Annahme).")
    print("  Runde Beträge verfehlen die Grenze leicht — 200 EUR zu wenig VD kostet")
    print("  die ganze Scheibe. Deshalb hier die exakten Beträge statt runder Stufen.")

    print("\n  Gegenprobe: ein endfälliges VD stundet Tilgung, es spart sie nicht.")
    print("  (ohne Zinsstaffel, um den Stundungseffekt zu isolieren; nominal UND")
    print("   abgezinst, weil nominale Summen über 10 Jahre den Effekt überzeichnen)\n")
    z_, j_ = w["zins_pct"], w["volltilger_j"]
    n_j = 10
    def barwert(zahlung_p_a, jahre, rs, disk):
        d = disk / 100
        bw_zahlungen = sum(zahlung_p_a / (1 + d) ** t for t in range(1, jahre + 1))
        return bw_zahlungen + rs / (1 + d) ** jahre
    print(f"  {'Variante':<38} {'Zahlung 10 J':>14} {'Restschuld':>13} "
          f"{'Summe':>13} {'Barwert':>13}")
    zahl = rate_volltilger(voll, z_, j_) * 12 * n_j
    rs = restschuld(voll, n_j, z_, j_)
    print(f"  {'ohne VD':<38} {eur(zahl):>14} {eur(rs):>13} {eur(zahl + rs):>13} "
          f"{eur(barwert(zahl / n_j, n_j, rs, z_)):>13}")
    for vd in (50_000, 100_000, 150_000):
        bank = voll - vd
        vz = PARAMETER["vd_zins_pct"]
        ze = (rate_volltilger(bank, z_, j_) * 12 + vd * vz / 100) * n_j
        re = restschuld(bank, n_j, z_, j_) + vd
        print(f"  {'VD ' + eur(vd) + ', endfällig':<38} {eur(ze):>14} {eur(re):>13} "
              f"{eur(ze + re):>13} {eur(barwert(ze / n_j, n_j, re, z_)):>13}")


def preisaufschlag(w, nk):
    kopf("3b PREISAUFSCHLAG GEGEN VERKÄUFERDARLEHEN")
    vd = 100_000
    z_, j_ = w["zins_pct"], w["volltilger_j"]
    nk_q = nebenkosten_pct(w) / 100 + w["grundschuld_pct"] / 100
    gesamt = w["kaufpreis"] + nk
    # Richtige Vergleichsbasis: derselbe Kaufpreis, MIT demselben VD.
    ref_bank = gesamt - w["eigenkapital"] - vd
    ref_kd = rate_volltilger(ref_bank, z_, j_) * 12 + vd * PARAMETER["vd_zins_pct"] / 100
    print(f"  Vergleichsbasis: Kaufpreis {eur(w['kaufpreis'])} MIT VD {eur(vd)}")
    print(f"  -> Kapitaldienst {eur(ref_kd)} p.a.   Isoliert wird nur der Preiseffekt.\n")
    print(f"  {'Aufschlag':>10} {'Kaufpreis':>11} {'Mehr-NK':>10} "
          f"{'Kapitaldienst p.a.':>20} {'Differenz':>11}")
    for auf in (20_000, 40_000, 60_000):
        kp2 = w["kaufpreis"] + auf
        ges2 = kp2 * (1 + nk_q)
        bank2 = ges2 - w["eigenkapital"] - vd
        kd2 = rate_volltilger(bank2, z_, j_) * 12 + vd * PARAMETER["vd_zins_pct"] / 100
        print(f"  {'+' + eur(auf):>10} {eur(kp2):>11} {eur(auf * nk_q):>10} "
              f"{eur(kd2):>20} {kd2 - ref_kd:>+11,.0f}".replace(",", "."))
    print(f"\n  {eur(w['kaufpreis_max'])} ist die beschlossene OBERGRENZE, keine Option.")
    print("  Der höhere Preis erhöht dauerhaft GrESt-Bemessungsgrundlage, Restschuld")
    print("  und den Betrag, den ein späterer Verkauf erst wieder einspielen muss.")


def option3(w, bw, darlehen):
    kopf("4  WEG-TEILUNG — Mehrvolumen gegen Teilungskosten")
    tk = PARAMETER["teilungskosten"]
    quote = 0.95
    print(f"  Beleihungswert als Ganzes {eur(bw)}, Restschuld heute {eur(darlehen)},")
    print(f"  Teilungskosten {eur(tk)} (Annahme), Beleihungsquote {quote * 100:.0f} %.\n")
    print(f"  Die Kapazität muss erst die vorhandene Schuld einholen — sonst wird")
    print(f"  gemessen, was die Bank theoretisch hergäbe, nicht was ausgezahlt wird.\n")
    print(f"  {'Aufschlag':>10} {'BW in Summe':>14} {'{:.0f} % davon'.format(quote * 100):>13} "
          f"{'./. Restschuld':>15} {'nach Kosten':>13}")
    for auf in (0, 5, 10, 15, 20):
        neu = bw * (1 + auf / 100)
        frei = neu * quote - darlehen
        print(f"  {auf:>8} % {eur(neu):>14} {eur(neu * quote):>13} "
              f"{eur(frei):>15} {eur(frei - tk):>13}")
    # Ab welchem Aufschlag trägt die Teilung ihre Kosten?
    schwelle = next((a for a in range(0, 101)
                     if bw * (1 + a / 100) * quote - darlehen - tk > 0), None)
    if schwelle is not None:
        print(f"\n  Erst ab rund {schwelle} % Aufteilungsaufschlag trägt die Teilung ihre")
        print(f"  eigenen Kosten. Darunter ist sie ein Verlustgeschäft.")
    print("\n  Und der Aufschlag ist eine MARKTgröße beim Einzelverkauf an Selbstnutzer.")
    print("  Für eine dauerhaft vermietete, unkündbare Einheit ist er nicht erzielbar —")
    print("  dort steht ein Abschlag. Ob die Bank ihn im BELEIHUNGSwert überhaupt")
    print("  nachvollzieht, während alle Einheiten gehalten und vermietet werden,")
    print("  entscheidet diese Option. Vorab klären, nicht unterstellen.")


def auslaufkosten(w, darlehen):
    kopf("5  WAS EIN HOHER AUSLAUF KOSTET")
    print(f"  Dasselbe Darlehen {eur(darlehen)}, nur andere Zinsscheibe:\n")
    print(f"  {'Auslauf':>9} {'Zins':>8} {'Rate/Monat':>13} {'Zinsanteil Jahr 1':>19}")
    for grenze, z in PARAMETER["zinsstaffel"]:
        rate = rate_volltilger(darlehen, z, w["volltilger_j"])
        print(f"  {grenze:>7} % {z:>7.2f} % {eur(rate):>13} {eur(darlehen * z / 100):>19}")
    z80, z95 = zins_fuer_auslauf(80), zins_fuer_auslauf(95)
    print(f"\n  Differenz Zinsanteil Jahr 1 zwischen 80 % ({z80:.2f} %) und "
          f"95 % ({z95:.2f} %): {eur(darlehen * (z95 - z80) / 100)} EUR p.a.")
    print("  'Wieviel kann ich finanzieren' ist nicht 'wieviel sollte ich finanzieren'.")
    print(f"\n  Ein Volltilger über {w['volltilger_j']} Jahre hat kein Anschlusszinsrisiko —")
    print("  der Stresstest auf einen Anschlusszins entfällt hier zu Recht.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--annahmen", help="Pfad zu annahmen.json (die einzige zulässige Quelle)")
    args = ap.parse_args()

    w, klasse, herkunft = lade(args.annahmen)

    kopf("EINGABEWERTE, IHRE KLASSE UND IHRE HERKUNFT")
    for feld in ALIASE:
        v = w[feld]
        if v is None:
            g = "—"
        elif feld.endswith("_pct"):
            g = f"{v:g} %"
        elif feld.endswith("_j"):
            g = f"{v:g} J"
        else:
            g = eur(v)
        print(f"  {feld:<18} {g:>10}  [{klasse[feld]:<11}] {herkunft[feld]}")
    offen = [f for f in ALIASE if klasse[f] == "platzhalter"]
    if offen:
        print(f"\n  !! Platzhalter ohne Beleg: {', '.join(offen)}")
        print("     Vor jeder Entscheidung in annahmen.json ergänzen.")

    print("\n  PARAMETER — Bankkonditionen und Bewertungsparameter:")
    for k, v in PARAMETER.items():
        print(f"    {k:<28} {v}")
    print("    (kapitalisierung_pct und bewirtschaftungskosten_pct folgen der")
    print("     BelWertV; alles andere ist Annahme und bei der Bank zu erfragen.)")

    darlehen, bw, nk = basis(w)
    bezugsgroesse(w)
    option1(w, darlehen, bw)
    option2(w, bw, nk)
    preisaufschlag(w, nk)
    option3(w, bw, darlehen)
    auslaufkosten(w, darlehen)
    print("\n" + "=" * 76)
    print("Keine Rechts-, Steuer- oder Anlageberatung. Bankkonditionen sind Annahmen.")
    print("=" * 76)


if __name__ == "__main__":
    main()
