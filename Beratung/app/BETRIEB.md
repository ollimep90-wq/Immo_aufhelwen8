# Betrieb: was vor dem Livegang nötig ist

Stand: 10.10.2026. Die App läuft lokal und ist getestet: 19 API-Tests und ein Browserablauf mit Zwei-Faktor-Anmeldung. Online ist sie noch nicht.

## Grundentscheidungen

- **Betreiberin ist die gemeinsame GmbH** (Name offen). Sie ist die einzige Verantwortliche im Sinne der DSGVO. Eine Vereinbarung nach Art. 26 zwischen zwei Firmen entfällt damit. Den Platzhalter `[Name GmbH, Anschrift]` im Einwilligungstext (Version `2026-10-v3`) vor dem Livegang füllen.
- **Reines Vorbereitungswerkzeug.**
  - Kommt ein Auftrag zustande, wird die gesetzliche Beratungsdokumentation außerhalb der App geführt und archiviert. Fristen siehe unten.
  - Der Widerruf löscht deshalb alle Angaben in der App.
- **Keine Gesundheitsdaten.** Die Antworten zu Block 9 „Selbstbild“ werden nicht gespeichert, der Server lehnt sie ab.
- **Zwei-Faktor-Anmeldung** (TOTP) ist für Berater und Admin Pflicht.
  - Sie wird bei der ersten Anmeldung eingerichtet. Dabei gibt es 10 Wiederherstellungscodes, jeder gilt einmal.
  - Kunden melden sich nur mit Passwort an.
- **Verschlüsselung in der App.**
  - Alle Angaben in den Akten und die 2FA-Geheimnisse liegen verschlüsselt in der Datenbank (Fernet, Schlüssel `APP_SCHLUESSEL`).
  - Der Schlüssel liegt nur in der Datei `.env` auf dem Server und in einer Offline-Kopie, nie in der Datenbank oder im Repo.
  - Damit hängt der Schutz nicht davon ab, ob der Hoster die Festplatte verschlüsselt.
  - **Geht der Schlüssel verloren, sind die Daten verloren.**

## Hosting bei IONOS

