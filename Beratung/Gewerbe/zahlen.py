"""Alle Rechenbeispiele der Gewerbe-Unterlagen. Einzige Quelle für Zahlen in den Präsentationen.

Jede Zahl ist entweder ein Rechenbeispiel auf Basis einer gekennzeichneten Annahme
oder ein gesetzlicher Wert mit Fundstelle. Auch Prozentsätze, die im Text stehen, kommen von hier.
Aufruf zur Kontrolle: python3 zahlen.py
"""
from decimal import Decimal, ROUND_HALF_UP


def _d(x):
    return x if isinstance(x, Decimal) else Decimal(str(x))


def eur(x):
    """Volle Euro, kaufmännisch gerundet (338,5 → 339; Pythons round() rundet auf die gerade Zahl)."""
    d = _d(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return f"{d:,}".replace(",", ".") + " €"


def eur2(x):
    """Cent-genau, kaufmännisch gerundet (51,415 → 51,42)."""
    d = _d(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def pct(x):
    """Prozentsatz für den Text, z. B. 0.026 → „2,6 %“."""
    s = f"{_d(x) * 100:f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",") + " %"


Z = {}

# Ertragsausfall (betrieb.html): Annahmen für das Rechenbeispiel, keine Branchenwerte
BU_FIX = Decimal(20000)     # Annahme: feste Kosten im Monat (Miete, Löhne, Leasing, Kredite)
BU_MONATE = 6               # Annahme: Monate Stillstand nach einem Großschaden
Z["bu_fix"] = eur(BU_FIX)
Z["bu_monate"] = str(BU_MONATE)
Z["bu_summe"] = eur(BU_FIX * BU_MONATE)

# Rechengrößen 2026 (dieselben Werte wie Privat/vorab-check/QUELLEN.md und rechenkern.js)
BBG_RV_2026 = Decimal(101400)           # BBG allgemeine RV, Jahr; SV-Rechengrößen 2026 (Beleg wie QUELLEN.md: AOK, KSK)
BEZUGSGROESSE_2026 = Decimal(3955)      # Monat; BA, Fachliche Weisungen § 28a SGB III, Stand 01/2026, S. 20
GERINGFUEGIGKEIT_2026 = Decimal(603)    # Monat; Mindestbemessung freiwillige RV (§ 167 SGB VI)
RV_SATZ = Decimal("0.186")              # Beitragssatz RV (wie rechenkern.js rv_satz)
ALV_SATZ = Decimal("0.026")             # Beitragssatz AV; BA, Fachliche Weisungen § 28a SGB III, Stand 01/2026, S. 20

# Betriebliche Altersversorgung (mitarbeiter.html)
BAV_ANSPRUCH = Decimal("0.04")          # § 1a Abs. 1 BetrAVG: Anspruch bis 4 % der BBG RV
BAV_STEUERFREI = Decimal("0.08")        # § 3 Nr. 63 S. 1 EStG: steuerfrei bis 8 % der BBG RV
BAV_SVFREI = Decimal("0.04")            # § 1 Abs. 1 S. 1 Nr. 9 SvEV: sozialversicherungsfrei bis 4 % der BBG RV
BAV_ZUSCHUSS = Decimal("0.15")          # § 1a Abs. 1a BetrAVG: Pflichtzuschuss 15 %
Z["bbg_rv"] = eur(BBG_RV_2026)
Z["bav_anspruch_pct"] = pct(BAV_ANSPRUCH)
Z["bav_steuerfrei_pct"] = pct(BAV_STEUERFREI)
Z["bav_svfrei_pct"] = pct(BAV_SVFREI)
Z["bav_zuschuss_pct"] = pct(BAV_ZUSCHUSS)
Z["bav_anspruch_jahr"] = eur(BBG_RV_2026 * BAV_ANSPRUCH)
Z["bav_anspruch_monat"] = eur(BBG_RV_2026 * BAV_ANSPRUCH / 12)
Z["bav_steuerfrei_jahr"] = eur(BBG_RV_2026 * BAV_STEUERFREI)
Z["bav_steuerfrei_monat"] = eur(BBG_RV_2026 * BAV_STEUERFREI / 12)
Z["bav_svfrei_monat"] = eur(BBG_RV_2026 * BAV_SVFREI / 12)
# Rechenbeispiel Entgeltumwandlung. Annahmen: 200 € im Monat, Lohn unter der BBG (sonst sinkt der Zuschuss)
BAV_UMWANDLUNG = Decimal(200)
Z["bav_umw"] = eur(BAV_UMWANDLUNG)
Z["bav_zuschuss"] = eur(BAV_UMWANDLUNG * BAV_ZUSCHUSS)
Z["bav_beitrag"] = eur(BAV_UMWANDLUNG * (1 + BAV_ZUSCHUSS))

# Geringverdienerförderung § 100 EStG, Fassung 2026 (gesetze-im-internet.de, Rechtsprüfung 11.10.2026)
GV_GRENZE_MONAT = Decimal(2575)         # § 100 Abs. 3 Nr. 3 EStG
GV_SATZ = Decimal("0.30")               # § 100 Abs. 2 EStG: 30 % des zusätzlichen Arbeitgeberbeitrags
GV_BEITRAG_MAX = Decimal(960)           # § 100 Abs. 2 EStG: geförderter Beitrag höchstens 960 €
GV_MINDEST = Decimal(240)               # § 100 Abs. 3 Nr. 2 EStG: Mindestbeitrag im Jahr
Z["gv_grenze_monat"] = eur(GV_GRENZE_MONAT)
Z["gv_satz"] = pct(GV_SATZ)
Z["gv_foerder_max"] = eur(GV_SATZ * GV_BEITRAG_MAX)
Z["gv_mindest"] = eur(GV_MINDEST)

# Betriebliche Krankenversicherung: Sachbezugsfreigrenze § 8 Abs. 2 S. 11 EStG
Z["bkv_freigrenze"] = eur(50)

# Selbständige (unternehmer.html)
# Freiwillige RV 2026: Mindestbeitrag aus der Geringfügigkeitsgrenze, Höchstbeitrag aus der BBG
# (stimmt mit der DRV-Meldung vom 09.02.2026 überein: 112,16 € und 1.571,70 €)
Z["rv_frei_min"] = eur2(GERINGFUEGIGKEIT_2026 * RV_SATZ)
Z["rv_frei_max"] = eur2(BBG_RV_2026 / 12 * RV_SATZ)
# Arbeitslosenversicherung auf Antrag (§ 28a, § 345b SGB III): Bemessung = Bezugsgröße, im Gründungszeitraum die Hälfte
Z["alv_satz"] = pct(ALV_SATZ)
Z["alv_beitrag"] = eur2(BEZUGSGROESSE_2026 * ALV_SATZ)
Z["alv_gruender"] = eur2(BEZUGSGROESSE_2026 / 2 * ALV_SATZ)

# Pauschaldotierte Unterstützungskasse (puk.html, unternehmer.html), § 4d Abs. 1 S. 1 Nr. 1 EStG und § 10 Abs. 3 Nr. 3 BetrAVG
# (Rechtsprüfung 11.10.2026, dejure.org / gesetze-im-internet.de)
PUK_POLSTER = Decimal("0.25")           # Zuwendung je Leistungsanwärter: 25 % der Jahresaltersrente pro Jahr (Buchst. b)
PUK_POLSTER_NUR_RISIKO = Decimal("0.06")  # 6 %, wenn nur Invaliditäts- oder Hinterbliebenenversorgung zugesagt
PUK_VERMOEGEN_FAKTOR = 8                # zulässiges Kassenvermögen: 8-Fache der Zuwendungen nach Buchst. b (plus Deckungskapital Rentner)
PSV_FAKTOR_UKASSE = 20                  # PSV-Bemessung U-Kasse: 20-Fache der Zuwendungen nach Buchst. b
PSV_SATZ_2025 = Decimal("0.0012")       # PSVaG-Beitragssatz 2025: 1,2 ‰ (Satz 2026 wird Anfang November 2026 festgesetzt)
# Rechenbeispiel, Annahme: zugesagte Jahresaltersrente 12.000 € für einen Leistungsanwärter
PUK_RENTE_JAHR = Decimal(12000)
puk_zuwendung = PUK_RENTE_JAHR * PUK_POLSTER
Z["puk_polster_pct"] = pct(PUK_POLSTER)
Z["puk_polster_risiko_pct"] = pct(PUK_POLSTER_NUR_RISIKO)
Z["puk_faktor"] = str(PUK_VERMOEGEN_FAKTOR)
Z["puk_psv_faktor"] = str(PSV_FAKTOR_UKASSE)
Z["puk_rente_jahr"] = eur(PUK_RENTE_JAHR)
Z["puk_zuwendung"] = eur(puk_zuwendung)
Z["puk_kassenvermoegen_max"] = eur(puk_zuwendung * PUK_VERMOEGEN_FAKTOR)
Z["puk_psv_basis"] = eur(puk_zuwendung * PSV_FAKTOR_UKASSE)
Z["psv_satz_2025"] = f"{PSV_SATZ_2025 * 1000:f}".rstrip("0").rstrip(".").replace(".", ",") + " ‰"
Z["puk_psv_beitrag_2025"] = eur2(puk_zuwendung * PSV_FAKTOR_UKASSE * PSV_SATZ_2025)

# Kontrolle gegen die belegten Werte (Rechtsprüfungen vom 11.10.2026, BA-Weisungen § 28a, DRV 09.02.2026)
assert Z["rv_frei_min"] == "112,16 €" and Z["rv_frei_max"] == "1.571,70 €"
assert Z["alv_beitrag"] == "102,83 €" and Z["alv_gruender"] == "51,42 €"
assert Z["gv_foerder_max"] == "288 €"

if __name__ == "__main__":
    for k, v in Z.items():
        print(f"{k:20s} {v}")
