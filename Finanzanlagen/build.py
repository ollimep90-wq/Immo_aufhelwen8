"""Baut die drei PDFs der Finanzanlagenberatung aus src/*.html.

Platzhalter ⟦…⟧ werden hier befüllt, damit Fakten an einer Stelle stehen.
Aufruf: python3 build.py
"""
import pathlib, subprocess
from pypdf import PdfReader, PdfWriter

ROOT = pathlib.Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
R = '<span class="tag tR">prüfen</span>'
A = '<span class="tag tA">Annahme</span>'

AVFAKTEN = """
<div class="card acc" style="padding:3.5mm"><h3>Die Eckdaten</h3><table style="font-size:7.9pt;line-height:1.3">
<tr><td style="width:32%"><b>Gesetz</b></td><td>Altersvorsorgereformgesetz vom 26.05.2026 (BGBl. 2026 I Nr. 156). Neue Verträge und Zulagen ab 01.01.2027.</td></tr>
<tr><td><b>Grundzulage</b></td><td>50 % auf die ersten 360 €, 25 % auf 360,01–1.800 €, also höchstens 540 € pro Jahr. Mindesteigenbeitrag 120 € pro Jahr.</td></tr>
<tr><td><b>Kinderzulage</b></td><td>100 % der Beiträge, höchstens 300 € je Kind mit Kindergeld</td></tr>
<tr><td><b>Berufseinsteiger</b></td><td>einmalig 200 € zusätzlich, wenn jünger als 25</td></tr>
<tr><td><b>Förderberechtigt</b></td><td>Pflichtversicherte, Beamte, <b>neu: Selbständige</b> mit gewerblichen oder freiberuflichen Einkünften und abgegebener Steuererklärung. Ehepartner mittelbar (höchstens 175 €).</td></tr>
<tr><td><b>Anlagen</b></td><td>Investmentfonds und ETFs, offene Publikumsfonds und ELTIF mit Risikoklasse (SRI) bis 5, Euro-Staatsanleihen. <b>Keine Einzelaktien, kein Krypto.</b></td></tr>
<tr><td><b>Standarddepot</b></td><td>Pflichtangebot jedes Anbieters: zwei Fonds, die vor Rentenbeginn automatisch sicherer werden (Lebenszyklus). Effektivkosten höchstens 1,0 %. Der Deckel gilt nur hier.</td></tr>
<tr><td><b>Varianten</b></td><td>freies Altersvorsorgedepot (eigene Fondsauswahl, keine Garantie) oder Garantieprodukt (80 % oder 100 % der Beiträge)</td></tr>
<tr><td><b>Auszahlung</b></td><td>ab 65 (früher mit gesetzlicher Altersrente), spätestens 70. Lebenslange Rente oder Auszahlplan bis mindestens 85. Bis 30 % als Kapital.</td></tr>
<tr><td><b>Steuer, Grenzen</b></td><td>Sonderausgabenabzug bis 1.800 € plus Zulage, nachgelagerte Besteuerung. Höchstens 6.840 € Einzahlung pro Jahr, ab dem dritten neuen Vertrag keine Förderung.</td></tr>
</table><p class="tiny" style="margin-top:2mm">Quelle: Gesetzestext BGBl. 2026 I Nr. 156. Günstigerprüfung, Zulageverfahren für Selbständige und Kostenverordnung stehen noch aus. """ + R + """</p></div>
"""
RIESTERNOTE = """<div class="note red" style="margin-top:4mm;font-size:8.4pt"><b>Riester-Falle:</b> Wer ab 2027 einen <b>neuen</b> Vertrag abschließt, stellt automatisch und unwiderruflich <b>alle</b> bestehenden Riester-Verträge auf das neue Recht um. Vorher prüfen! Übertragung aus Riester: gesetzliches Recht, 3 Monate zum Quartalsende, höchstens 150 € Kosten, Zulagen bleiben erhalten. Garantien gehen dabei verloren. """ + R + """</div>
"""

