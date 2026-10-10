# Beratungs-App (Privatkunden)

Eine Web-App für Kunden und Berater. Sie ersetzt den Excel-Prototyp und läuft auf Laptop und Tablet. Auf dem Tablet lässt sie sich über „Zum Home-Bildschirm“ wie eine App ablegen.

| Bereich | Wer | Was |
|---|---|---|
| `kunde.html` | Kunde (per Einladungslink) | Finanz-Check in du-Form. Speichert nach jedem Schritt, aber nur mit Einwilligung. Widerruf und Selbstauskunft möglich |
| `berater.html` | Oliver, Jan | Kundenakten mit sieben Arbeitsbereichen, siehe unten |
| Server | – | Python/FastAPI, SQLite. Rollen und Rechte: siehe `server/app.py` (Kopfkommentar) |

Die sieben Arbeitsbereiche einer Kundenakte:

1. Überblick
2. Haushalt & Netto
3. Budget
4. Vermögen & Vorsorge
5. Risiko-Check: 79 Fragen, davon 78 aus dem Prototyp
6. Absicherung: Nur Jan kann sie schreiben.
7. Ziele & Notizen

Dazu kommt der Bereich Zugang & Daten.

## Rechte

- **Kunde:** sieht nur die eigene Akte und schreibt nur seinen Finanz-Check.
- **Berater:** sieht nur Akten, denen er zugeordnet ist.
  - Die Bewertung der Absicherung schreibt nur der Bereich `versicherung` (§ 34d GewO).
  - Die Angaben des Kunden ändert kein Berater.
- **Admin:** legt Berater an und sieht alle Akten.

## Lokal starten

```
cd Beratung/app
pip install -r requirements-dev.txt
python3 tools/sync.py          # Rechenkern/Fragen aus Privat/vorab-check übernehmen
python3 tools/baue_kunde.py    # Kundenbereich aus dem Vorab-Check erzeugen
APP_DB=dev.sqlite python3 -m server.verwaltung berater-anlegen oliver@… "Oliver Rosenbaum" anlage
APP_DB=dev.sqlite APP_UNSICHER=1 python3 -m uvicorn server.app:app --port 8000
```

`APP_UNSICHER=1` erlaubt das Sitzungs-Cookie ohne HTTPS. Das ist **nur lokal** zulässig.

## Tests

```
python3 -m pytest -q tests                        # API, Rechte, Rentenlücke gegen zahlen.py
python3 ../Privat/vorab-check/test_rechenkern.py  # Netto-Rechnung JS gegen Python
```

Den Ablauf im Browser (Einladung, Einwilligung, Finanz-Check, Übernahme, Risiko-Check, Bewertung durch Jan) habe ich am 10.10.2026 mit Playwright geprüft. Das Testskript liegt nicht im Repo.

## Eine Quelle für Rechnungen und Fragen

- **Netto, Budget, Risiko-Wertung:** `Privat/vorab-check/rechenkern.js`, kopiert über `tools/sync.py`.
- **Kurzcheck-Fragen:** `Privat/vorab-check/fragen.js`.
- **Voller Fragenkatalog:** `data/fragen_voll.json`, erzeugt mit `tools/export_fragen.py` aus dem Excel-Prototyp.
- **Rentenlücke:** `web/js/vorsorge.js`, gleiche Formeln wie `Privat/zahlen.py`, per Test abgesichert.
