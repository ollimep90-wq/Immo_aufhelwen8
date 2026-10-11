"""Kontoauszug-Import (web/js/kontoauszug.js) mit nachgebauten Exporten typischer Banken.
Die Beispieldaten sind erfunden und nur im Aufbau den Exporten nachempfunden (Spaltennamen, Trenner, Vorspann)."""
import json, pathlib, subprocess

JS = pathlib.Path(__file__).resolve().parent.parent / "web/js/kontoauszug.js"


def node(code):
    return json.loads(subprocess.check_output(["node", "-e", f"const K=require({json.dumps(str(JS))});{code}"]))


def csv(text, enc="utf-8"):
    b = list(text.encode(enc))
    return node(f"console.log(JSON.stringify(K.leseCSV(K.dekodiere(new Uint8Array({json.dumps(b)}).buffer))))")


SPARKASSE = '''"Auftragskonto";"Buchungstag";"Valutadatum";"Buchungstext";"Verwendungszweck";"Beguenstigter/Zahlungspflichtiger";"Kontonummer/IBAN";"Betrag";"Waehrung"
"DE00";"01.10.26";"01.10.26";"GUTSCHR. UEBERWEISUNG";"Gehalt 10/2026";"Muster GmbH";"DE11";"3.210,55";"EUR"
"DE00";"02.10.26";"02.10.26";"FOLGELASTSCHRIFT";"Miete Oktober";"Hausverwaltung Nord";"DE22";"-1.250,00";"EUR"
"DE00";"05.10.26";"05.10.26";"KARTENZAHLUNG";"REWE SAGT DANKE";"REWE Markt GmbH";"";"-84,37";"EUR"
'''
ING = '''Umsatzanzeige;Datei erstellt am: 11.10.2026 10:00
;Letztes Update: aktuell

IBAN;DE00 0000
Kontoname;Girokonto

Buchung;Valuta;Auftraggeber/Empfänger;Buchungstext;Verwendungszweck;Saldo;Währung;Betrag;Währung
03.10.2026;03.10.2026;Vodafone GmbH;Lastschrift;Kundennr 123;1.000,00;EUR;-39,99;EUR
04.10.2026;04.10.2026;Familienkasse;Gutschrift;Kindergeld;1.259,00;EUR;259,00;EUR
'''
DKB = '''"Konto";"Girokonto DE00"
""
"Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";"Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"IBAN";"Betrag (€)"
"06.10.26";"06.10.26";"Gebucht";"Lena Muster";"HUK-COBURG";"Beitrag Kfz";"Ausgang";"DE33";"-58,20"
"07.10.26";"07.10.26";"Gebucht";"Muster GmbH";"Lena Muster";"Lohn";"Eingang";"DE44";"2.100,00"
'''
COMDIRECT = '''"Umsätze Girokonto";"Zeitraum: 30 Tage";
"Buchungstag";"Wertstellung (Valuta)";"Vorgang";"Buchungstext";"Umsatz in EUR";
"08.10.2026";"08.10.2026";"Lastschrift / Belastung";"Auftraggeber: Netflix International Buchungstext: Abo";"-13,99";
'''
VOLKSBANK = '''Buchungstag;Valuta;Auftraggeber/Zahlungsempfänger;Vorgang/Verwendungszweck;Währung;Umsatz;Soll/Haben
09.10.2026;09.10.2026;Stadtwerke Bonn;Abschlag Strom;EUR;95,00;S
10.10.2026;10.10.2026;Arbeitgeber AG;Gehalt;EUR;1.500,00;H
'''
CAMT = '''<?xml version="1.0"?><Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"><BkToCstmrStmt><Stmt>
<Ntry><Amt Ccy="EUR">45.90</Amt><CdtDbtInd>DBIT</CdtDbtInd><BookgDt><Dt>2026-10-02</Dt></BookgDt>
<NtryDtls><TxDtls><RltdPties><Dbtr><Nm>Lena Muster</Nm></Dbtr><Cdtr><Nm>Telekom Deutschland</Nm></Cdtr></RltdPties>
<RmtInf><Ustrd>Rechnung 10/2026</Ustrd></RmtInf></TxDtls></NtryDtls></Ntry>
<Ntry><Amt Ccy="EUR">3000.00</Amt><CdtDbtInd>CRDT</CdtDbtInd><BookgDt><Dt>2026-10-01</Dt></BookgDt>
<NtryDtls><TxDtls><RltdPties><Dbtr><Nm>Muster GmbH &amp; Co. KG</Nm></Dbtr></RltdPties><RmtInf><Ustrd>Gehalt</Ustrd></RmtInf></TxDtls></NtryDtls></Ntry>
</Stmt></BkToCstmrStmt></Document>'''


def test_sparkasse():
    r = csv(SPARKASSE, "windows-1252")
    assert [x["betrag"] for x in r] == [3210.55, -1250, -84.37]
    assert r[1]["name"] == "Hausverwaltung Nord" and r[0]["datum"] == "2026-10-01"
    # Verwendungszweck hat Vorrang vor der Buchungsart, beide stehen im Zweck (Fehler im Browsertest 11.10.2026)
    assert r[0]["zweck"].startswith("Gehalt 10/2026") and "GUTSCHR" in r[0]["zweck"]