AVKONZEPT_TABELLE = """
<table style="font-size:8.8pt">
<thead><tr><th>Eigenbeitrag pro Jahr</th><th>Kinder</th><th class="num">Zulagen</th><th class="num">Förderquote</th></tr></thead>
<tbody>
<tr><td>120 €</td><td>0</td><td class="num">60 €</td><td class="num">50 %</td></tr>
<tr><td>360 €</td><td>0</td><td class="num">180 €</td><td class="num">50 %</td></tr>
<tr class="hl"><td>600 €</td><td>2</td><td class="num">840 €</td><td class="num">140 %</td></tr>
<tr><td>1.200 €</td><td>1</td><td class="num">690 €</td><td class="num">57,5 %</td></tr>
<tr><td>1.800 €</td><td>0</td><td class="num">540 €</td><td class="num">30 %</td></tr>
<tr class="hl"><td>1.800 €</td><td>2</td><td class="num">1.140 €</td><td class="num">63,3 %</td></tr>
<tr><td>1.800 €</td><td>3</td><td class="num">1.440 €</td><td class="num">80 %</td></tr>
</tbody></table>
<p class="tiny" style="margin-top:2mm">Lesart: Kinderzulage aus denselben Beiträgen wie die Grundzulage. Ohne Berufseinsteigerbonus und Sonderausgabenabzug. """ + R + """</p>
"""

PFLICHTEN = """
<div class="grid g2" style="gap:6mm;margin-top:2mm">
<table style="font-size:8.6pt">
<thead><tr><th style="width:30%">Pflicht</th><th>Was konkret</th></tr></thead><tbody>
<tr><td><b>Statusinformation</b></td><td>Vor der ersten Beratung in Textform: Name, Anschrift, Status „Honorar-Finanzanlagenberater", Registernummer, Erlaubnisbehörde (§12 FinVermV)</td></tr>
<tr><td><b>Exploration</b></td><td>Kenntnisse und Erfahrungen, finanzielle Verhältnisse inkl. Verlusttragfähigkeit, Anlageziele inkl. Risikotoleranz (§16 FinVermV). Ohne vollständige Angaben keine Empfehlung.</td></tr>
<tr><td><b>Nachhaltigkeit</b></td><td>Nachhaltigkeitspräferenzen abfragen (Pflicht seit 2023)</td></tr>
<tr><td><b>Geeignetheit</b></td><td>Empfehlung muss passen, Zielmarkt der Fonds beachten. <b>Geeignetheitserklärung vor Vertragsschluss</b> (§18 FinVermV).</td></tr>
<tr><td><b>Kosten</b></td><td>Kosteninformation vorher (alle Kosten aggregiert) und jährlich danach (§13 FinVermV)</td></tr>
</tbody></table>
<table style="font-size:8.6pt">
<thead><tr><th style="width:30%">Pflicht</th><th>Was konkret</th></tr></thead><tbody>
<tr><td><b>Aufzeichnung</b></td><td>Telefonische und elektronische Beratung wird aufgezeichnet (§18a FinVermV). Videoberatung bei der IHK klären. Persönliche Gespräche dokumentieren.</td></tr>
<tr><td><b>Aufbewahrung</b></td><td>10 Jahre auf dauerhaftem Datenträger (§23 FinVermV)</td></tr>
<tr><td><b>Breite Auswahl</b></td><td>Empfehlungen aus einer hinreichenden Anzahl von Fonds verschiedener Anbieter (§34h Abs. 2 GewO). Nur ein Altersvorsorgedepot-Anbieter könnte problematisch sein.</td></tr>
<tr><td><b>Keine Zuwendungen</b></td><td>Vergütung nur vom Kunden. Zuwendungen nur ausnahmsweise und dann vollständig an den Kunden (§34h Abs. 3 GewO).</td></tr>
<tr><td><b>Bezeichnung</b></td><td>„Honorar-Finanzanlagenberater". <b>Nicht</b> „Honorar-Anlageberater" (§94 WpHG geschützt), „unabhängig" nur mit Vorsicht.</td></tr>
</tbody></table></div>
<div class="note" style="margin-top:4mm"><b>Grenzen zu anderen Berufen:</b> Keine Bewertung einzelner Versicherungsverträge gegen Honorar (das macht Jan als Makler, vergütet über Courtage). Courtage nie mit Honorar verrechnen. Keine Einzelfallberatung zur gesetzlichen Rente (Rentenberatung nach RDG) und keine individuelle Steuerberatung (StBerG). Allgemeine Hinweise sind zulässig. """ + R + """</div>
"""

