"""Baut die drei PDFs der ganzheitlichen Finanzberatung aus src/*.html.

Platzhalter ⟦…⟧ werden hier befüllt, damit Fakten an einer Stelle stehen.
Aufruf: python3 build.py
"""
import pathlib, subprocess, sys
from pypdf import PdfReader, PdfWriter
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))
from brand import marke, marke_icon, KONTAKT_OLIVER, PFLICHTHINWEIS  # noqa: E402

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
<tr><td><b>Anlagen</b></td><td>Investmentfonds und ETFs, offene Publikums-AIF und ELTIF, jeweils mit Risikoklasse (SRI) bis 5, sowie Euro-Staatsanleihen. <b>Keine Einzelaktien, kein Krypto.</b></td></tr>
<tr><td><b>Standarddepot</b></td><td>Pflichtangebot jedes Anbieters: zwei Fonds, die vor Rentenbeginn automatisch sicherer werden (Lebenszyklus). Effektivkosten höchstens 1,0 %. Der Deckel gilt nur hier.</td></tr>
<tr><td><b>Varianten</b></td><td>freies Altersvorsorgedepot (eigene Fondsauswahl, keine Garantie) oder Garantieprodukt (80 % oder 100 % der Beiträge)</td></tr>
<tr><td><b>Auszahlung</b></td><td>ab 65 (früher mit gesetzlicher Altersrente), spätestens 70. Lebenslange Rente oder Auszahlplan bis mindestens 85. Bis 30 % als Kapital.</td></tr>
<tr><td><b>Steuer, Grenzen</b></td><td>Sonderausgabenabzug bis 1.800 € plus Zulage, nachgelagerte Besteuerung. Höchstens 6.840 € Einzahlung pro Jahr, ab dem dritten neuen Vertrag keine Förderung.</td></tr>
</table><p class="tiny" style="margin-top:2mm">Quelle: Gesetzestext BGBl. 2026 I Nr. 156. Günstigerprüfung, Zulageverfahren für Selbständige und Kostenverordnung stehen noch aus. """ + R + """</p></div>
"""
RIESTERNOTE = """<div class="note red" style="margin-top:4mm;font-size:8.4pt"><b>Riester-Falle:</b> Wer ab 2027 einen <b>neuen</b> geförderten Vertrag abschließt, für den gilt bei <b>allen</b> bestehenden Riester-Verträgen die neue Förderung; die Vertragsbedingungen bleiben. Nach Anbieterquellen nicht umkehrbar, Fundstelle im Gesetz noch prüfen. Vorher prüfen! Übertragung aus Riester: gesetzliches Recht, 3 Monate zum Quartalsende, höchstens 150 € Kosten, Zulagen bleiben erhalten. Die Riester-Garantie entfällt; im neuen Recht ist eine Garantievariante (80 % oder 100 %) wählbar. """ + R + """</div>
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
<div class="note" style="margin-top:4mm"><b>Grenzen zu anderen Berufen:</b> Keine Bewertung oder Beratung von Versicherungsverträgen, auch nicht unentgeltlich (das macht Jan als Makler, vergütet über Courtage). Courtage nie mit Honorar verrechnen. Keine Einzelfallberatung zur gesetzlichen Rente (Rentenberatung nach RDG) und keine individuelle Steuerberatung (StBerG). Allgemeine Hinweise sind zulässig. """ + R + """</div>
"""

CHECKDOKU = "".join(f'<p class="small chk">{t}</p>' for t in [
    "Statusinformation vor Beratung übergeben (Datum)",
    "Vergütungsvereinbarung unterschrieben",
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
<li><b>Einmalig 200 € Bonus</b> bei Abschluss vor dem 25. Geburtstag</li>
<li><b>Neu: auch für viele Selbständige</b> (Voraussetzungen klären wir mit Ihnen)</li>
<li>Anlage in Fonds und ETFs, ohne Garantiepflicht (Varianten mit Garantie sind möglich)</li>
<li>Auszahlung frühestens ab 65, spätestens ab 70, als Rente oder Auszahlplan bis mindestens 85, bis 30 % als Kapital</li>
</ul></div>
<div class="card fill"><h3>So viel legt der Staat dazu</h3>
<table style="font-size:8.8pt"><thead><tr><th>Ihr Beitrag pro Jahr</th><th>Kinder</th><th class="num">Zulagen</th></tr></thead><tbody>
<tr><td>360 € (30 € im Monat)</td><td>0</td><td class="num">180 €</td></tr>
<tr><td>600 € (50 € im Monat)</td><td>2</td><td class="num">840 €</td></tr>
<tr><td>1.800 € (150 € im Monat)</td><td>0</td><td class="num">540 €</td></tr>
<tr class="hl"><td>1.800 € (150 € im Monat)</td><td>2</td><td class="num">1.140 €</td></tr>
</tbody></table>
<p class="tiny" style="margin-top:2mm">Vereinfachte Rechnung nach Gesetzesstand Oktober 2026, ohne steuerliche Effekte und ohne Berufseinsteigerbonus.</p></div>
</div>
<div class="note" style="margin-top:5mm"><b>Sie haben schon einen Riester-Vertrag?</b> Dann sprechen Sie mit uns, bevor Sie etwas Neues abschließen. Schließen Sie ab 2027 einen neuen geförderten Vertrag ab, gilt für alle Ihre bestehenden Riester-Verträge die neue Förderung. Die Bedingungen der alten Verträge bleiben. Bei Riester-Fondssparplänen prüfen wir gemeinsam, ob Weiterführen, Ruhenlassen oder Übertragen am besten ist. Riester-Rentenversicherungen bewertet unser Versicherungspartner.</div>
<div class="card fill" style="margin-top:5mm"><h3>Beispiel: 150 € im Monat über 30 Jahre</h3><table style="font-size:8.8pt"><thead><tr><th>Angenommene Rendite nach Kosten</th><th class="num">mit Grundzulage</th><th class="num">ohne Zulage</th></tr></thead><tbody><tr><td>2 % pro Jahr</td><td class="num">ca. 95.600 €</td><td class="num">ca. 73.700 €</td></tr><tr><td>5,5 % pro Jahr</td><td class="num">ca. 172.800 €</td><td class="num">ca. 133.600 €</td></tr></tbody></table><p class="small" style="margin-top:2mm">Annahmen, keine Prognose. Bei Umschichtung in sicherere Anlagen vor Rentenbeginn kann die Rendite niedriger ausfallen. Die Auszahlungen sind einkommensteuerpflichtig. <b>Fonds und ETFs können an Wert verlieren.</b></p></div>
"""



