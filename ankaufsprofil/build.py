"""Erzeugt alle Ankaufsprofile aus vorlage.html + profile.json (einzige Quelle)."""
import json, html, subprocess, os, sys
here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, 'profile.json')))
tpl = open(os.path.join(here, 'vorlage.html')).read()
out = os.path.join(here, 'out'); os.makedirs(out, exist_ok=True)
g = cfg['gemeinsam']
email = html.escape(g['email']) if g['email'] else '<span class="ph">[E-Mail]</span>'
about = ''
if g.get('ueber_mich'):
    best = f" {html.escape(g['eigener_bestand'])}" if g.get('eigener_bestand') else ''
    about = f'    <div class="about"><h3>Über mich</h3><p>{g["ueber_mich"]}{best}</p></div>'
for p in cfg['profile']:
    items = []
    for lbl, txt in p['standorte']:
        lab = f'<span class="lbl">{html.escape(lbl)}:</span> ' if lbl else ''
        items.append(f'            <li>{lab}{html.escape(txt)}</li>')
    rt = p['region_titel']
    s = (tpl.replace('{{TITEL}}', 'Ankaufsprofil' + (f' {rt}' if rt else ''))
            .replace('{{REGION_TITEL}}', html.escape(rt))
            .replace('{{LEAD_ORT}}', html.escape(p['lead_ort']))
            .replace('{{STAND}}', html.escape(g['stand']))
            .replace('{{STANDORTE}}', '\n'.join(items))
            .replace('{{EMAIL}}', email)
            .replace('{{UEBER_MICH}}', about)
            .replace('{{BODYCLASS}}', 'kompakt' if p.get('kompakt') else ''))
    assert '{{' not in s, p['datei']
    hp = os.path.join(out, p['datei'] + '.html'); open(hp, 'w').write(s)
    pdf = os.path.join(out, p['datei'] + '.pdf')
    subprocess.run(['node', os.path.join(here, 'render.js'), hp, pdf], check=True,
                   env=dict(os.environ, NODE_PATH=subprocess.run(['npm','root','-g'],capture_output=True,text=True).stdout.strip()))
    if g.get('autor'):
        subprocess.run(['python3','-c','import sys,pypdf;r=pypdf.PdfReader(sys.argv[1]);w=pypdf.PdfWriter(clone_from=r);w.add_metadata({"/Author":sys.argv[2]});w.write(sys.argv[1])',pdf,g['autor']],check=True)
    pages = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
    n = [l for l in pages.splitlines() if l.startswith('Pages')][0].split()[-1]
    print(f"{p['datei']}.pdf  Seiten: {n}")
    assert n == '1', 'mehr als eine Seite: ' + p['datei']
