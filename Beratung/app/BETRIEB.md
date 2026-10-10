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
6. **Zwei-Faktor-Anmeldung für Berater:** noch nicht eingebaut. Für eine App mit Finanzdaten dringend empfohlen, als nächster Ausbauschritt.
7. **E-Mail:** Die App verschickt keine E-Mails. Den Einladungslink schickt der Berater selbst, am besten nicht zusammen mit sensiblen Angaben.

## Recht und Datenschutz (mit Fachleuten klären)

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
