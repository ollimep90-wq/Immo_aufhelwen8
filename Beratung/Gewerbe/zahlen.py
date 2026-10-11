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

if __name__ == "__main__":
    for k, v in Z.items():
        print(f"{k:20s} {v}")