def test_ing_mit_vorspann():
    r = csv(ING)
    assert [(x["name"], x["betrag"]) for x in r] == [("Vodafone GmbH", -39.99), ("Familienkasse", 259.0)]


def test_dkb_zahler_und_empfaenger():
    r = csv(DKB)
    assert r[0]["name"] == "HUK-COBURG" and r[0]["betrag"] == -58.2     # Ausgabe: Empfänger
    assert r[1]["name"] == "Muster GmbH" and r[1]["betrag"] == 2100      # Eingang: Zahler


def test_comdirect_und_volksbank_soll_haben():
    assert csv(COMDIRECT)[0]["betrag"] == -13.99
    r = csv(VOLKSBANK)
    assert [x["betrag"] for x in r] == [-95, 1500]


def test_camt():
    r = node(f"console.log(JSON.stringify(K.leseCAMT({json.dumps(CAMT)})))")
    assert r[0] == {"datum": "2026-10-02", "betrag": -45.9, "name": "Telekom Deutschland", "zweck": "Rechnung 10/2026"}
    assert r[1]["betrag"] == 3000 and r[1]["name"] == "Muster GmbH & Co. KG"


def test_pdf_zeilen():
    zeilen = ["Kontoauszug 10/2026 Seite 1", "Alter Kontostand 1.000,00", "01.10.2026 01.10.2026 Lastschrift Allianz Versicherung -45,90",
              "Beitrag Hausrat 2026", "02.10.2026 Gutschrift Muster GmbH 2.500,00 +", "Gehalt Oktober", "03.10.2026 Kartenzahlung EDEKA 23,10",
              "Neuer Kontostand 3.431,00"]
    r = node(f"console.log(JSON.stringify(K.lesePDFZeilen({json.dumps(zeilen)})))")
    assert [(x["betrag"], x.get("unsicher")) for x in r] == [(-45.9, False), (2500, False), (-23.1, True)]
    assert "Hausrat" in r[0]["zweck"]


def test_auswertung_und_zuordnung():
    buch = [dict(datum="2026-07-01", betrag=-1200, name="Hausverwaltung", zweck="Miete"),
            dict(datum="2026-08-01", betrag=-1200, name="Hausverwaltung", zweck="Miete"),
            dict(datum="2026-09-01", betrag=-1200, name="Hausverwaltung", zweck="Miete"),
            dict(datum="2026-09-30", betrag=-300, name="REWE", zweck=""),
            dict(datum="2026-09-30", betrag=-300, name="REWE", zweck=""),          # doppelt (zweite Datei) → zählt einmal
            dict(datum="2026-08-15", betrag=-90, name="Max Bauer", zweck="Geschenk"),
            dict(datum="2026-07-01", betrag=3000, name="Muster GmbH", zweck="Gehalt")]
    a = node(f"console.log(JSON.stringify(K.auswerten({json.dumps(buch)})))")
    assert a["anzahl"] == 6 and a["monate"] == 3
    assert a["monat"]["wohnen"] == 1200 and a["monat"]["essen"] == 100 and a["monat"]["sonst"] == 30 and a["monat"]["gehalt"] == 1000
    # Kunde ordnet „Max Bauer“ dem Bereich Kinder zu
    g = next(x for x in a["gruppen"] if x["name"] == "Max Bauer")
    b = node(f"console.log(JSON.stringify(K.auswerten({json.dumps(buch)}, {{{json.dumps(g['schluessel'])}: 'kinder'}})))")
    assert b["monat"]["kinder"] == 30 and b["monat"]["sonst"] == 0


def test_kategorien_ohne_fehltreffer():
    f = lambda n, z="", b=-10: node(f"console.log(JSON.stringify(K.kategorie({json.dumps(dict(name=n, zweck=z, betrag=b))})))")
    assert f("Max Müller") == "sonst" and f("Bergold GmbH") == "sonst" and f("TUI Deutschland") == "urlaub"
    assert f("Krankenversicherung") == "vers" and f("Kreditkartenabrechnung") == "sonst" and f("Übertrag auf Tagesgeld") == "umbuchung"
    assert f("Mieter Schmidt", "Miete Oktober", 900) == "einnahme" and f("REWE", "Erstattung", 5) == "essen"


def test_gruppen_ohne_buchungsart():
    buch = [dict(datum="2026-09-02", betrag=-1450, name="Hausverwaltung Nord", zweck="Miete"),
            dict(datum="2026-10-02", betrag=-1450, name="Dauerauftrag Hausverwaltung Nord", zweck="Miete Oktober")]
    a = node(f"console.log(JSON.stringify(K.auswerten({json.dumps(buch)})))")
    assert len(a["gruppen"]) == 1 and a["gruppen"][0]["kategorie"] == "wohnen"


def test_angebrochener_monat():
    buch = [dict(datum=f"2026-0{m}-01", betrag=-1450, name="Hausverwaltung", zweck="Miete") for m in (7, 8, 9)] + \
           [dict(datum="2026-10-02", betrag=-1450, name="Hausverwaltung", zweck="Miete"), dict(datum="2026-10-09", betrag=-50, name="REWE", zweck="")]
    a = node(f"console.log(JSON.stringify(K.auswerten({json.dumps(buch)})))")
    assert a["monate"] == 3 and a["monat"]["wohnen"] == 1450 and a["monat"]["essen"] == 0 and a["ausgelassen"] == ["2026-10"]