CHECKDOKU = "".join(f'<p class="small chk">{t}</p>' for t in [
    "Statusinformation vor Beratung übergeben (Datum)",
    "Honorarvereinbarung unterschrieben",
    "Exploration vollständig: Kenntnisse, Verlusttragfähigkeit, Risikotoleranz, Ziele",
    "Nachhaltigkeitspräferenzen abgefragt",
    "Geeignetheitserklärung vor Vertragsschluss übergeben",
    "Kosteninformation (vorher) übergeben",
    "Telefon- oder Online-Beratung aufgezeichnet bzw. Hinweis erteilt",
    "Alles 10 Jahre archiviert",
])

AVKUNDE = """
<div class="grid g2" style="gap:5mm">
<div class="card acc"><h3>Das Wichtigste</h3><ul class="small">
<li><b>Bis zu 540 € Grundzulage</b> pro Jahr: 50 % auf die ersten 360 €, 25 % auf den Rest bis 1.800 €</li>
<li><b>Bis zu 300 € je Kind</b> mit Kindergeld</li>
<li><b>200 € Bonus</b> für Sparer unter 25 Jahren</li>
<li><b>Neu: auch für Selbständige</b></li>
<li>Anlage in Fonds und ETFs, ohne teure Pflichtgarantie</li>
<li>Auszahlung ab 65 als Rente oder Auszahlplan, bis 30 % als Kapital</li>
</ul></div>
<div class="card fill"><h3>So viel legt der Staat dazu</h3>
<table style="font-size:8.8pt"><thead><tr><th>Ihr Beitrag pro Jahr</th><th>Kinder</th><th class="num">Zulagen</th></tr></thead><tbody>
<tr><td>360 € (30 € im Monat)</td><td>0</td><td class="num">180 €</td></tr>
<tr><td>600 € (50 € im Monat)</td><td>2</td><td class="num">840 €</td></tr>
<tr><td>1.800 € (150 € im Monat)</td><td>0</td><td class="num">540 €</td></tr>
<tr class="hl"><td>1.800 € (150 € im Monat)</td><td>2</td><td class="num">1.140 €</td></tr>
</tbody></table>
<p class="tiny" style="margin-top:2mm">Vereinfachte Rechnung nach Gesetzesstand Oktober 2026, ohne steuerliche Effekte. """ + R + """</p></div>
</div>
<div class="note" style="margin-top:5mm"><b>Sie haben schon einen Riester-Vertrag?</b> Dann sprechen Sie mit uns, bevor Sie etwas Neues abschließen. Ein neuer Vertrag ab 2027 hat Folgen für alle bestehenden Riester-Verträge. Ob Weiterführen, Ruhenlassen oder Übertragen am besten ist, prüfen wir gemeinsam.</div>
<div class="card fill" style="margin-top:5mm"><h3>Beispiel: 150 € im Monat über 30 Jahre</h3><p class="small">Mit Grundzulage wächst das Vermögen bei angenommenen 5,5 % Rendite pro Jahr nach Kosten auf ca. <b>178.000 €</b>, ohne Zulage auf ca. <b>137.000 €</b>.</p><p class="tiny">Annahme, keine Prognose. Steuern in der Auszahlphase nicht berücksichtigt. Fonds können an Wert verlieren.</p></div>
"""

KONTAKT_OLIVER = '<span style="background:#FFF3B0">[Anschrift] · [Telefon] · [E-Mail]</span>'
PFLICHTHINWEIS = ('Oliver Rosenbaum, Rosenbaum Finanzberatung: Honorar-Finanzanlagenberater nach § 34h Abs. 1 GewO, '
    'Register-Nr. <span style="background:#FFF3B0">[D-…]</span>; Immobiliardarlehensvermittler nach § 34i Abs. 1 GewO, '
    'Register-Nr. <span style="background:#FFF3B0">[D-…]</span>. Jan Schnichels, Endlich Besser Beraten: Versicherungsmakler nach § 34d Abs. 1 GewO, '
    'Register-Nr. <span style="background:#FFF3B0">[D-…]</span>. Erlaubnis- und Registerbehörde: <span style="background:#FFF3B0">[IHK]</span>. '
    'Prüfung im Vermittlerregister unter www.vermittlerregister.info. Für die Finanzanlagenberatung erhält Rosenbaum Finanzberatung ausschließlich ein Honorar vom Kunden. '
    'Für die Vermittlung von Versicherungen wird Endlich Besser Beraten von den Versicherern über Courtage vergütet.')