def gantt():
    """Fahrplan als Swimlane-Grafik: Bereiche, Balken, Meilensteine, Heute-Linie."""
    X0, W = 205, 52                       # x-Start, Breite je Monat; m = Monate ab Oktober 2026
    X = lambda m: X0 + W * m
    labels = ["Okt", "Nov", "Dez", "Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    lanes = [  # (Bereich, Farbe, hell, [(Text, von, bis)])
        ("Aufbau", "#14213D", "#EEF0F5", [("Vorlagen, Recht, WealthKonzept-Strategien", 0, 3), ("Testgespräche", 1, 2)]),
        ("Fundament", "#3F6FB0", "#E8EEFB", [("Absicherungs-Check Bestand (Jan)", 1, 7)]),
        ("Beratung", "#2E7D32", "#E8F3E6", [("Pilot Jans Bestand", 1.5, 4), ("Regelbetrieb, Jahresgespräche, Kennzahlen", 6, 15)]),
        ("Altersvorsorge", "#B7791F", "#FBF1DF", [("AV vorbereiten", 1, 3), ("Start AV-Depot und Aktion", 3, 6)]),
        ("Add-ons", "#6B4FA0", "#F0ECF7", [("§34c, Immobilien-Abo", 6, 11), ("Edelmetall-Partner (Jan)", 2, 5)]),
    ]
    miles = [(1.5, "Pilotstart"), (3, "Start AV-Depot 1.1.27"), (6, "GmbH (geplant)")]
    top, lane_h, bar_h = 58, 52, 18
    H = top + lane_h * len(lanes) + 10
    s = [f'<svg width="100%" viewBox="0 0 1000 {H}" font-family="Inter, sans-serif">']
    # Jahresband
    s.append(f'<rect x="{X(0)}" y="0" width="{X(3)-X(0)}" height="16" rx="3" fill="#E5E8EF"/><text x="{(X(0)+X(3))/2}" y="12" font-size="10" font-weight="700" fill="#3D4A63" text-anchor="middle">2026</text>')
    s.append(f'<rect x="{X(3)+2}" y="0" width="{X(15)-X(3)-2}" height="16" rx="3" fill="#DCEFD8"/><text x="{(X(3)+X(15))/2}" y="12" font-size="10" font-weight="700" fill="#2E7D32" text-anchor="middle">2027</text>')
    for k, l in enumerate(labels):
        s.append(f'<text x="{X(k)+W/2}" y="32" font-size="9.5" fill="#6B7690" text-anchor="middle">{l}</text>')
    # Lanes: Hintergründe zuerst, dann Gitter, dann Balken
    fg = []
    for n, (name, c, cl, bars) in enumerate(lanes):
        y = top + n * lane_h
        s.append(f'<rect x="0" y="{y}" width="1000" height="{lane_h-6}" rx="6" fill="{cl}"/>')
        s.append(f'<rect x="0" y="{y}" width="6" height="{lane_h-6}" rx="3" fill="{c}"/>')
        s.append(f'<text x="16" y="{y+(lane_h-6)/2+4}" font-size="12" font-weight="700" fill="{c}">{name}</text>')
        rows = 2 if len(bars) > 1 and any(a < bb2 and a2 < b1 for (_, a, b1) in bars for (_, a2, bb2) in bars if (a, b1) != (a2, bb2)) else 1
        for k, (txt, a, bb) in enumerate(bars):
            r = k if rows == 2 else 0
            by = y + 5 + r * (bar_h + 4) if rows == 2 else y + (lane_h - 6 - bar_h) / 2
            fg.append(f'<rect x="{X(a)+2}" y="{by}" width="{X(bb)-X(a)-4}" height="{bar_h}" rx="9" fill="{c}"/>')
            if len(txt) * 5.6 > X(bb) - X(a) - 16:   # passt nicht in den Balken: rechts daneben
                fg.append(f'<text x="{X(bb)+6}" y="{by+12.5}" font-size="9.6" font-weight="600" fill="{c}">{txt}</text>')
            else:
                fg.append(f'<text x="{X(a)+10}" y="{by+12.5}" font-size="9.6" font-weight="600" fill="#fff">{txt}</text>')
    # Gitter
    for k in range(16):
        s.append(f'<line x1="{X(k)}" y1="38" x2="{X(k)}" y2="{H-6}" stroke="#FFFFFF" stroke-width="1"/>')
    s.extend(fg)
    # Meilensteine
    for m, txt in miles:
        x = X(m)
        s.append(f'<line x1="{x}" y1="44" x2="{x}" y2="{H-6}" stroke="#2E7D32" stroke-width="1" stroke-dasharray="3 3"/>')
        s.append(f'<path d="M{x} 38 l6 6 l-6 6 l-6 -6 z" fill="#2E7D32"/>')
    lab = "".join(f'<text x="{X(m)+9}" y="49" font-size="9" font-weight="700" fill="#2E7D32">{t}</text>' for m, t in miles)
    s.append(lab)
    # Heute
    xt = X(0.3)
    s.append(f'<line x1="{xt}" y1="20" x2="{xt}" y2="{H-6}" stroke="#B42318" stroke-width="2"/><rect x="{xt-20}" y="{H-20}" width="40" height="14" rx="7" fill="#B42318"/><text x="{xt}" y="{H-10}" font-size="8.5" font-weight="700" fill="#fff" text-anchor="middle">heute</text>')
    s.append('</svg>')
    return "".join(s)


