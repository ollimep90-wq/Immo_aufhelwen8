# Beratungskonzept — Stand

Stand: 11.10.2026. Arbeitstitel „Ganzheitliche Finanzberatung“. Der endgültige Name ist noch offen.

## Was es gibt (Privatkunden)

| Datei | Für wen | Inhalt |
|---|---|---|
| `Privat/01_Bedarfsanalyse_Privat.pdf` | intern, A4 | Gesprächsleitfaden: Ablauf in 5 Schritten, Vorab-Check, Wunschleben, Ist-Aufnahme, Risikoprofil, Ampel-Regeln, Konstrukt, Ergebnisbogen |
| `Privat/02_Kennenlernen_Unser_Weg.pdf` | Kunde | Erstgespräch: Haltung, Rollen, 5 Schritte, Haus der Finanzen, Vergütung |
| `Privat/03_Risikoabsicherung.pdf` | Kunde, präsentiert von Jan | Risiken nach Stufen, Arbeitskraft, Notreserve, Absicherungs-Check, §19 VVG |
| `Privat/04_Vermoegensaufbau.pdf` | Kunde | Ziele, Zinseszins, Anlageklassen, Strategiedepot und ETF-Standarddepot, Kosten, Verhalten |
| `Privat/05_Altersvorsorge.pdf` | Kunde | drei Säulen, Rentenlücke, Kapitalbedarf, Altersvorsorgedepot, Riester-Hinweis, bAV über Jan |
| `Privat/06_Immobilien_und_Finanzierung.pdf` | Kunde | Eigenheim und Kapitalanlage, Nebenkosten, Beispielfinanzierung, Tilgung, Ablauf, Unterlagen |

## Wie gebaut wird

- Rechenwerte stehen nur in `Privat/zahlen.py`. Die Quellen verwenden `⟦Z:key⟧`.
- Bauen: `cd Beratung/Privat && python3 build.py` für alle Dokumente, `python3 build.py alter` für ein einzelnes.
- Marke, Kontakt und Pflichtangaben kommen aus `shared/brand.py`. Die Finanzanlagen-Dokumente nutzen dieselbe Quelle.

## Annahmen in den Rechenbeispielen

Alle Werte sind gekennzeichnet und gelten als Beispiel, nicht als Prognose.

- **Rendite:** 6 % vor Kosten, Kosten 1,3 %, Inflation 2 %. Die Entnahmephase rechnet real mit 1 %.
- **Rentenlücke:** 3.000 € netto, Ziel 80 %. Die gesetzliche Rente von 1.300 € netto ist eine Annahme.
- **Finanzierung:**
  - Kaufpreis 450.000 €, Nebenkosten NRW 12,07 %.
  - Die Nebenkosten setzen sich zusammen aus Grunderwerbsteuer 6,5 %, Makler 3,57 % und Notar/Grundbuch rund 2 % (Erfahrungswert).
  - Darlehen 400.000 € zu 3,8 % Zins und 2 % Tilgung.
- **Kapitalanlage:** Kaufpreis 300.000 €, Kaltmiete 1.250 €.

## Offen

1. **Excel-Prototyp:** am 10.10.2026 erhalten und ausgewertet, siehe `Prototyp_Analyse.md`. Budgetlogik und Risiko-Check sind in der Bedarfsanalyse übernommen (S. 7 und 9). Der Vorab-Check ist offen, siehe Punkt 2.
2. **Vorab-Check:** Das Formular ist gebaut (`Privat/07_Vorab-Check.html`, Quellen in `Privat/vorab-check/`). Vor dem Livegang fehlen noch:
   - Empfangsdienst für die Übermittlung (`VERSAND.url`) und ein AVV mit diesem Dienst.
   - Datenschutzerklärung und Impressum.
   - ~~Hosting.~~ *Erledigt 10.10.2026:* IONOS (siehe `app/BETRIEB.md`).
   - Rechtliche Prüfung der Einwilligung.
   - ~~Wer ist verantwortlich?~~ *Erledigt 10.10.2026:* die gemeinsame GmbH, siehe Punkt 15.
   - ~~Speicherdauer.~~ *Erledigt 10.10.2026:* 12 Monate nach der letzten Aktivität (in der App umgesetzt).
   - ~~Nachweis der Einwilligung auf dem Server.~~ *Erledigt:* in der App umgesetzt.
   - **Zu entscheiden:** Wird das eigenständige Formular `07_Vorab-Check.html` noch gebraucht, oder ersetzt der Kundenbereich der App es? Dann entfallen auch der Empfangsdienst und der zugehörige AVV.
   - Verzeichnis der Verarbeitungstätigkeiten.
   - Impressum nach § 5 DDG.

   Bewusst umgesetzt:
   - Die Kirchensteuer wird nur im Browser verwendet und nicht übertragen.
   - Keine Fragen zur eigenen Gesundheit. Freitext mit Bitte, keine Gesundheitsangaben zu machen.
   - Keine Webfonts, keine Cookies, kein lokaler Speicher.
   - Der Live-Build bricht ab, solange Platzhalter offen sind (`python3 build.py --live URL DS`).
   - Mit Jan zu klären: Gewichtung der Themen im Kurzcheck, vor allem Unfall.
