#!/usr/bin/env python3
"""Kennzahlen aus den Annahmen berechnen und den Vault dagegen abgleichen.

    python3 kennzahlen.py --strategie <ordner> [--vault <ordner>]

Ohne --vault werden nur die Kennzahlen ausgegeben. Mit --vault sucht das
Skript jeden Eurobetrag in den Notizen und meldet:

  TREFFER    der Betrag steht so im Vault — die Kennzahl ist propagiert
  ABWEICHUNG ein Betrag in der Nähe einer Kennzahl, aber nicht gleich

Die zweite Kategorie ist der eigentliche Zweck: So fällt eine Zahl auf, die
nach einer Annahmenänderung alt stehen geblieben ist. Das Skript entscheidet
nichts — es macht sichtbar, was ein Mensch prüfen muss.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

# Ein Betrag gilt als Abweichung, wenn er in dieser relativen Nähe einer
# Kennzahl liegt, ohne ihr zu entsprechen — eng genug, dass Szenarientabellen
# mit 700/750/800 Tsd. nicht jede Zeile melden.
NAEHE = 0.10
MIN_BETRAG = 1000.0

EURO = re.compile(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+|\d{4,})(?:,(\d{1,2}))?\s*(?:&nbsp;)?€")


def lade_modell(ordner: pathlib.Path):
    pfad = ordner / "modell.py"
    if not pfad.exists():
        sys.exit(f"modell.py nicht gefunden in {ordner}")
    spec = importlib.util.spec_from_file_location("modell", pfad)
    modul = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ordner))
    spec.loader.exec_module(modul)
    return modul


def kennzahlen(modell) -> dict[str, float]:
    a = modell.annahmen()
    o, f, st = a["objekt"], a["finanzierung"], a["steuern"]
    # Der Zielpreis ist eine Rechengroesse, keine feste Zahl -- er kommt aus
    # der "preisregel" in annahmen.json. Bis 2026-09-19 stand hier 740000 fest,
    # und damit pruefte der mechanische Abgleich gegen einen veralteten Anker.
    pr = a.get("preisregel")
    if pr and hasattr(modell, "preisbild"):
        vk = pr["planungs_verkaeufermiete_eur_m2"]
        pb = modell.preisbild(a=a)
        stufen = (("Zielpreis", round(pb["zielpreis"], -3)),
                  ("Obergrenze", round(pb["obergrenze"], -3)),
                  ("Aufgerufen", o["aufgerufener_preis"]))
    else:
        vk = a["mieten"]["haus_a_verkaeufermiete_eur_m2"]
        stufen = (("Aufgerufen", o["aufgerufener_preis"]),)
    werte: dict[str, float] = {}

    for name, kp in stufen:
        r = modell.rechne(kp, a=a, vk_miete_eur_m2=vk)
        werte[f"{name}: Kaufpreis"] = r["kaufpreis"]
        werte[f"{name}: Nebenkosten"] = r["nebenkosten"]
        werte[f"{name}: Darlehen"] = r["darlehen"]
        werte[f"{name}: EK gebunden"] = r["ek_benoetigt"]
        werte[f"{name}: Restliquidität"] = r["restliquiditaet"]
        werte[f"{name}: Jahresmiete"] = r["miete_jahr"]
        werte[f"{name}: Reinertrag"] = r["noi"]
        werte[f"{name}: Annuität"] = r["annuitaet"]
        werte[f"{name}: AfA-Basis"] = r["afa_basis"]
        werte[f"{name}: AfA"] = r["afa"]
        werte[f"{name}: Zins Jahr 1"] = r["zins_j1"]

    werte["Bodenwert"] = o["grundstueck_m2"] * o["bodenrichtwert_eur_m2"]
    werte["Eigenkapital"] = f["eigenkapital"]

    inv, fo = a["investitionen"], a["foerderung"]
    waerme = (inv["wp_haus_b"] + inv["wp_haus_a"] + inv["heizkoerper_typ33_haus_b"]
              + inv["fbh_haus_a"] + inv["hydraulik_speicher_ww"]
              + inv["entsorgung_kessel_tanks"])
    basis = min(waerme, fo["hoechstgrenze_ein_gebaeude"])
    werte["Wärmepaket"] = waerme
    # Die Bonuszeile nur dann, wenn es einen Bonus gibt. Sonst stuenden hier zwei
    # identische Betraege unter verschiedenen Prozentsaetzen -- und ein Leser
    # schloesse daraus, der Bonus sei noch eingerechnet.
    satz = fo["grundfoerderung_pct"]
    bonus = fo["effizienzbonus_pct"]
    werte["Zuschuss %g %%" % satz] = basis * satz / 100
    if bonus:
        werte["Zuschuss %g %% inkl. Bonus" % (satz + bonus)] = basis * (satz + bonus) / 100
    werte["PV inkl. Zählerplatz"] = (inv["pv_40_kwp"]
                                     + inv["zaehlerplatzumbau_je_we"] * o["einheiten"])
    return werte


TAG = re.compile(r"<[^>]+>")


def _zeilen(pfad: pathlib.Path) -> list[str]:
    """Zeilen einer Notiz oder eines erzeugten Dokuments.

    HTML wird mitgeprüft, weil die aus build.py erzeugten Dokumente genau der
    Ort sind, an dem hartkodierte Beträge eine Annahmenänderung überleben —
    und weil ein Fehler dort in einem Dokument steht, das nach außen geht.
    """
    text = pfad.read_text(encoding="utf-8")
    if pfad.suffix == ".html":
        text = TAG.sub(" ", text).replace("&nbsp;", " ").replace("&rarr;", "->")
    return text.splitlines()


def betraege(vault: pathlib.Path) -> list[tuple[float, pathlib.Path, int, str]]:
    gefunden = []
    pfade = sorted(list(vault.rglob("*.md")) + list(vault.rglob("*.html")))
    for pfad in pfade:
        # Das Archiv ist per Definition überholt — es zu prüfen erzeugt nur Rauschen.
        if "99-Archiv" in pfad.parts:
            continue
        for nr, zeile in enumerate(_zeilen(pfad), 1):
            for treffer in EURO.finditer(zeile):
                ganz = treffer.group(1).replace(".", "")
                nach = treffer.group(2) or "0"
                wert = float(f"{ganz}.{nach}")
                if wert >= MIN_BETRAG:
                    gefunden.append((wert, pfad, nr, zeile.strip()[:100]))
    return gefunden


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--strategie", required=True, type=pathlib.Path,
                   help="Ordner mit annahmen.json und modell.py")
    p.add_argument("--vault", type=pathlib.Path, help="Ordner mit den Notizen")
    p.add_argument("--naehe", type=float, default=NAEHE)
    args = p.parse_args()

    werte = kennzahlen(lade_modell(args.strategie))

    print("Kennzahlen aus den Annahmen\n")
    for name, wert in werte.items():
        print(f"  {name:<32} {wert:>14,.0f} €".replace(",", "."))

    if not args.vault:
        return

    alle = betraege(args.vault)
    print(f"\n{len(alle)} Eurobeträge in {args.vault.name} gefunden.")

    # Ein Betrag, der selbst eine Kennzahl ist, ist keine Abweichung.
    kanonisch = {round(w) for w in werte.values()}
    fehlend, abweichungen = [], []

    for name, wert in werte.items():
        exakt = [b for b in alle if abs(b[0] - wert) < 1]
        if not exakt:
            fehlend.append((name, wert))
        for b in alle:
            d = abs(b[0] - wert)
            if 1 <= d <= wert * args.naehe and round(b[0]) not in kanonisch:
                abweichungen.append((d / wert, name, wert, b))

    if fehlend:
        print("\nFEHLT — steht nirgends im Vault, also vermutlich nicht nachgezogen:\n")
        for name, wert in fehlend:
            print(f"  {name:<32} {wert:>14,.0f} €".replace(",", "."))

    if abweichungen:
        print("\nABWEICHUNG — nahe an einer Kennzahl, aber nicht gleich."
              " Jede Zeile ist zu prüfen:\n")
        gesehen = set()
        for _, name, wert, b in sorted(abweichungen)[:40]:
            schluessel = (b[1].name, b[2])
            if schluessel in gesehen:
                continue
            gesehen.add(schluessel)
            ab = 100 * (b[0] - wert) / wert
            print(f"  {b[1].name}:{b[2]}")
            print(f"    {b[0]:>12,.0f} € gegen {name} = {wert:,.0f} € ({ab:+.1f} %)"
                  .replace(",", "."))
            print(f"    {b[3]}")

    if not fehlend and not abweichungen:
        print("\nKeine fehlenden Kennzahlen, keine Abweichungen im gesetzten Band.")


if __name__ == "__main__":
    main()