def gantt():
    X = lambda m: 250 + 50 * m      # m = Monate ab Oktober 2026
    labels = ["Okt", "Nov", "Dez", "Jan 27", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    ticks = "".join(f'<text x="{X(i)+25}" y="16">{l}</text>' for i, l in enumerate(labels))
    lines = "".join(f'<line x1="{X(i)}" y1="22" x2="{X(i)}" y2="318"/>' for i in range(16))
    rows = [("Vorlagen und Rechtsprüfung", 0, 2, "#14213D", "Vorlagen", "#fff"),
            ("Modellportfolios festlegen", 0, 2, "#14213D", "", ""),
            ("Testgespräche (3–5)", 1, 2, "#2E7D32", "", ""),
            ("Pilot mit Jans Bestand", 1, 4, "#2E7D32", "Pilot", "#fff"),
            ("Altersvorsorgedepot vorbereiten", 1, 3, "#B7791F", "FFB, Rechner", "#fff"),
            ("Start Altersvorsorgedepot und Aktion", 3, 6, "#B7791F", "Familien, Riester-Kunden", "#fff"),
            ("Regelbetrieb, Jahresgespräche", 6, 15, "#5FA463", "Preise festigen, Kennzahlen", "#fff"),
            ("Frühstart-Rente beobachten", 0, 6, "#9AA3B8", "Gesetzgebung offen", "#fff")]
    r = t = l = ""
    for i, (n, a, b, c, lab, lc) in enumerate(rows):
        y = 30 + 36 * i
        r += f'<rect x="{X(a)}" y="{y}" width="{X(b)-X(a)}" height="22" rx="5" fill="{c}"/>'
        t += f'<text x="0" y="{y+15}">{n}</text>'
        if lab:
            l += f'<text x="{X(a)+7}" y="{y+15}" fill="{lc}">{lab}</text>'
    return (f'<svg width="100%" height="320" viewBox="0 0 1010 320"><g font-size="10.5" fill="#6B7690" text-anchor="middle">{ticks}</g>'
            f'<g stroke="#D9DEE8">{lines}</g><g font-size="12" fill="#14213D" font-weight="600">{t}</g><g>{r}</g>'
            f'<g font-size="10" font-weight="600">{l}</g></svg>')

REPL = {"⟦AVFAKTEN⟧": AVFAKTEN, "⟦PFLICHTEN⟧": PFLICHTEN, "⟦GANTT⟧": gantt(), "⟦CHECKDOKU⟧": CHECKDOKU,
        "⟦AVKUNDE⟧": AVKUNDE, "⟦KONTAKT-OLIVER⟧": KONTAKT_OLIVER, "⟦PFLICHTHINWEIS⟧": PFLICHTHINWEIS,
        "⟦AVTABELLE⟧": AVKONZEPT_TABELLE, "⟦RIESTERNOTE⟧": RIESTERNOTE, "⟦R⟧": R, "⟦A⟧": A}

DOCS = {"konzept": "Konzept_Finanzanlagenberatung", "kunde": "Kundeninformation_Ganzheitliche_Beratung",
        "leitfaden": "Gespraechsleitfaden_Bedarfsanalyse"}
TITLES = {"konzept": "Konzept Finanzanlagenberatung", "kunde": "Ganzheitliche Beratung – Rosenbaum Finanzberatung",
          "leitfaden": "Gesprächsleitfaden Bedarfsanalyse"}

for key, out in DOCS.items():
    html = (ROOT / "src" / f"{key}.html").read_text()
    for k, v in REPL.items():
        html = html.replace(k, v)
    assert "⟦" not in html, (key, html[html.index("⟦"):html.index("⟦") + 40])
    tmp = ROOT / "src" / f"_{key}.built.html"
    tmp.write_text(html)
    pdf = ROOT / f"{out}.pdf"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    w = PdfWriter(clone_from=PdfReader(pdf))
    w.add_metadata({"/Title": TITLES[key], "/Author": "Rosenbaum Finanzberatung", "/Creator": "", "/Producer": ""})
    w.write(pdf)
    print(out, len(PdfReader(pdf).pages), "Seiten")