REPL = {"⟦AVFAKTEN⟧": AVFAKTEN, "⟦PFLICHTEN⟧": PFLICHTEN, "⟦GANTT⟧": gantt(), "⟦MARKE_HELL⟧": marke("#FFFFFF", "#9BD77F", "NAME FOLGT · ARBEITSTITEL", 120), "⟦MARKE⟧": marke(h=70), "⟦MARKE_HELL_S⟧": marke("#FFFFFF", "#9BD77F", "NAME FOLGT · ARBEITSTITEL", 70), "⟦MARKE_KLEIN⟧": marke(subline="OLIVER ROSENBAUM", h=48), "⟦MARKE_ICON⟧": marke_icon(), "⟦CHECKDOKU⟧": CHECKDOKU,
        "⟦AVKUNDE⟧": AVKUNDE, "⟦KONTAKT-OLIVER⟧": KONTAKT_OLIVER, "⟦PFLICHTHINWEIS⟧": PFLICHTHINWEIS,
        "⟦AVTABELLE⟧": AVKONZEPT_TABELLE, "⟦RIESTERNOTE⟧": RIESTERNOTE, "⟦R⟧": R, "⟦A⟧": A}

DOCS = {"konzept": "Konzept_Ganzheitliche_Finanzberatung", "kunde": "Kundenpraesentation_Ganzheitliche_Beratung",
        "leitfaden": "Gespraechsleitfaden_Bedarfsanalyse"}
TITLES = {"konzept": "Konzept Ganzheitliche Finanzberatung", "kunde": "Ganzheitliche Finanzberatung",
          "leitfaden": "Gesprächsleitfaden Bedarfsanalyse"}

for key, out in DOCS.items():
    html = (ROOT / "src" / f"{key}.html").read_text()
    for k, v in REPL.items():
        html = html.replace(k, v)
    assert "⟦" not in html, (key, html[html.index("⟦"):html.index("⟦") + 40])
    if key == "kunde":
        assert 'class="tag' not in html, "interner Prüfvermerk im Kunden-PDF"
    tmp = ROOT / "src" / f"_{key}.built.html"
    tmp.write_text(html)
    pdf = ROOT / f"{out}.pdf"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    w = PdfWriter(clone_from=PdfReader(pdf))
    w.add_metadata({"/Title": TITLES[key], "/Author": "Oliver Rosenbaum", "/Creator": "", "/Producer": ""})
    w.write(pdf)
    print(out, len(PdfReader(pdf).pages), "Seiten")
