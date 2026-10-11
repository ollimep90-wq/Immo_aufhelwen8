# Kontoanbindung: Konzept für später

Stand: 11.10.2026. Grundlage ist eine Prüfung mit dem Prüfagenten für Recht und Förderung.
- gesetze-im-internet.de war nicht erreichbar. Nur § 36 ZAG und der Stand von PSD3/PSR und FIDA sind live geprüft.
- Alles mit **[G]** ist Wissen ohne Live-Beleg. Vor einer Entscheidung am amtlichen Text prüfen.

## Was heute schon geht (umgesetzt)

Kunden lesen im Finanz-Check ihre Kontoauszüge selbst ein, als CSV, CAMT (XML) oder PDF.
- Die Auswertung läuft nur im Browser. Am 11.10.2026 per Netzwerk-Mitschnitt geprüft: Beim Einlesen geht keine Anfrage an den Server.
- Gespeichert werden nur die Monatssummen, die der Kunde übernimmt. Buchungen, Empfängernamen und Dateinamen werden nicht gespeichert.
- Damit landen auch keine Buchungen mit Gesundheits-, Kirchen- oder Gewerkschaftsbezug bei uns (Art. 9 DSGVO).

## Direkte Anbindung an das Konto

### Rechtlicher Rahmen

| Punkt | Ergebnis |
|---|---|
| Was ist das? | Ein **Kontoinformationsdienst** (§ 1 Abs. 34 ZAG) [G]. Das gilt unabhängig von der Technik: PSD2-Schnittstelle, FinTS oder Screen-Scraping. |
| Selbst anbieten | Nur mit **Registrierung bei der BaFin** (§ 34 ZAG [G]) und **Berufshaftpflicht** nach **§ 36 ZAG** (geprüft). Die Erlaubnisse nach § 34d/h/i GewO genügen nicht [G]. |
| Über einen Dienstleister | Üblich ist: Ein registrierter Kontoinformationsdienst holt die Daten, der Kunde stimmt bei ihm zu. **Offen:** Erbringt die GmbH dann trotzdem selbst einen Kontoinformationsdienst? Das hängt vom Vertrag ab und sollte ein Fachanwalt für Aufsichtsrecht klären. |
| Freigabe durch den Kunden | Starke Kundenauthentifizierung bei der Bank, danach mindestens alle **180 Tage** erneut (DelVO (EU) 2022/2360, seit 25.07.2023 [G]). Ohne den Kunden höchstens 4 Abrufe pro Tag [G]. |
| FinTS mit PIN in der App | **Nicht weiterverfolgen.** Ohne Registrierung ist das ein Verstoß gegen das ZAG (strafbewehrt [G]). Die Bankbedingungen verbieten die Weitergabe der Zugangsdaten [G]. Den Kunden droht volle Haftung bei Missbrauch (§ 675v Abs. 3 BGB [G]). |
| Datenschutz | Umsätze können Art.-9-Daten enthalten (EDPB-Leitlinien 06/2020). Dafür braucht es eine **ausdrückliche Einwilligung** (Art. 9 Abs. 2 lit. a) oder eine Filterung. Besser ist, dass schon der Dienstleister zu Kategorien zusammenfasst. Der Dienstleister ist meist **eigener Verantwortlicher**; ein Vertrag zur Auftragsverarbeitung passt nur für Zusatzleistungen. **Offen**, mit Datenschutzanwalt klären. |
| Neue EU-Regeln | PSD3/PSR: politische Einigung am 27.11.2025, wirksam frühestens etwa 2028, mit einem Berechtigungs-Dashboard für Kunden. FIDA: Verhandlungen stocken, für die Planung kein Faktor. |

### Mögliche Dienstleister (Stand und Zulassung selbst prüfen)

| Anbieter | Einschätzung |
|---|---|
| finAPI GmbH, München | BaFin-Zahlungsinstitut, auch für Kontoinformationsdienste [G] |
| Tink (Tink AB, Schweden; Tink Germany GmbH) | lizenziert und nach Deutschland gemeldet [G] |
| GoCardless Bank Account Data (vorher Nordigen) | Laut mehreren Quellen seit Juli 2025 keine Neuanmeldungen. Vermutlich nicht verfügbar. |

Prüfweg:
- BaFin-Unternehmensdatenbank und EBA-Register (PSD2).
- Zulassung und Datenfluss beim Anbieter schriftlich bestätigen lassen.
- Kosten je Verbindung beim Anbieter erfragen. Sie sind hier nicht bekannt.

### Vorschlag für den Ablauf

1. Der Kunde tippt im Finanz-Check auf „Konto verbinden“ und wird zum Dienstleister weitergeleitet. Dort wählt er seine Bank und gibt bei der Bank frei.
2. Der Dienstleister liefert die Umsätze der letzten Monate. Am besten liefert er sie gleich nach Kategorien zusammengefasst.
3. Die App zeigt dieselbe Prüfansicht wie beim Datei-Import. Der Kunde ordnet bei Bedarf neu zu und übernimmt.
4. Gespeichert werden nur die Monatssummen. Die Freigabe läuft nach 180 Tagen ab. Bei einer neuen Beratung gibt der Kunde wieder frei.

### Vor einer Entscheidung klären

1. Aufbau mit dem Dienstleister und Pflichten der GmbH: Fachanwalt Bank- und Aufsichtsrecht, gegebenenfalls Anfrage bei der BaFin.
2. Registerstatus und Preise von finAPI und Tink.
3. Datenschutz: Rollen, Art.-9-Konzept, Einwilligungstext. Zuständig sind Datenschutzanwalt oder Datenschutzbeauftragter.
4. Zeitplan von PSD3/PSR im Amtsblatt prüfen.
