# Ankaufsprofile

Fünf einseitige Ankaufsprofile für Makler, Insolvenz- und Zwangsverwalter
und Bankenverwertung. Alle fünf entstehen aus einer Vorlage und einer
Datendatei.

| Datei in `out/` | Empfänger |
|---|---|
| `Ankaufsprofil_Aachen-Koeln-Bonn-Nordeifel.pdf` | Makler in NRW |
| `Ankaufsprofil_Region-Hannover.pdf` | Makler in der Region Hannover |
| `Ankaufsprofil_Muenchen-Nord.pdf` | Makler im Raum München |
| `Ankaufsprofil_Hamburg-Nord.pdf` | Makler im Raum Hamburg |
| `Ankaufsprofil_Uebersicht.pdf` | **nur** bundesweite Verwerter (Insolvenz-/Zwangsverwalter, Banken) |

Lokale Makler bekommen nur ihr Regionalprofil. Vier Regionen auf einem Blatt
wirken auf sie wie ein Objektsammler.

## Aufbau

- `profile.json`: **einzige Quelle für alle Inhalte**, die je Profil wechseln
  (Region, Einleitung, Standorte), dazu die gemeinsamen Felder (Datum, E-Mail,
  „Über mich", eigener Bestand).
- `vorlage.html`: Layout und Text, der in allen Profilen gleich ist.
- `build.py`: erzeugt HTML und PDF nach `out/`. Bricht ab, sobald ein Profil
  nicht mehr auf eine Seite passt.
- `render.js`: druckt das HTML mit Chromium (Playwright) als PDF.

Bauen:

```
python3 ankaufsprofil/build.py
```

Inhalte werden nur in `profile.json` oder `vorlage.html` geändert, nie im PDF
und nie in `out/*.html`. Danach neu bauen.

## Vor dem Versand

1. `gemeinsam.email` in `profile.json` eintragen (noch offen).
2. `gemeinsam.stand` auf den Versandmonat setzen.
3. Erst **nach dem Notartermin Auf Helwen 8** versenden.
4. `gemeinsam.eigener_bestand` erst **nach Übergabe und unterschriebenem
   Mietvertrag mit Indexmiete** setzen: „Eigener Bestand: ein Mehrfamilienhaus
   in der Nordeifel."
5. Den `aussenwirkung-pruefer` laufen lassen.
6. Die eigenen Online-Profile (LinkedIn/XING) abgleichen. Makler googeln den
   Namen. Arbeitgeber und Finanzberatertätigkeit sollen dort nicht den
   Eindruck eines Vermittlers erzeugen.

## Entscheidungen (Stand 09.10.2026, eigene Angaben des Nutzers)

- MFH ab 4 WE und ab ca. 300 m² Wfl., auch Wohn- und Geschäftshäuser mit
  überwiegendem Wohnanteil.
- Light Industrial ab ca. 500 m² Nutzfläche, keine reinen Büros. Etwas
  Büroanteil ist in Ordnung. **Die 500 m² sind ein Vorschlag, noch nicht
  ausdrücklich bestätigt.**
- Nahversorgung: Supermärkte ab ca. 1.200 m² Verkaufsfläche. **Fachmärkte:
  Entscheidung offen.**
- Nicht gesucht (Nutzer, 09.10.2026): reine Büroimmobilien, Erbbaurecht, einzelne
  Eigentumswohnungen, Neubau- und Projektentwicklungen, unbebaute Grundstücke.
- Kein Kaufpreisfaktor, kein Volumen, keine Zusage zur Käuferprovision.
- „Verbindliche Rückmeldung", „Core+ / Value-Add" und „Mietniveau unter Markt"
  bleiben drin.
- Kein „im eigenen Namen", weil der Kauf auch über die vermögensverwaltende
  Gesellschaft möglich sein soll.
- Regionen:
  - NRW: Städteregion Aachen, Köln, Bonn, Kreise Euskirchen, Düren, Heinsberg,
    Rhein-Erft, Rhein-Sieg. Keine Eifelkreise aus Rheinland-Pfalz.
  - Region Hannover: alle Objektarten. Intern gilt beim Wohnen eine engere
    Auswahl.
  - München und Hamburg: Wohnen eng um den Norden, Light Industrial und
    Nahversorgung im nördlichen Großraum. **Die Übersetzung in Ortsangaben
    ist noch zu bestätigen.**
- Bevölkerungsfilter nur als „bevorzugt". Geprüft ist er bisher nur für NRW
  (siehe `notizen/`). Für Hannover, München und Hamburg steht die Prüfung noch
  aus.
- „Über mich“: M.Sc. Finance, Accounting & Taxation laut Urkunde (13.02.2026); Abschluss als Wirtschaftsingenieur vom Nutzer bestätigt (eigene Angabe). Zeugnisse liegen nicht im Repo.
- Farben aus dem eigenen Logo (#006837 / #95CE24), das Logo selbst nicht im
  Profil.

## Notizen und Analyse

- `notizen/Demografie-Check-Ankaufsregion.md`: IT.NRW-Prognose 2024–2050
  und Rheinland-Pfalz, Vertiefung zur Stadt Aachen.
- `notizen/Marktcheck-Wanderung-und-Kaufpreisfaktoren.md`: tatsächliche
  Wanderung 2018–2024 und Rohertragsfaktoren der Gutachterausschüsse. Vom
  `zahlen-pruefer` nachgerechnet, Korrekturen sind im Text markiert.
- `analyse/parse_kp.py`, `analyse/kp.json`: Auswertung der IT.NRW-Kommunalprofile.
  Die Quell-PDFs sind nicht eingecheckt, ihre Links stehen in der Notiz.
