# Betrieb: was vor dem Livegang nötig ist

Stand 10.10.2026. Die App läuft lokal und ist getestet. Online ist sie noch nicht.

## Technik

1. **Server in der EU.** Zum Beispiel ein kleiner virtueller Server bei einem deutschen Hoster mit AVV.
   - Docker und Docker Compose installieren.
   - Domain in `Caddyfile` eintragen.
   - Starten mit `docker compose up -d`. Caddy holt das HTTPS-Zertifikat selbst.
   - *Ungetestet:* Das Docker-Image konnte in der Entwicklungsumgebung nicht gebaut werden, weil dort kein Docker-Dienst lief. Beim ersten Aufsetzen einmal komplett durchspielen.
2. **Ersten Admin anlegen:**
   ```
   docker compose exec app python -m server.verwaltung admin-anlegen …
   ```
   Danach die Berater anlegen, Oliver mit `anlage`, Jan mit `versicherung`.
3. **Verschlüsselung der gespeicherten Daten.**
   - Die Datenbank liegt im Volume `daten`.
   - Der Datenträger muss verschlüsselt sein (beim Hoster wählen oder LUKS).
   - Ohne das kein Livegang.
4. **Backup.**
   - Täglich `sqlite3 /daten/beratung.sqlite ".backup …"`.
   - Verschlüsselt ablegen, zum Beispiel mit `age` oder `gpg`, an einem zweiten Ort in der EU.
   - Die Rücksicherung einmal testen.
5. **Updates:** Betriebssystem und Image monatlich aktualisieren. Die Versionen sind in `requirements.txt` festgeschrieben.
6. **Zwei-Faktor-Anmeldung für Berater:** noch nicht eingebaut. Muss vor dem Livegang eingebaut werden (siehe unten).
7. **E-Mail:** Die App verschickt keine E-Mails. Den Einladungslink schickt der Berater selbst, am besten nicht zusammen mit sensiblen Angaben.

## Entscheidungen im Code (10.10.2026)

Grundlage sind die Prüfungen vom 10.10.2026, siehe unten.

### Zweck und Löschung

- **Reines Vorbereitungswerkzeug.** Die App ist nicht die gesetzliche Beratungsdokumentation.
  - Nimmt eine Firma einen Auftrag an, übernimmt sie die Pflichtdokumentation in ihr eigenes System.
  - Bei Oliver betrifft das die Geeignetheitserklärung und die Aufzeichnungen nach § 22/23 FinVermV, die 10 Jahre aufzubewahren sind.
  - Bei Jan betrifft es die Dokumentation nach § 61 VVG.
  - Nur so bleibt das Versprechen im Einwilligungstext wahr, dass ein Widerruf alles löscht.
- **Widerruf:**
  - Er löscht alle Angaben der Akte, auch was Berater übernommen haben.
  - Danach ist die Akte für Berater gesperrt.
  - Es bleiben der Zugang (Name, E-Mail) und der Nachweis der Einwilligung.
- **Block 9 „Selbstbild“:** Die Antworten werden nicht gespeichert, weil sie Gesundheitsbezug haben (Art. 9 DSGVO). Der Block erscheint nur als Gesprächsimpuls, der Server lehnt die Felder ab.
- **Löschlauf:**
  - Er läuft bei jeder Anmeldung.
  - Abgelaufene Sitzungen sowie benutzte oder abgelaufene Einladungen werden sofort gelöscht.
  - Das Protokoll wird nach 730 Tagen gelöscht.
  - Einwilligungsnachweise gelöschter Akten werden nach 1.095 Tagen gelöscht.
  - **Beide Fristen sind Annahmen und müssen festgelegt werden** (`APP_PROTOKOLL_TAGE`, `APP_EINWILLIGUNG_TAGE`).
- **Interessentenakten ohne Auftrag** werden noch nicht automatisch gelöscht. Dafür fehlt eine festgelegte Frist (Vorschlag der Prüfung: 6 bis 12 Monate nach der letzten Änderung).

### Zugriff und Sitzungen

