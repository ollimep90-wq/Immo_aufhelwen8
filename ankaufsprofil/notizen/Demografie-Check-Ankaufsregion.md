---
tags: [ankaufsprofil, demografie, recherche]
stand: 2026-10-09
---

# Demografie-Check Ankaufsregion

Prüft, ob die Kreise im Ankaufsprofil den Filter „stabile oder wachsende
Bevölkerung" erfüllen. Alle Werte sind **amtliche Vorausberechnungen**
(Quellenklasse: Recherche, amtliche Statistik), keine Ist-Werte. Die
Veränderungen der Gesamtregionen sind **eigene Rechnung** aus den
Tabellenwerten (Python).

## NRW – IT.NRW, Basisvariante, 31.12.2023 → 31.12.2050

| Gebiet | 2023 (Tsd.) | Index 2035 | Index 2050 | Veränderung bis 2050 | davon natürlich | davon Wanderung |
|---|---:|---:|---:|---:|---:|---:|
| Bonn (Stadt) | 321,7 | 103,9 | 103,9 | +3,9 % | −4,0 | +7,9 |
| Düren (Kreis) | 278,5 | 102,2 | 100,9 | +0,9 % | −13,4 | +14,3 |
| Euskirchen (Kreis) | 201,8 | 102,4 | 100,9 | +0,9 % | −16,0 | +16,9 |
| Köln (Stadt) | 1.024,4 | 100,7 | 99,6 | −0,4 % | −2,4 | +2,0 |
| Rhein-Erft-Kreis | 476,4 | 100,9 | 99,0 | −1,0 % | −11,1 | +10,1 |
| *NRW gesamt (Vergleich)* | 18.017,5 | 100,0 | 97,4 | −2,6 % | −11,1 | +8,5 |
| Aachen (ehem. Kreis, Teil der Städteregion) | 318,7 | 99,9 | 96,9 | −3,1 % | −13,5 | +10,4 |
| Rhein-Sieg-Kreis | 605,3 | 99,9 | 96,7 | −3,3 % | −13,0 | +9,7 |
| Aachen (Stadt) | 263,8 | 98,3 | 95,4 | −4,6 % | −5,9 | +1,4 |
| Städteregion Aachen gesamt | 582,5 | – | – | −3,8 % *(eigene Rechnung)* | – | – |
| Heinsberg (Kreis, seit 09.10.2026 im Profil) | 262,1 | 104,5 | 104,7 | +4,7 % | −15,2 | +19,8 |

Index: 2023 = 100. Natürliche Entwicklung und Wanderung in % der Bevölkerung 2023.

Quelle: IT.NRW im Auftrag des MWIKE NRW, *Bevölkerungsvorausberechnung für
Nordrhein-Westfalen 2024 bis 2050/2070 – Ergebnisse*, Tab. 7 und Tab. 8.
https://landesplanung.nrw.de/system/files/media/document/file/bevoelkerungsvorausberechnung_2024_2050-20704_0.pdf

## Rheinland-Pfalz (Eifel) – Statistisches Landesamt RLP, Projektion, 2020 → 2040

**Nicht direkt mit NRW vergleichbar:** Das Basisjahr ist 2020 statt 2023, der Horizont 2040 statt 2050.

| Landkreis | 2020 | 2040 | Veränderung |
|---|---:|---:|---:|
| Eifelkreis Bitburg-Prüm | 100.055 | 104.649 | +4,6 % |
| Ahrweiler | 130.479 | 133.807 | +2,6 % |
| Vulkaneifel | 60.491 | 58.497 | −3,3 % (alle drei Verbandsgemeinden rückläufig) |

Quelle: Statistisches Landesamt Rheinland-Pfalz, *Sechste regionalisierte
Bevölkerungsvorausberechnung (Basisjahr 2020)*, Kreisblätter 131, 232 und 233
sowie die Blätter auf Verbandsgemeindeebene.
https://www.statistik.rlp.de/fileadmin/dokumente/stat_analysen/RP_2070/kreis/

## Was daraus folgt

Die folgenden Punkte sind Schlussfolgerungen aus den Tabellen.

- **Der Filter widerspricht der Eifel nicht.** Euskirchen und Düren wachsen
  laut Prognose bis 2035 und liegen 2050 noch über dem Stand von 2023.
- **Aachen und der Rhein-Sieg-Kreis erfüllen den Filter auf Kreisebene nicht.**
  Ihr Rückgang ist stärker als der NRW-Durchschnitt.
- **Überall entscheidet der Zuzug.** Ohne Wanderung schrumpft jeder Kreis.
  Der Filter „Zuwanderung" trifft also den eigentlichen Treiber.