3. Den gleichen Satz für **Gewerbe und Unternehmen** erstellen.
4. ~~**§34i-Modell wählen:** Provision oder Honorar.~~ *Entschieden 11.10.2026: Provision.* Die Platzhalter in Decks und Pflichtangaben sind ersetzt („eine Provision von der Bank, die dir das Darlehen gibt“; Pflichtangabe: „eine Provision des Darlehensgebers“). Die Höhe wird vorab genannt. Bisheriger Stand zur Nachverfolgung:
   - Nach § 34i Abs. 5 GewO schließen sich Vermittlung und Honorarberatung aus, eine Wahl je Kunde ist nicht möglich.
   - *Korrektur 10.10.2026:* Die Decks sagten vorher „Provision der Bank oder, als Honorarberater, ein Honorar von dir, nie beides“. Das klang wie eine Wahl je Kunde und war deshalb falsch.
   - Jetzt steht dort der gelbe Platzhalter „[eine Provision der Bank]“, bis du entschieden hast.
5. **Platzhalter:** Register-Nummern, IHK, Kontaktdaten.
6. **Name und Marke.**
7. **DIN 77230:** Der Normtext lag nicht vor. Die Dokumente sagen deshalb „angelehnt“ und behaupten keine Konformität.
8. **Alte Sie-Fassungen:** Kundenpräsentation und Gesprächsleitfaden in `Finanzanlagen/` sind teilweise durch die neuen Decks ersetzt. Seit 11.10.2026 gibt es zu den Privat-Decks 01–06 eigene `_Sie`-Fassungen (Punkt 16, „Anrede du/Sie“). Zu entscheiden: Können die alten Sie-Fassungen archiviert werden?
9. **Jans Rückmeldung** zu `03_Risikoabsicherung` und zu seiner Rolle in den anderen Decks.
10. **Masterarbeit:** Die Kapitel 3–7 sind noch „XXX“, Anhang A ist leer, und das Literaturverzeichnis enthält fremde Einträge (RFID, Industrie 4.0). Das ist für die Arbeit selbst wichtig, nicht für die Decks.
11. **Vor Kundeneinsatz anwaltlich klären** (Fachanwalt Bank- und Kapitalmarktrecht):
    - **§ 17 PAngV** bei den Zinsbeispielen in `06_Immobilien`. Effektivzins, Nettodarlehensbetrag und der Hinweis auf die Grundschuld sind ergänzt. Ob ein repräsentatives Beispiel nötig ist, ist offen.
    - **§ 34h Abs. 3 GewO:** Entgeltfluss beim Strategiedepot mit WealthKonzept und Erlaubnisumfang für die Vermittlung der Vermögensverwaltung.
12. **Altersvorsorgedepot, noch an Primärquellen prüfen:**
    - Stichtag für den Bonus von 200 €.
    - Teilkapital 30 %.
    - Verrechnung der Kinderzulage.
    - Mindesteigenbeitrag (laut Prüfung 120 €/Jahr, nicht übernommen).
    - Umstellung der Riester-Verträge (Fundstelle im EStG n. F.).
    - Förderberechtigung Selbständiger.
