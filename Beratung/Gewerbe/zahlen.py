"""Alle Rechenbeispiele der Gewerbe-Unterlagen. Einzige Quelle für Zahlen in den Präsentationen.

Jede Zahl ist entweder ein Rechenbeispiel auf Basis einer gekennzeichneten Annahme
oder ein gesetzlicher Wert mit Fundstelle. Aufruf zur Kontrolle: python3 zahlen.py
"""


def eur(x):
    return f"{round(x):,}".replace(",", ".") + " €"


Z = {}

# Ertragsausfall (betrieb.html): Annahmen für das Rechenbeispiel, keine Branchenwerte
BU_FIX = 20000          # Annahme: feste Kosten im Monat (Miete, Löhne, Leasing, Kredite)
BU_MONATE = 6           # Annahme: Monate Stillstand nach einem Großschaden
Z["bu_fix"] = eur(BU_FIX)
Z["bu_monate"] = str(BU_MONATE)
Z["bu_summe"] = eur(BU_FIX * BU_MONATE)

# Betriebliche Altersversorgung (mitarbeiter.html), Werte 2026
# BBG allgemeine Rentenversicherung 2026: 101.400 €/Jahr, bundeseinheitlich
# (Sozialversicherungsrechengrößen-Verordnung 2026; belegt über Barmer und lohn-info, Rechtsprüfung 11.10.2026)
BBG_RV_2026 = 101400
Z["bbg_rv"] = eur(BBG_RV_2026)
Z["bav_anspruch_jahr"] = eur(BBG_RV_2026 * 0.04)        # § 1a Abs. 1 BetrAVG: bis 4 % der BBG RV
Z["bav_anspruch_monat"] = eur(BBG_RV_2026 * 0.04 / 12)
Z["bav_steuerfrei_jahr"] = eur(BBG_RV_2026 * 0.08)      # § 3 Nr. 63 S. 1 EStG: 8 % der BBG RV
Z["bav_steuerfrei_monat"] = eur(BBG_RV_2026 * 0.08 / 12)
Z["bav_svfrei_monat"] = eur(BBG_RV_2026 * 0.04 / 12)    # § 1 Abs. 1 S. 1 Nr. 9 SvEV: 4 % der BBG RV
# Rechenbeispiel Entgeltumwandlung (Annahme: 200 € im Monat), Zuschuss 15 % nach § 1a Abs. 1a BetrAVG
BAV_UMWANDLUNG = 200
Z["bav_umw"] = eur(BAV_UMWANDLUNG)
Z["bav_zuschuss"] = eur(BAV_UMWANDLUNG * 0.15)
Z["bav_beitrag"] = eur(BAV_UMWANDLUNG * 1.15)
# Geringverdienerförderung § 100 EStG, Fassung 2026 (gesetze-im-internet.de, Rechtsprüfung 11.10.2026)
Z["gv_grenze_monat"] = eur(2575)
Z["gv_foerder_max"] = eur(288)
Z["gv_mindest"] = eur(240)
# Betriebliche Krankenversicherung: Sachbezugsfreigrenze § 8 Abs. 2 S. 11 EStG
Z["bkv_freigrenze"] = eur(50)

if __name__ == "__main__":
    for k, v in Z.items():
        print(f"{k:20s} {v}")
