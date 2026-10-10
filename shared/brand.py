"""Gemeinsame Marke, Pflichtangaben und PDF-Erzeugung für alle Unterlagen.

Eine Quelle für Pflichtangaben und Wortmarke, damit Konzept, Präsentationen
und Leitfäden nicht auseinanderlaufen.
"""
import subprocess, pathlib
from pypdf import PdfReader, PdfWriter

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
R = '<span class="tag tR">prüfen</span>'
A = '<span class="tag tA">Annahme</span>'

KONTAKT_OLIVER = '<span style="background:#FFF3B0">[Anschrift] · [Telefon] · [E-Mail]</span>'
PFLICHTHINWEIS = ('Oliver Rosenbaum: Honorar-Finanzanlagenberater nach § 34h Abs. 1 GewO, '
    'Register-Nr. <span style="background:#FFF3B0">[D-…]</span>; Immobiliardarlehensvermittler nach § 34i Abs. 1 GewO, '
    'Register-Nr. <span style="background:#FFF3B0">[D-…]</span>. Jan Schnichels, Endlich Besser Beraten: Versicherungsmakler nach § 34d Abs. 1 GewO, '
    'Register-Nr. <span style="background:#FFF3B0">[D-…]</span>. Erlaubnis- und Registerbehörde: für Oliver Rosenbaum <span style="background:#FFF3B0">[IHK]</span>, für Endlich Besser Beraten <span style="background:#FFF3B0">[IHK]</span>. '
    'Prüfung im Vermittlerregister unter www.vermittlerregister.info. Oliver Rosenbaum ist zudem Versicherungsmakler nach § 34d Abs. 1 GewO, Register-Nr. <span style="background:#FFF3B0">[D-…]</span>; Versicherungen vermittelt in dieser Kooperation Endlich Besser Beraten. Für die Beratung zu Finanzanlagen erhält Oliver Rosenbaum ausschließlich eine Vergütung vom Kunden (laufendes Serviceentgelt auf das betreute Vermögen bzw. Festpreis für einen Finanzplan). Für die Vermittlung von Immobiliardarlehen erhält Oliver Rosenbaum <span style="background:#FFF3B0">[eine Provision des Darlehensgebers]</span> und arbeitet mit mehreren Darlehensgebern zusammen. '
    'Für die Vermittlung von Versicherungen wird Endlich Besser Beraten von den Versicherern über Courtage vergütet. Wir erbringen keine Steuer- und Rechtsberatung; steuerliche und erbrechtliche Fragen klären Sie bitte mit Ihrem Steuerberater oder Notar.')

# Fassung für Unterlagen in du-Form
PFLICHTHINWEIS_DU = PFLICHTHINWEIS.replace(
    'steuerliche und erbrechtliche Fragen klären Sie bitte mit Ihrem Steuerberater oder Notar.',
    'steuerliche und erbrechtliche Fragen klärst du bitte mit deinem Steuerberater oder Notar.')
assert PFLICHTHINWEIS_DU != PFLICHTHINWEIS

def marke(text="#14213D", sub="#6B7690", subline="", h=60):
    """Neutrale Wortmarke ohne Personennamen: Haus der Finanzen."""
    icon = ('<g><path d="M30 4 L56 22 L4 22 Z" fill="#2E7D32"/>'
            '<rect x="10" y="25" width="15" height="19" rx="2" fill="#7CC243"/><rect x="35" y="25" width="15" height="19" rx="2" fill="#7CC243"/>'
            '<rect x="4" y="47" width="52" height="8" rx="2" fill="#2E7D32"/></g>')
    sl = f'<text x="72" y="52" font-size="11" fill="{sub}" letter-spacing="1.5">{subline}</text>' if subline else ""
    return (f'<svg height="{h}" viewBox="0 0 400 60" style="display:block" font-family="Inter, sans-serif">{icon}'
            f'<text x="72" y="{30 if subline else 38}" font-size="22" font-weight="700" fill="{text}">Ganzheitliche Finanzberatung</text>{sl}</svg>')

def marke_icon(h=34):
    return ('<svg height="%d" viewBox="0 0 60 60" style="display:block"><path d="M30 4 L56 22 L4 22 Z" fill="#2E7D32"/>'
            '<rect x="10" y="25" width="15" height="19" rx="2" fill="#7CC243"/><rect x="35" y="25" width="15" height="19" rx="2" fill="#7CC243"/>'
            '<rect x="4" y="47" width="52" height="8" rx="2" fill="#2E7D32"/></svg>' % h)


def render(html, pdf, title, author="Oliver Rosenbaum", forbid_tags=False):
    """Schreibt HTML in eine Temp-Datei neben dem PDF, druckt mit Chromium und setzt Metadaten."""
    pdf = pathlib.Path(pdf)
    assert "⟦" not in html, html[html.index("⟦"):html.index("⟦") + 40]
    if forbid_tags:
        assert 'class="tag' not in html, "interner Prüfvermerk in einem Kundendokument"
    tmp = pdf.with_suffix(".built.html")
    tmp.write_text(html)
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    w = PdfWriter(clone_from=PdfReader(pdf))
    w.add_metadata({"/Title": title, "/Author": author, "/Creator": "", "/Producer": ""})
    w.write(pdf)
    return len(PdfReader(pdf).pages)
