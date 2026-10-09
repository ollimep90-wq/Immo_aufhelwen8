---
tags: [ankaufsprofil, demografie, marktdaten, recherche]
stand: 2026-10-09
---

# Marktcheck: tatsächliche Wanderung 2018–2024 und Kaufpreisfaktoren für MFH

Diese Notiz klärt zwei Fragen:

1. Ist der Rückgang von Aachen in der IT.NRW-Prognose nur ein Corona-Effekt?
   Und hat Corona umgekehrt die ländlichen Kreise geschönt?
2. Ist Kaufpreisfaktor 10 (10 % Bruttorendite) am Markt erreichbar?

Alle Quoten und Faktoren hat Python aus den amtlichen Tabellen berechnet
(Skripte: `ankaufsprofil/analyse/parse_kp.py`, Auswertung im Chatverlauf vom 09.10.2026).

**Geprüft durch den zahlen-pruefer am 09.10.2026.** Die Rohdaten und Rechnungen
wurden bestätigt. Vier Schlussfolgerungen und mehrere Rundungen auf eine
Nachkommastelle wurden korrigiert; die Korrekturen sind im Text markiert.

---

## 1 · Tatsächliche Wanderung 2018–2024

Quelle: IT.NRW, Kommunalprofile (Stand 15.01.2026), Tabelle „Bevölkerungsstand und
-bewegung 2018–2024". Abgeleitet sind:

- „Städteregion ohne Stadt Aachen": Städteregion minus Stadt (eigene Rechnung)
- „Deutsche": insgesamt minus Nichtdeutsche (eigene Rechnung)

Werte je 1.000 Einwohner (alle Einwohner, auch beim Saldo Deutsche) und Jahr, Durchschnitte der jeweiligen Jahre.
„Gesamt 2023/24" = Wanderungssaldo + natürlicher Saldo, ohne die amtlichen Bestandskorrekturen; deshalb weicht er leicht von der Einwohnerveränderung unten ab (Aachen amtlich −0,42 je 1.000).
*(Rundungen am 09.10.2026 nach Nachrechnung um bis zu 0,1 korrigiert.)*

| Gebiet | Wanderung gesamt 2018/19 | 2020/21 (Corona) | 2022 (Ukraine) | 2023/24 | Saldo Deutsche 2018/19 | 2020/21 | 2023/24 | Natürl. Saldo 2023/24 | **Gesamt 2023/24** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Stadt Aachen** | +5,9 | +1,5 | +14,1 | **+1,5** | −6,2 | −7,3 | **−9,9** | −2,1 | **−0,7** |
| Städteregion ohne Stadt | +2,3 | +2,2 | +13,3 | +7,7 | −1,7 | −0,6 | +0,6 | −4,3 | +3,4 |
| Kreis Euskirchen | +6,3 | +6,7 | +16,8 | +12,5 | +3,8 | +5,1 | +3,6 | −4,1 | **+8,4** |
| Kreis Düren | +4,6 | +6,9 | +18,7 | +8,6 | −0,1 | +2,8 | +1,5 | −4,0 | +4,6 |
| Kreis Heinsberg | +6,7 | +8,4 | +17,3 | +8,8 | +2,7 | +4,8 | +3,0 | −4,2 | +4,6 |
| Rhein-Erft-Kreis | +4,0 | +3,3 | +16,2 | +8,2 | −0,2 | +1,2 | +0,7 | −3,7 | +4,5 |
| Rhein-Sieg-Kreis | +2,8 | +2,0 | +16,0 | +5,3 | −0,1 | +0,1 | −0,6 | −3,3 | +2,0 |
| Köln | +2,2 | −6,6 | +11,7 | +2,8 | −2,2 | −6,8 | −3,1 | −1,1 | +1,7 |
| Bonn | +5,0 | +3,1 | +15,1 | +2,9 | −3,3 | −1,9 | −5,7 | −1,4 | +1,5 |

Einwohnerzahl vom 31.12.2023 zum 31.12.2024 (IT.NRW, Basis Zensus 2022):

| Gebiet | Veränderung |
|---|---:|
| Stadt Aachen | **−1.102 (−0,42 %)** |
| Städteregion ohne Stadt | +1.049 (+0,33 %) |
| Euskirchen | +768 (+0,38 %) |
| Düren | +823 (+0,30 %) |
| Heinsberg | +1.532 (+0,58 %) |
| Rhein-Erft | +1.576 (+0,33 %) |
| Rhein-Sieg | +158 (+0,03 %) |
| Köln | +213 (+0,02 %) |
| Bonn | +1.656 (+0,51 %) |