1. **Server mieten:** VPS mit Linux (Ubuntu oder Debian) und Rechenzentrum in Deutschland.
2. **AVV mit IONOS abschließen** (Art. 28 DSGVO).
   - IONOS bietet einen Auftragsverarbeitungsvertrag an, eine Fassung von 2022 ist [öffentlich einsehbar](https://vacos.de/files/cto_layout/PDFs/AVV%20IONOS%20SE_2022.pdf).
   - Die aktuelle Fassung im IONOS-Kundenkonto abschließen und ablegen.
   - *Wo genau im Kundenkonto, habe ich nicht geprüft.*
3. **Domain und DNS:** eine Subdomain wie `app.<domain>.de` auf die Server-IP zeigen lassen. Die Domain in `Caddyfile` eintragen. Caddy holt das HTTPS-Zertifikat selbst.
4. **Server einrichten:**
   ```
   apt install docker.io docker-compose-v2 ufw
   ufw allow 22,80,443/tcp && ufw enable
   git clone … && cd Beratung/app
   python3 -m server.verwaltung schluessel-erzeugen     # alternativ im Container, siehe README
   echo "APP_SCHLUESSEL=<Schlüssel>" > .env && chmod 600 .env
   docker compose up -d --build
   docker compose exec app python -m server.verwaltung admin-anlegen admin@… "Name"
   docker compose exec app python -m server.verwaltung berater-anlegen oliver@… "Oliver Rosenbaum" anlage
   docker compose exec app python -m server.verwaltung berater-anlegen jan@… "Jan Schnichels" versicherung
   ```
   - SSH nur mit Schlüssel, Passwortanmeldung abschalten.
   - Automatische Sicherheitsupdates einschalten (`unattended-upgrades`).
   - *Ungetestet:* Das Docker-Image konnte ich in der Entwicklungsumgebung nicht bauen. Beim ersten Aufsetzen den Ablauf einmal komplett durchspielen.
5. **Backup.**
   - Täglich `sqlite3 /daten/beratung.sqlite ".backup …"`. Die Datei ist inhaltlich schon verschlüsselt. Zusätzlich mit `age` verschlüsseln, falls auch Namen und E-Mails geschützt sein sollen; die sind nicht verschlüsselt.
   - Ablage an einem zweiten Ort in der EU, z. B. IONOS Object Storage in Deutschland oder ein anderer Anbieter. AVV nicht vergessen.
   - Backups nach 30 Tagen rotieren. Gelöschtes verschwindet erst dann aus den Sicherungen.
   - Die Rücksicherung einmal testen, mit Schlüssel.
6. **2FA zurücksetzen,** wenn ein Handy verloren geht: `python -m server.verwaltung 2fa-zuruecksetzen <email>`. Damit enden auch alle Sitzungen dieses Kontos.

## Fristen und Löschung

Diese Fristen beruhen auf der Prüfung vom 10.10.2026. Die Normtexte stammen aus nicht-amtlichen Fassungen, weil gesetze-im-internet.de nicht erreichbar war. Vor Verwendung am amtlichen Text prüfen.

| Fall | Frist | Grundlage | Wo |
|---|---|---|---|
| Interessent ohne Auftrag | **12 Monate nach letzter Aktivität**, dann automatische Löschung (umgesetzt, `APP_AKTEN_TAGE=365`). Aktivität ist jedes Speichern und jede Kundenanmeldung. Die Liste zeigt „Löschung am“, 30 Tage vorher gelb markiert | Keine gewerberechtliche Pflicht. DSGVO: Speicherbegrenzung (Art. 5 Abs. 1 e). Die 12 Monate sind eine Wertung, keine Vorgabe | App |
| Auftrag Finanzanlagen (§ 34h) | **10 Jahre** ab Ende des Jahres des letzten aufzeichnungspflichtigen Vorgangs. Betrifft die Kundenangaben nach § 16, die Geeignetheitserklärung, Informationsnachweise und gegebenenfalls Gesprächsaufzeichnungen nach § 18a (Telefon/Video) | §§ 22, 23 FinVermV | **außerhalb der App** archivieren, unveränderbar |
| Auftrag Darlehen (§ 34i) | Pflichtangaben **5 Jahre**. Empfehlung nach § 511 BGB aus Haftungsgründen länger (strittig, bis 10 Jahre) | § 14 ImmVermV, § 511 BGB | außerhalb |
| Auftrag Versicherung (§ 34d) | Keine gesetzliche Frist für die Beratungsdokumentation. Aufbewahrung wegen Haftung: Mandat plus bis 10 Jahre (strittig). Zahlungsaufzeichnungen 5 Jahre | §§ 61–63 VVG, § 22 VersVermV, §§ 195, 199 BGB | außerhalb |
| GwG-Unterlagen (Lebensversicherung, wohl auch § 34h) | 5 Jahre, **spätestens nach 10 Jahren löschen** | § 8 Abs. 4 GwG | getrennt |
| Rechnungen/Belege; Geschäftsbriefe | 8 Jahre; 6 Jahre | § 147 AO, § 257 HGB | Buchhaltung |

**Protokoll:** 730 Tage. **Einwilligungsnachweise gelöschter Akten:** 1.095 Tage. Beide Fristen sind Annahmen und noch festzulegen.

**Offene Entscheidung:** Wo wird die Pflichtdokumentation der Aufträge geführt? Siehe die Frage an den Nutzer im Verlauf.

## Was die Sicherheitsprüfung ergab und umgesetzt ist (10.10.2026)

- **Kundendaten in der Berateransicht:** Sie werden nur geprüft dargestellt. Der Angriff aus Befund H1 wurde im Browser getestet und ist wirkungslos.
- **Einladungen:** Nur die neueste Einladung gilt, und eine Akte mit Kunde lässt sich nicht übernehmen (H2).
- **Speichern:** Die Versionierung läuft atomar. Nach einem Widerruf lässt sich nichts mehr schreiben (M1, M2).
- **Eingaben:** NaN und zu tiefe Verschachtelung werden abgelehnt (M3), ebenso Anfragen über 512 KB.
- **Login-Bremse:** Sie normalisiert die Eingaben, begrenzt die Versuche und gilt je IP (M4).
- **Zuordnen:** Nur wer die Akte angelegt hat, oder der Admin (M5).
- **Protokolle:** Einladungs-Tokens stehen nicht mehr im Pfad, es gibt kein Zugriffsprotokoll, die Logs rotieren (M6).
- **Sitzungen:**
  - Abmeldung nach 30 Minuten ohne Aktivität.
  - Cookie `__Host-sid`.
  - 422-Antworten wiederholen die Eingaben nicht.
- **Datenbank:** `secure_delete` und ein regelmäßiger Löschlauf.

## Noch offen

- [ ] Name, Anschrift und Erlaubnisse der GmbH eintragen: Einwilligungstext, Impressum (§ 5 DDG), Datenschutzerklärung.
- [ ] **Datenschutzerklärung** schreiben. Inhalt:
  - Verantwortliche ist die GmbH.
  - Zwecke und Rechtsgrundlagen: Einwilligung für den Vorab-Check, Vertragsanbahnung für die Beratung.
  - Empfänger: IONOS als Auftragsverarbeiter.
  - Speicherdauer und Rechte der Kunden.
- [ ] **Verzeichnis der Verarbeitungstätigkeiten** (Art. 30 DSGVO) und **TOM-Beschreibung** (Art. 32 DSGVO), dazu eine kurze Schwellwertanalyse für eine Datenschutz-Folgenabschätzung.
- [ ] **Rollen intern regeln:**
  - Wer ist Admin?
  - Der Admin sieht alle Akten. Gewollt?
- [ ] **Docker-Ablauf** beim ersten Aufsetzen testen, ebenso die Rücksicherung.