13. **USt beim ETF-Standarddepot:** „jeweils inkl. USt“ wurde am 10.10.2026 aus dem Pflichthinweis entfernt, weil es für die 0,5 % noch offen ist.
15. **Gemeinsame GmbH (Entscheidung 10.10.2026, Name offen):**
    - Sie betreibt die App und ist die einzige Verantwortliche nach DSGVO.
    - **Anzupassen**, sobald Name und Erlaubnisse feststehen:
      - Pflichtangaben in `shared/brand.py`, denn die GmbH braucht eigene Erlaubnisse und Registernummern.
      - Die Texte „zwei eigenständige Unternehmen in Kooperation“ in den Präsentationen und Fußzeilen.
      - Der Platzhalter `[Name GmbH]` in den Einwilligungen.
    - **Fachlich prüfen:** Gehen § 34h, § 34i und § 34d zusammen in einer GmbH? Ist Courtage mit § 34h Abs. 3 vereinbar?
    - **GwG (Entscheidung 11.10.2026: als Verpflichtete behandeln):**
      - Pflichten, Grenzen und offene Fragen stehen in `GWG.md`.
      - In der App gibt es dafür den Reiter „Geldwäsche“ als Checkliste. Die Nachweise selbst kommen ins Archiv.
16. **Beratungs-App** (`app/`):
    - Gebaut: Zwei-Faktor-Anmeldung, Verschlüsselung, Löschung nach 12 Monaten ohne Aktivität, Archivauszug.
    - Hosting bei IONOS, offene Punkte in `app/BETRIEB.md`.
    - **Kundenbericht „Dein Finanzbericht“:** Die Außenwirkung wurde am 11.10.2026 geprüft, die Befunde sind eingearbeitet.
      - *Korrektur:* Vorher stand dort „Gewünscht sind … €“. Der Betrag ist aber eine Annahme (80 % vom Netto), nicht der Wunsch des Kunden. Jetzt heißt es „Als Ziel rechnen wir mit …“, und die Annahme wird genannt.
      - *Korrektur:* Fehlte die Angabe zur Notreserve, zeigte der Bericht „0 Monate“. Jetzt entfällt der Abschnitt.
      - *Korrektur:* Bei einem negativen Überschuss stand dort „bleiben −250 € frei“. Jetzt heißt es „fehlen im Monat rund 250 €“.
      - *Korrektur:* Aktenvermerke wie „Kunde lehnt ab“ erschienen beim Kunden. Jetzt steht dort Kundensprache, z. B. „möchtest du nicht“.
      - Die Sparrate berücksichtigt bereits Angespartes. Das ist jetzt als eigene Kachel ausgewiesen.
      - Alle Annahmen der Rentenrechnung stehen in der Fußnote.
      - Der Pflichthinweis ist ohne Fachbegriffe formuliert und erwähnt die Versicherungseinschätzung.
      - Statt „deines Versicherungsmaklers“ stand dort zwischenzeitlich der Name des Ansprechpartners. *Erledigt 11.10.2026:* Oliver hat bestätigt, dass Jan Versicherungsmakler ist (siehe unten).
      - **Netto-Rente (11.10.2026):** Die App rechnet die gesetzliche Rente selbst von brutto (Renteninformation) auf netto um. Grundlage sind Kranken- und Pflegeversicherung der Rentner, der Besteuerungsanteil nach Rentenbeginn und der Tarif 2026. Die Regeln stehen in `Privat/vorab-check/QUELLEN.md`. *Erledigt:* Die Rechtsprüfung vom 11.10.2026 hat alle Werte bestätigt.
        - *Korrektur:* Vorher ging der Bruttobetrag des Kunden ungeprüft als netto in die Rechnung. Beispiel Lena: Die Lücke war mit 2.038 € zu klein. Richtig sind rund 2.260 €, weil von 1.500 € brutto rund 1.278 € netto bleiben.
      - Jan und Oliver sind Versicherungsmakler (§ 34d Abs. 1, Angabe Oliver 11.10.2026). Die Versicherungsthemen liegen trotzdem bei Jan: Nur der Bereich Versicherung bewertet die Absicherung, und der Bericht nennt ihn als „deinen Versicherungsmakler“ mit Namen.
      - **Vorzeitige Rente (11.10.2026):** Die App rechnet mit beiden Werten der Renteninformation fehlende Beitragsjahre und den Abschlag (§ 77 SGB VI) heraus.
      - **Weitere Einkünfte (11.10.2026):** neuer Tab mit 6 Einträgen.
        - Arten: Vermietung (pauschal oder EÜR), Kapitalerträge mit Günstigerprüfung, Betriebsrente, private Rente, Sonstiges.
        - Fremdwährung mit EZB-Tageskurs.
        - Die Einkünfte wirken heute aufs Netto und Budget, im Alter auf die Rentenlücke (Person 1). Quellen und Grenzen stehen in `Privat/vorab-check/QUELLEN.md`.
        - *Korrektur:* Vorher hieß es in der Rentenrechnung „keine weiteren Einkünfte im Alter“, und Betriebsrenten fehlten ganz.
      - *Fehler behoben:* Auf langen Seiten ging der erste Klick auf „Speichern“ direkt nach einer Eingabe ins Leere, weil die Leiste beim Fokuswechsel sprang.
      - **Ganzer Haushalt im Alter (Entscheidung Oliver, 11.10.2026):**
        - Gerechnet werden beide Renten, jeweils auch mit vorzeitigem Beginn, und alle weiteren Einkünfte beider Personen. Ehepaare werden mit Splitting zusammen veranlagt.
        - Das Ziel bezieht sich auf das Haushaltsnetto heute, also Lohn und weitere Einkünfte ohne Kindergeld.
        - Die Sparzeit läuft bis zum ersten Rentenbeginn.
        - *Korrektur:* Vorher wurde nur Person 1 gerechnet und das Ziel aus ihrem Netto abgeleitet. Bei Paaren war die Lücke dadurch nicht vergleichbar.
      - **Kundenbericht:**
        - Farbiger gestaltet: Kopfband, Farbmarken je Abschnitt, getönte Kacheln, nummerierte nächste Schritte.
        - Hell oder dunkel wählbar, auch als PDF. Das dunkle PDF hat keinen weißen Rand.
        - Die dunklen Diagrammfarben sind mit dem Palette-Validator geprüft.
      - **Kundenbericht als Geschichte (11.10.2026):**
        - Aufbau: „Auf einen Blick“, dann die drei Kapitel „Wo du stehst“, „Wo du hinwillst“ (mit Vision Board) und „Wie du dahin kommst“ (mit Weg).
        - Paare werden mit „ihr“ angesprochen.
        - Die Außenwirkung ist geprüft.
        - *Korrektur:* Ein Punkt „Jeden Monat X € zurücklegen“ im Weg wirkte wie eine Sparempfehlung und ist entfernt.
      - **Kontoauszüge einlesen (11.10.2026):**
        - Formate: CSV, CAMT (XML) und PDF.
        - Alles läuft nur im Browser, gespeichert werden nur übernommene Monatssummen.
        - Angebrochene Monate zählen nicht mit.
        - *Fehler behoben:* Der Dateiname wäre beim Speichern mitgeschickt worden.
      - **Direkte Kontoanbindung:** Konzept und offene Rechtsfragen in `app/KONTOANBINDUNG.md`. Noch nicht gebaut, weil zuerst die Rechtslage geklärt werden muss.
      - **Anrede du/Sie (Entscheidung Oliver, 11.10.2026: Schalter in Decks und App):**
        - Decks: Zu den Privat-Dokumenten 01–06 gibt es je eine `_Sie`-Fassung (Dateiname mit `_Sie`). `07_Vorab-Check.html` gibt es nur in der du-Form; ob es noch gebraucht wird, ist offen (Punkt 2). Die Sätze stehen in `shared/sie.json`, der Build bricht bei du-Resten ab.
        - App: Der Berater stellt die Anrede je Akte unter „Zugang & Daten“ ein. Standard ist du, Paare werden mit „ihr“ angesprochen, „Sie“ gilt für alle.
        - Der Kundenbereich wechselt dann auf `kunde_sie.html`, und neue Berichte erscheinen in der Sie-Form. Bereits freigegebene Berichte bleiben, wie sie sind. Freitexte prüft der Berater selbst, die App weist auf du-Formen hin.
        - Die Einstellung bleibt nach einem Widerruf erhalten, weil sie keine Angabe des Kunden ist. In der Selbstauskunft steht sie getrennt unter „einstellungen_berater“. Nach einem Widerruf ist sie nicht mehr änderbar.
        - Geprüft am 11.10.2026: API-Test und Browsertest aller Schritte, ohne du-Reste.
    - **Klick-Demo** ohne Server, mit erfundenen Daten: `app/demo/`. Die Akte „Tom Beispiel“ steht dort auf Sie.
14. **Gemeinsamer Auftritt:**
    - Die Namen sind aus der Unterzeile entfernt, die Fußzeilen lauten „… in Kooperation mit …“.
    - Die gemeinsame Marke bleibt. Klären: Risiko einer Außen-GbR (siehe Pitch).