- **Kreiswerte verdecken Unterschiede innerhalb des Kreises.** Gemeinden
  innerhalb eines Kreises können deutlich abweichen. Bei einem konkreten
  Objekt deshalb die Gemeindeebene prüfen. Für NRW-Gemeinden ist das hier
  **noch nicht geprüft**.

## Entscheidungen (eigene Angabe, 09.10.2026)

- Der Bevölkerungsfilter steht im Profil als **„bevorzugt"** und nicht als
  Ausschluss. Aachen und der Rhein-Sieg-Kreis bleiben deshalb im Profil.
- Die Eifel-Kreise in Rheinland-Pfalz (Ahrweiler, Bitburg-Prüm, Vulkaneifel)
  werden **nicht** aufgenommen.
- **Heinsberg wird aufgenommen**, weil der Kreis laut Prognose am stärksten
  wächst (+4,7 % bis 2050).

## Vertiefung: Warum schrumpft die Stadt Aachen in der IT.NRW-Prognose? (Stand 09.10.2026)

**Zerlegung laut IT.NRW, 2023 → 2050** (Recherche, Tab. 8 und 9; Prozente als eigene Rechnung)

- Natürliche Bilanz −5,9 % (≈ −15,6 Tsd.), Wanderung nur +1,4 % (≈ +3,7 Tsd.),
  zusammen −4,6 % (263,8 → 251,7 Tsd.).
- Zum Vergleich: Bonn hat einen Wanderungsgewinn von +7,9 %, Köln von +2,0 %.
  Aachen hat also **kein besonderes Sterbeproblem**, sondern einen **schwachen
  Zuzugsüberschuss**.
- Altersgruppen: unter 20 Jahre −11,7 %, 20–67 Jahre −5,8 %, 67 Jahre und älter +7,9 %.

**Mögliche Gründe**

- **Fortschreibung der Vergangenheit (belegt):** IT.NRW schreibt die
  Wanderungen des Stützzeitraums 2017–2023 fort. In diesen Zeitraum fallen die
  Corona-Jahre. Laut Demografiemonitoring der Stadt brach 2020 die
  Bildungswanderung der 18- bis 24-Jährigen ein, der Saldo lag bei +106 nach
  +1.651 im Jahr 2019.
- **Rückläufiger Saldo (Recherche, Stadt Aachen „Aachen in Zahlen 2025"):**
  Der Wanderungssaldo sinkt seit 2014 und war 2020 und 2024 negativ.
  Einzelwerte stehen nur in einer Grafik; nicht nachgeprüft.
- **Familien ziehen ins Umland (belegt, Demografiemonitoring 2019/2020):**
  Saldo der Familienwanderung −1.321, Saldo gegenüber der Städteregion
  −598 (2019) bzw. −776 (2020).
- **Abhängigkeit von Studierenden (Schlussfolgerung):** Die 20- bis
  29-Jährigen stellen 23 % der Bevölkerung (Zensus 2022). Die KMK rechnet für
  NRW bis 2030 mit 5 % weniger Studierenden (zitiert in der Stadtprognose).

**Gegenposition: die eigene Prognose der Stadt Aachen (Dezember 2023)**

- Medium-Variante 2021 → 2039: +3,0 % (258.588 → 266.273), Low +0,8 %, High +4,0 %.
- Die Stadt nennt die IT.NRW-Prognose von 2022 ausdrücklich „Corona-beeinflusst".
- **Nicht direkt vergleichbar:** Die Stadt rechnet mit der wohnberechtigten
  Bevölkerung, also einschließlich Nebenwohnsitzen, die bei Studierenden
  häufig sind. Basis ist 2021, vor der Zensuskorrektur. IT.NRW rechnet nur mit
  dem Hauptwohnsitz.
- Treiber laut Stadt sind Wohnungsbauprojekte (Campus West, Blue Gate,
  Richtericher Dell u. a.). Wird weniger gebaut, kommen auch weniger Menschen.

**Fazit (Schlussfolgerung):** Die Spanne reicht von leichtem Wachstum bis zu
leichtem Rückgang. Ein „Schrumpfen" ist kein Strukturbruch. Es hängt am
Zuzug von Studierenden und Berufseinsteigern und am Wohnungsbau.

Quellen:
- IT.NRW 2024–2050, Tab. 7–9 (siehe oben)
- Stadt Aachen, Bevölkerungsprognose 2023–2039:
  https://www.aachen.de/aachen-entdecken/typisch-aachen/statistische-daten/bevoelkerungsprognose-2023-2039.pdf
- Stadt Aachen, Aachen in Zahlen 2025 (Wanderung 2014–2024)
- Stadt Aachen, Demografiemonitoring 2019 und 2020
- Ratsinfo Aachen zum Zensus 2022: Korrektur +4,4 %; nicht direkt
  geöffnet, nur über die Suchergebnisse