Hinweis: Die Zahlen von 2018 bis 2021 stehen auf Zensus-2011-Basis, ab 2022 auf
Zensus-2022-Basis. Der Sprung der Einwohnerzahl 2022 in Aachen (+13.816) geht
**überwiegend (rund 10.700) auf Zensus- und Bestandskorrekturen** zurück. Echte
Bewegung war nur rund +3.100 (Wanderung +3.717, natürlicher Saldo −638).
*(Korrigiert am 09.10.2026. Vorher stand hier, der Sprung sei ganz Zensuskorrektur,
„nicht ein echter Zuzug". Das war zu pauschal.)*

### Was die Daten zeigen (Schlussfolgerung)

- **Der Corona-Knick in Aachen war echt, aber er hat sich nicht erholt.**
  Der Zuzugsüberschuss fiel von +5,9 auf +1,5 je 1.000 Einwohner und liegt
  2023/24 immer noch bei +1,5. Im Jahr 2024 war er negativ (−595 Personen,
  −2,3 je 1.000). Die These „ohne Corona wäre Aachen positiv" stützen die
  Ist-Daten nicht.
- **Deutsche verlassen Aachen zunehmend:** −6,2 je 1.000 vor Corona, −9,9 je
  1.000 in 2023/24, davon −12,9 je 1.000 im Jahr 2024 (−3.388 Personen).
  Aachen hat nur noch bei Nichtdeutschen Wanderungsgewinne (zu ihnen gehören
  internationale Studierende). *(Korrigiert: Vorher stand „Zuzug aus dem
  Ausland". Die Daten trennen aber nach Staatsangehörigkeit, nicht nach Herkunft.)*
  Auch die Zahl der Deutschen ist auf alle Einwohner bezogen. Je 1.000 Deutsche
  wären es −12,8 (2023/24) bzw. −16,7 (2024). Zu den internationalen Studierenden (36 % der RWTH-Studierenden laut Studienportal;
  nicht bei der RWTH geprüft).
- **Kein Corona-Strohfeuer in den Landkreisen.** In Euskirchen und Heinsberg
  war der Zuzug Deutscher schon vor Corona positiv (+3,8 bzw. +2,7). Er stieg
  2020/21 leicht an und liegt 2023/24 wieder etwa auf Vorkrisenniveau. Düren
  hat sich sogar verbessert (von −0,1 auf +1,5).
- **Die Ukraine-Flucht 2022 hat die Gebiete unterschiedlich stark angehoben**:
  +8,3 (Aachen) bis +14,1 (Düren) je 1.000 gegenüber 2018/19. Auch 2023/24
  tragen Nichtdeutsche einen großen Teil des Zuzugs. In Euskirchen sind es
  +8,9 von +12,5. Ob das Zuweisungen oder marktgetriebene Nachfrage sind,
  geben die Daten nicht her. **Für die Nachfrage nach Wohnungen am Markt ist
  die Spalte „Saldo Deutsche" der robustere Vergleich.** Auch dort liegen
  Euskirchen, Heinsberg und Düren vor der Stadt Aachen.
  *(Korrigiert: Vorher stand „gleichermaßen" und „verzerrt nicht". Das decken
  die Zahlen nicht.)*
- **Fazit:** Die Ist-Daten bestätigen die Richtung der IT.NRW-Prognose 2024–2050
  (siehe Notiz „Demografie-Check Ankaufsregion").
  Euskirchen, Heinsberg, Düren und Rhein-Erft stehen besser da als die
  Stadt Aachen.

---

## 2 · Kaufpreisfaktoren (Rohertragsfaktoren) für Mehrfamilienhäuser

### Direkt veröffentlichte Werte (Beleg)

| Gebiet | Quelle (Kaufjahre) | Rohertragsfaktor Mittel | Streuung | Spanne | Fälle | ≙ Bruttorendite |
|---|---|---:|---:|---:|---:|---:|
| Stadt Aachen | GMB Städteregion 2026 (2024–25) | 19,2 | ± 3,4 | 11,7 – 28,6 | 119 | 5,2 % |
| ehem. Kreis Aachen | GMB Städteregion 2026 (2024–25) | 17,5 | ± 3,2 | 8,9 – 26,8 | 114 | 5,7 % |
| Euskirchen, Restnutzungsdauer > 40 J. | GMB Euskirchen 2024 (2023) | 18,1 | ± 2,6 | – | 16 | 5,5 % |
| Euskirchen, Restnutzungsdauer < 40 J. | GMB Euskirchen 2024 (2023) | 13,9 | ± 1,3 | – | 10 | 7,2 % |

Die Bruttorendite (100 / Faktor) ist eigene Rechnung.

Methodik:

- **Städteregion:** Rohertrag nach Mietspiegel bzw. marktüblicher Miete,
  nicht nach Ist-Miete.
- **Euskirchen:** Rohertrag aus der Nettokaltmiete, laut Modellbeschreibung
  unter Berücksichtigung des örtlichen Mietspiegels (§ 31 ImmoWertV), also auch
  hier keine reine Ist-Miete. Nur bauschadensfreie Weiterverkäufe.
- Die beiden Reihen sind daher nur grob vergleichbar.

### Grobe Schätzung ohne veröffentlichten Faktor

Die folgenden Werte sind eigene Rechnung und nur eine Schätzung:
Durchschnittspreis je m² geteilt durch Durchschnittsmiete × 12.

| Gebiet | Quelle | Preis €/m² | Miete €/m² | ≈ Faktor | Fälle |
|---|---|---:|---:|---:|---:|
| Kreis Heinsberg | GMB Heinsberg 2024 (2023) | 1.199 | 5,8 | ≈ 17,2 | 8 |
| Kreis Düren (ohne Stadt Düren) | GMB Düren 2024 (2023) | 1.346 (± 589) | 6,1 (± 1,5) | ≈ 18,4 (kaum belastbar) | 4 |

**Achtung, diese Schätzung ist ungenau.** Die gleiche Rechnung ergibt für
Euskirchen 19,7 bzw. 16,8. Der Gutachterausschuss weist dort aber 18,1 bzw.
13,9 aus. Die Methode überschätzt also um etwa 1,5 bis 3 Punkte. Für Düren
liegen außerdem nur 4 Fälle vor.

**Noch nicht erhoben:** Köln, Bonn, Rhein-Erft, Rhein-Sieg und die Stadt Düren.
Für Euskirchen, Heinsberg und Düren gibt es vermutlich schon Berichte mit dem
Kaufjahr 2024 (GMB 2025); diese sind nicht abgerufen.

### Was das für Faktor 10 heißt (Schlussfolgerung)

- **Faktor 10 liegt überall weit unter dem Marktdurchschnitt**, nämlich
  2,3 bis 3,1 Standardabweichungen darunter. In der Stadt Aachen lag der
  niedrigste von 119 Verkäufen bei 11,7. Im ehemaligen Kreis Aachen reicht
  die Spanne bis 8,9, das ist aber die äußerste Ausnahme.
- **Am nächsten an Faktor 10 kommen ältere Häuser mit kurzer
  Restnutzungsdauer in Euskirchen (13,9 im Mittel).** Laut Gutachterausschuss
  sind das bauschadensfreie Objekte mit kürzerer Restnutzungsdauer (Ø 32 Jahre).
  Der niedrige Faktor bildet also das Alter ab, nicht Sanierungsstau. Höhere
  Instandhaltung ist aber zu erwarten *(Annahme)*. *(Korrigiert: Vorher stand,
  die Objekte hätten Sanierungsbedarf. Das widerspricht der Quelle.)*
- **Faktor 10 als harte Ankaufsgrenze würde fast den gesamten regulären
  Markt ausschließen**, in Aachen wie in der Region. Erreichbar wäre er nur
  in Sondersituationen: Sanierungsstau, Leerstand, Zwangsversteigerung,
  Insolvenz. Der Wert spiegelt dann den Investitionsbedarf wider, eine
  echte Mehrrendite ist er nicht.
- **Für den Vergleich Aachen gegen Region:** Die Region ist **etwa 1 bis 5
  Faktorpunkte** günstiger als die Stadt Aachen (Mittel 19,2). Im ehemaligen
  Kreis Aachen sind es 1,7, in Euskirchen je nach Restnutzungsdauer 1,1 bzw. 5,3.
  Heinsberg und Düren liegen nach Abzug der bekannten Überschätzung bei
  vermutlich 2 bis 5. Dabei schneidet die Region laut Ist- und Prognosedaten bei
  der Bevölkerung besser ab. **Einschränkungen:** Die Kaufjahre unterscheiden
  sich (Städteregion 2024/25, sonst 2023, mitten in der Preiswende). Die
  Methodik ist nicht identisch, wobei auch Euskirchen laut Modellbeschreibung
  mietspiegelorientiert rechnet. Heinsberg und Düren beruhen auf wenigen Fällen.
  *(Korrigiert: Vorher stand „nur etwa 1,5 bis 2 Faktorpunkte". Das war zu eng.)*

---

## Quellen

- IT.NRW, Kommunalprofile (Stand 15.01.2026):
  https://statistik.nrw/sites/default/files/municipalprofiles/l05334.pdf (Städteregion),
  l05334002 (Stadt Aachen), l05366 (Euskirchen), l05358 (Düren), l05370 (Heinsberg),
  l05362 (Rhein-Erft), l05382 (Rhein-Sieg), l05315 (Köln), l05314 (Bonn)
- Gutachterausschuss Städteregion Aachen, Grundstücksmarktbericht 2026, Kap. 5.2:
  https://epflicht.ulb.uni-bonn.de/download/pdf/817403
- Gutachterausschuss Kreis Euskirchen, Grundstücksmarktbericht 2024, Kap. 5.2.2/5.2.3:
  https://epflicht.ulb.uni-bonn.de/download/pdf/767614
- Gutachterausschuss Kreis Heinsberg, Grundstücksmarktbericht 2024, Kap. 5.2.1:
  https://epflicht.ulb.uni-bonn.de/download/pdf/767617
- Gutachterausschuss Kreis Düren, Grundstücksmarktbericht 2024, Kap. 5.2.3:
  https://epflicht.ulb.uni-bonn.de/download/pdf/767623
