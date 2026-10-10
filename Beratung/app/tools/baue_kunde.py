"""Erzeugt den Kundenbereich der App aus dem Vorab-Check (eine Quelle: Privat/vorab-check/vorab.html).

Ausgabe: web/kunde.html und web/js/kunde_check.js. Ersetzt werden nur Start (Einwilligung),
Versand (Speichern über die API) und der Start der Seite. Jede Ersetzung wird geprüft.
"""
import pathlib, re
HIER = pathlib.Path(__file__).resolve().parent.parent
SRC = (HIER.parent / "Privat/vorab-check/vorab.html").read_text()
KOPF = (HIER / "tools/kopf.html").read_text()
MARKE = (HIER / "tools/marke.html").read_text()

EINWILLIGUNG = ("Ich bin einverstanden, dass meine Angaben in diesem Finanz-Check zur Vorbereitung und Durchführung "
                "meiner Beratung gespeichert und von Oliver Rosenbaum und Jan Schnichels verarbeitet werden. "
                "Ich kann die Einwilligung jederzeit hier in der App widerrufen; dann werden meine Angaben gelöscht.")


def ersetze(s, alt, neu, n=1):
    assert s.count(alt) == n, (alt[:80], s.count(alt))
    return s.replace(alt, neu)


form = SRC[SRC.index('<form id="f"'):SRC.index("</form>") + len("</form>")]
form = ersetze(form, '<form id="f" novalidate onsubmit="return false">', '<form id="f" novalidate hidden>')
# Schritt 0: Begrüßung mit Einwilligung
s0a = form.index('<section class="step on" data-step="0">'); s0b = form.index("</section>", s0a) + len("</section>")
form = form[:s0a] + f'''<section class="step on" data-step="0">
  <div class="eyebrow">Vor unserem ersten Gespräch</div>
  <h1 id="hallo">Dein Finanz-Check</h1>
  <p class="lead">Ein paar Fragen zu deinem Leben, deinem Geld und deinen Plänen, in etwa 15 Minuten. Schätzungen reichen völlig, jede Frage kannst du überspringen. Am Ende siehst du ein erstes Bild.</p>
  <div class="card">
    <p style="margin:0 0 8px"><b>Deine Daten</b></p>
    <p class="hint" style="margin:0 0 10px">Deine Angaben werden nach jedem Schritt gespeichert, damit wir uns gut vorbereiten können. Ohne deine Einwilligung speichern wir nichts. Das Ergebnis ist eine erste Einschätzung, keine Beratung.</p>
    <label style="font-weight:400;display:flex;gap:10px;align-items:flex-start"><input type="checkbox" id="einwilligung" style="margin-top:4px"> <span id="einwilligung-text">{EINWILLIGUNG}</span></label>
    <p class="hint">Details in der <a class="ph" href="#" id="ds-link">[Datenschutzerklärung]</a>.</p>
  </div>
</section>''' + form[s0b:]
# Versand-Box durch Kontobereich ersetzen
va = form.index('<div class="card" id="versand-box">'); vb = form.index("</section>", va)
form = form[:va] + '''<div class="card" id="konto-box">
    <h2 style="margin-top:0">Gespeichert</h2>
    <p id="gespeichert-text">Deine Angaben sind bei uns. Wir melden uns bei dir für das Gespräch.</p>
    <div class="nav" style="justify-content:flex-start">
      <button type="button" class="ghost" id="drucken">Als PDF speichern</button>
      <button type="button" class="quiet" id="export">Meine Daten herunterladen</button>
      <button type="button" class="danger" id="widerruf">Einwilligung widerrufen</button>
    </div>
    <p class="err" id="konto-status" role="status"></p>
  </div>
''' + form[vb:]

skripte = re.findall(r"<script>(.*?)</script>", SRC, flags=re.S)
js = skripte[2]
js = ersetze(js, 'const VERSAND = { url: "", ds_url: "" };  /*VERSAND*/\n', "")
js = ersetze(js, 'if (VERSAND.ds_url) $("ds-link").href = VERSAND.ds_url;\n', "")
a = js.index('$("senden").addEventListener'); b = js.index("// Barrierefreiheit")
js = js[:a] + js[b:]
js = ersetze(js, '$("weiter").addEventListener("click", () => zeige(akt + 1));', '$("weiter").addEventListener("click", weiterKlick);')
js = ersetze(js, "zeige(0); aktualisiere();", "")
js = ersetze(js, '"use strict";', '"use strict";\n/* erzeugt aus Privat/vorab-check/vorab.html durch tools/baue_kunde.py, nicht von Hand ändern */')
js += (HIER / "tools/kunde_zusatz.js").read_text()

html = KOPF.replace("%TITEL%", "Dein Finanz-Check") + f'''<div class="wrap">
<div class="top">{MARKE}<span class="hint" id="schritt-text"></span><button type="button" class="ghost" id="abmelden" hidden>Abmelden</button></div>
<div class="progress" aria-hidden="true"><div id="bar"></div></div>
<div class="card" id="einladung-box" hidden>
  <h1 id="einladung-titel">Willkommen</h1>
  <p class="lead">Leg ein Passwort fest, dann kannst du deinen Finanz-Check ausfüllen und später wieder aufrufen.</p>
  <form id="einladung-form" novalidate>
    <input type="email" id="einladung-email" autocomplete="username" readonly hidden>
    <label for="neu-pw">Passwort <span class="hint">mindestens 10 Zeichen</span></label><input id="neu-pw" type="password" autocomplete="new-password" minlength="10">
    <label for="neu-pw2">Passwort wiederholen</label><input id="neu-pw2" type="password" autocomplete="new-password">
    <div class="nav"><button class="primary" type="submit">Zugang anlegen</button></div>
    <p class="err" id="einladung-fehler" role="alert"></p>
  </form>
</div>
<p class="err" id="lade-fehler" role="alert"></p>
{form}
<footer><span class="ph">[Impressum]</span> · <span class="ph">[Datenschutz]</span> · Rechengrößen Stand 2026. Netto aus Brutto ist eine Schätzung.</footer>
</div>
<script src="/js/api.js"></script>
<script src="/js/rechenkern.js"></script>
<script src="/js/fragen.js"></script>
<script src="/js/kunde_check.js"></script>
</body></html>
'''
(HIER / "web/kunde.html").write_text(html)
(HIER / "web/js/kunde_check.js").write_text("(function () {" + js + "\n})();\n")
assert "onsubmit" not in html and "onclick" not in html, "Inline-Handler verstoßen gegen die CSP"
print("kunde.html und kunde_check.js erzeugt")