- **Rechte der Berater:** Berater zuordnen oder entziehen und die Akte löschen darf nur, wer die Akte angelegt hat, oder der Admin.
- **Admin:** Er sieht weiterhin alle Akten. Seine Befugnisse sind in der Vereinbarung nach Art. 26 zu regeln.
- **Sitzungen:**
  - Abmeldung nach 30 Minuten ohne Aktivität, spätestens nach 8 Stunden.
  - Das Cookie heißt `__Host-sid`.

### Sicherheitsprüfung: was umgesetzt ist

- **Kundendaten:** Sie werden in der Berateransicht nur geprüft dargestellt. Der Angriff aus Befund H1 ist im Browser getestet und wirkungslos.
- **Einladungen:** Nur die neueste Einladung gilt. Eine Akte mit Kunde lässt sich nicht übernehmen (H2).
- **Versionierung:** Sie läuft in Transaktionen. Nach einem Widerruf lässt sich nichts mehr schreiben (M1, M2).
- **Eingaben:** Ungültige Werte (NaN, zu tiefe Verschachtelung) lehnt der Server ab (M3). Anfragen über 512 KB lehnt er vor dem Einlesen ab.
- **Login-Bremse:** Sie normalisiert die Eingaben, hat eine Obergrenze und gilt je IP auch für Einladungen (M4).
  - Weiter gilt: eine Bremse pro Prozess.
  - Ein Konto lässt sich weiterhin für 10 Minuten sperren, wenn jemand gezielt 10 falsche Passwörter eingibt.
- **Einladungstoken** stehen im Body, nicht im Pfad. Das Zugriffsprotokoll ist abgeschaltet, die Logs rotieren (M6).
- **Fehlerantworten** enthalten die Eingaben nicht mehr, also auch keine Passwörter. SQLite überschreibt Gelöschtes (`secure_delete`).

## Recht und Datenschutz (mit Fachleuten klären)

- **Gemeinsame Verantwortung:** Die Prüfung hält gemeinsame Verantwortlichkeit (Art. 26 DSGVO) für sehr naheliegend: eine Akte, ein Fragebogen, ein Einwilligungstext für beide Firmen.
  - Nötig ist eine Vereinbarung nach Art. 26. Sie regelt Informationspflichten, Betroffenenanfragen, Hosting und AVV, Datenpannen, Admin-Befugnisse und Löschung.
  - Ihr Wesentliches muss den Kunden zugänglich sein.
- **Einwilligungstext:** Er nennt beide Firmen mit Anschrift; dafür stehen noch Platzhalter. Version `2026-10-v2`.
- **Zwei-Faktor-Anmeldung (TOTP)** für Berater und Admin **vor** dem Livegang einbauen. Bei Finanzdaten ist das Stand der Technik (Art. 32 DSGVO).
- **Fachlich absichern:**
  - Ab wann gilt § 22/23 FinVermV bei Honorarberatung?
  - Wie lange bewahrt Jan nach § 61/63 VVG auf?
  - Wer ist Verpflichteter nach GwG?
- **Schwellwertanalyse** für eine Datenschutz-Folgenabschätzung dokumentieren.
- **Backups** rotieren, zum Beispiel 30 Tage. Gelöschtes verschwindet erst danach aus den Sicherungen.

## Ältere Notizen

- **Verantwortung:**
  - Klären: Ist Oliver allein verantwortlich, oder seid ihr gemeinsam verantwortlich nach Art. 26 DSGVO, mit Vereinbarung?
  - Beide Firmen sehen dieselbe Akte. Das muss vertraglich geregelt sein.
- **Datenschutzerklärung und Impressum** (§ 5 DDG). In der App stehen dafür noch Platzhalter.
- **AVV mit dem Hoster** (Art. 28 DSGVO).
- **Verzeichnis der Verarbeitungstätigkeiten** (Art. 30 DSGVO).
- **Aufbewahrung gegen Löschung:**
  - Die App löscht beim Widerruf die Angaben des Kunden und beim Löschen der Akte alles.
  - Klären: Gibt es Aufbewahrungspflichten (etwa Beratungsdokumentation), die eine sperrende statt einer löschenden Lösung verlangen?
- **Speicherdauer:**
  - Festlegen, wie lange eine Akte ohne Auftrag bleibt.
  - Eine automatische Löschung ist noch nicht eingebaut.
