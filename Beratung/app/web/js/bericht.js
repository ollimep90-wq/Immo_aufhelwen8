/* Kundenbericht „Dein Finanzbericht“: verständliche Aufbereitung mit Grafiken.
 * Eingabe ist ein Schnappschuss (keine Rohdaten, keine internen Notizen), erzeugt im Beraterbereich
 * mit Bericht.schnappschuss(); gezeigt im Beraterbereich (Vorschau) und im Kundenbereich nach Freigabe.
 * Alle Texte aus Daten werden escaped; Grafiken sind SVG ohne externe Bibliotheken.
 * Farben (geprüft mit dem Palette-Validator, hell): Feste Ausgaben #3F6FB0, Sparen #2E7D32, Frei #C98A00. */
(function (root) {
  "use strict";
  const F = { fix: "#3F6FB0", spar: "#2E7D32", frei: "#C98A00", grau: "#D2D2D7", tinte: "#1D1D1F", leise: "#6E6E73", rot: "#D64545", gelb: "#C98A00", gruen: "#2E7D32" };
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const zahl = (x) => { const n = Number(x); return isFinite(n) ? n : 0; };
  const eur = (x) => Math.round(zahl(x)).toLocaleString("de-DE") + " €";
  const pct = (x) => Math.round(zahl(x) * 100).toLocaleString("de-DE") + " %";

  /* ---------- Grafiken ---------- */
  function geldBalken(b) {
    const ein = Math.max(zahl(b.einnahmen), 1), fix = Math.max(0, zahl(b.fixkosten)), spar = Math.max(0, zahl(b.sparen));
    const frei = Math.max(0, ein - fix - spar), ueber = fix + spar > ein;
    const W = 640, H = 120, x0 = 0, bw = W, teile = [["Feste Ausgaben", fix, F.fix], ["Sparen", spar, F.spar], ["Frei verfügbar", frei, F.frei]];
    const summe = Math.max(ein, fix + spar);
    let x = x0, svg = "";
    teile.forEach(([n, v, c], i) => {
      const w = v / summe * bw; if (w <= 0) return;
      const breite = Math.max(0, w - (i < 2 ? 2 : 0));
      svg += `<rect x="${x.toFixed(1)}" y="24" width="${breite.toFixed(1)}" height="36" rx="4" fill="${c}"><title>${n}: ${eur(v)}</title></rect>`;
      if (w > 70) svg += `<text x="${(x + 8).toFixed(1)}" y="47" font-size="13" font-weight="600" fill="#fff">${pct(v / ein)}</text>`;
      x += w;
    });
    const legende = teile.map(([n, v, c]) => `<div class="b-leg"><span style="background:${c}"></span><b>${eur(v)}</b> ${n}</div>`).join("");
    return `<svg viewBox="0 0 ${W} ${H - 40}" width="100%" role="img" aria-label="Aufteilung deiner Einnahmen">${svg}
      <text x="0" y="16" font-size="12" fill="${F.leise}">Einnahmen ${eur(ein)} im Monat = 100 %</text></svg>
      <div class="b-legenden">${legende}</div>${ueber ? '<p class="b-hinweis">Feste Ausgaben und Sparen sind zusammen höher als die Einnahmen.</p>' : ""}`;
  }

  function ausgabenBalken(liste) {
    const l = (liste || []).filter((x) => zahl(x.betrag) > 0).sort((a, z) => zahl(z.betrag) - zahl(a.betrag));
    if (!l.length) return "";
    const max = zahl(l[0].betrag), zeile = 30, W = 640, lab = 190;
    const svg = l.map((x, i) => {
      const w = zahl(x.betrag) / max * (W - lab - 90), y = i * zeile;
      return `<text x="0" y="${y + 19}" font-size="13" fill="${F.tinte}">${esc(x.name)}</text>
        <rect x="${lab}" y="${y + 6}" width="${Math.max(2, w).toFixed(1)}" height="18" rx="4" fill="${F.fix}"><title>${esc(x.name)}: ${eur(x.betrag)}</title></rect>
        <text x="${(lab + w + 8).toFixed(1)}" y="${y + 19}" font-size="13" font-weight="600" fill="${F.tinte}">${eur(x.betrag)}</text>`;
    }).join("");
    return `<svg viewBox="0 0 ${W} ${l.length * zeile}" width="100%" role="img" aria-label="Deine festen Ausgaben">${svg}</svg>`;
  }

  function reserveSkala(m) {
    if (m == null) return "";
    const max = 9, W = 640, s = (v) => Math.min(v, max) / max * W, wert = zahl(m);
    const farbe = wert < 1 ? F.rot : wert < 3 ? F.gelb : F.gruen;
    return `<svg viewBox="0 0 ${W} 74" width="100%" role="img" aria-label="Notreserve in Monaten">
      <rect x="0" y="20" width="${W}" height="14" rx="7" fill="#EEF0F2"/>
      <rect x="${s(3)}" y="20" width="${s(6) - s(3)}" height="14" fill="#DCEFD9"><title>Faustregel: 3 bis 6 Monate</title></rect>
      <rect x="0" y="20" width="${Math.max(6, s(wert)).toFixed(1)}" height="14" rx="7" fill="${farbe}"><title>${wert.toLocaleString("de-DE", { maximumFractionDigits: 1 })} Monate</title></rect>
      ${[0, 3, 6, 9].map((v) => `<text x="${Math.min(W - 10, s(v)).toFixed(1)}" y="52" font-size="12" fill="${F.leise}" text-anchor="${v === 0 ? "start" : v === 9 ? "end" : "middle"}">${v}${v === 9 ? "+" : ""}</text>`).join("")}
      <text x="${((s(3) + s(6)) / 2).toFixed(1)}" y="68" font-size="12" fill="${F.leise}" text-anchor="middle">Faustregel 3–6 Monate</text></svg>`;
  }

  function renteSaeulen(v) {
    const w = zahl(v.wunsch), g = Math.min(zahl(v.gesetzlich), w), l = Math.max(0, w - g);
    if (!w) return "";
    const H = 220, s = (x) => x / w * (H - 30);
    return `<svg viewBox="0 0 420 ${H + 20}" width="100%" style="max-width:420px" role="img" aria-label="Wunschrente, gesetzliche Rente und Lücke">
      <rect x="40" y="${H - s(w)}" width="120" height="${s(w)}" rx="6" fill="${F.grau}"><title>Wunsch: ${eur(w)}</title></rect>
      <text x="100" y="${H - s(w) / 2}" text-anchor="middle" font-size="13" font-weight="600" fill="${F.tinte}">Wunsch</text>
      <text x="100" y="${H - s(w) / 2 + 18}" text-anchor="middle" font-size="14" font-weight="700" fill="${F.tinte}">${eur(w)}</text>
      <rect x="240" y="${H - s(g)}" width="120" height="${s(g)}" rx="6" fill="${F.fix}"><title>Gesetzliche Rente: ${eur(g)}</title></rect>
      ${s(g) > 40 ? `<text x="300" y="${H - s(g) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="600" fill="#fff">${eur(g)}</text>` : ""}
      ${l > 0 ? `<rect x="240" y="${H - s(w)}" width="120" height="${Math.max(0, s(l) - 2)}" rx="6" fill="${F.rot}"><title>Lücke: ${eur(l)}</title></rect>
      ${s(l) > 40 ? `<text x="300" y="${H - s(w) + s(l) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">Lücke ${eur(l)}</text>` : ""}` : ""}
      <text x="300" y="${H + 16}" text-anchor="middle" font-size="12" fill="${F.leise}">Gesetzliche Rente + Lücke</text></svg>`;
  }

  function zeitstrahl(ziele, jahrHeute) {
    const z = (ziele || []).filter((x) => x && x.text);
    if (!z.length) return "";
    const mitJahr = z.filter((x) => zahl(x.jahr) >= jahrHeute).sort((a, b) => zahl(a.jahr) - zahl(b.jahr));
    const ohne = z.filter((x) => !(zahl(x.jahr) >= jahrHeute));
    let svg = "";
    if (mitJahr.length) {
      const bis = Math.max(...mitJahr.map((x) => zahl(x.jahr)), jahrHeute + 5), W = 640, s = (j) => 20 + (j - jahrHeute) / (bis - jahrHeute) * (W - 40);
      svg = `<svg viewBox="0 0 ${W} ${60 + mitJahr.length * 22}" width="100%" role="img" aria-label="Zeitstrahl deiner Ziele">
        <line x1="20" y1="30" x2="${W - 20}" y2="30" stroke="${F.grau}" stroke-width="2"/>
        <text x="20" y="18" font-size="12" fill="${F.leise}">heute</text>` +
        mitJahr.map((x, i) => `<circle cx="${s(zahl(x.jahr)).toFixed(1)}" cy="30" r="7" fill="${F.spar}" stroke="#fff" stroke-width="2"><title>${esc(x.text)}</title></circle>
          <text x="${Math.min(W - 10, s(zahl(x.jahr))).toFixed(1)}" y="${56 + i * 22}" font-size="13" fill="${F.tinte}" text-anchor="${s(zahl(x.jahr)) > W - 160 ? "end" : "start"}"><tspan font-weight="700">${zahl(x.jahr)}</tspan> · ${esc(x.text)}${zahl(x.betrag) ? " · " + eur(x.betrag) : ""}</text>`).join("") + "</svg>";
    }
    return svg + (ohne.length ? `<ul class="b-liste">${ohne.map((x) => `<li>${esc(x.text)}</li>`).join("")}</ul>` : "");
  }

  const STATUS = { rot: ["stark", F.rot, "●"], gelb: ["spürbar", F.gelb, "●"], gruen: ["wenig", F.gruen, "●"] };
  function absicherung(liste) {
    if (!liste || !liste.length) return "";
    return `<table class="b-tab"><thead><tr><th>Bereich</th><th>Wie stark es dich treffen würde</th><th>Einschätzung</th></tr></thead><tbody>` +
      liste.map((x) => { const s = STATUS[x.ampel] || ["–", F.grau, "○"];
        return `<tr><td>${esc(x.name)}</td><td><span style="color:${s[1]}" aria-hidden="true">${s[2]}</span> ${s[0]}</td><td>${esc(x.einschaetzung || "im Gespräch")}</td></tr>`; }).join("") + "</tbody></table>";
  }

  /* ---------- Bericht ---------- */
  function html(d, opt) {
    opt = opt || {};
    const jahr = new Date(d.erstellt * 1000).getFullYear();
    const b = d.budget, v = d.vorsorge, m = d.vermoegen;
    let h = `<article class="bericht">
      <header class="b-titel"><div class="b-marke">${opt.marke || ""}</div>
        <p class="b-eyebrow">Dein Finanzbericht</p><h1>${esc(d.vorname ? d.vorname + ", so steht es um dein Geld" : "So steht es um dein Geld")}</h1>
        <p class="b-lead">Stand ${new Date(d.erstellt * 1000).toLocaleDateString("de-DE")} · erstellt von ${esc(d.berater)}</p></header>`;
    if (d.ziele && d.ziele.length) h += `<section><h2>Deine Ziele</h2><p class="b-lead">Darauf richten wir deinen Plan aus.</p>${zeitstrahl(d.ziele, jahr)}</section>`;
    if (b) h += `<section><h2>Dein Geld im Monat</h2><p class="b-lead">Von ${eur(b.einnahmen)} Einnahmen bleiben nach festen Ausgaben und Sparen <b>${eur(b.ueberschuss2)}</b> frei.</p>
      ${geldBalken(b)}<div class="b-kacheln"><div><small>Sparquote</small><b>${pct(b.sparquote)}</b></div><div><small>Frei nach festen Ausgaben</small><b>${eur(b.ueberschuss1)}</b></div><div><small>Frei nach dem Sparen</small><b>${eur(b.ueberschuss2)}</b></div></div></section>`;
    if (b && b.ausgaben && b.ausgaben.some((x) => zahl(x.betrag) > 0)) h += `<section><h2>Wohin deine festen Ausgaben gehen</h2>${ausgabenBalken(b.ausgaben)}</section>`;
    if (b && b.reserve_monate != null) h += `<section><h2>Deine Notreserve</h2><p class="b-lead">Dein Konto und Tagesgeld reichen für rund <b>${zahl(b.reserve_monate).toLocaleString("de-DE", { maximumFractionDigits: 1 })} Monate</b> feste Ausgaben.</p>${reserveSkala(b.reserve_monate)}</section>`;
    if (m && (m.vermoegen || m.schulden)) h += `<section><h2>Was du schon hast</h2><div class="b-kacheln"><div><small>Vermögen</small><b>${eur(m.vermoegen)}</b></div><div><small>Kredite</small><b>${eur(m.schulden)}</b></div><div><small>Unterm Strich</small><b>${eur(zahl(m.vermoegen) - zahl(m.schulden))}</b></div></div></section>`;
    if (v) h += `<section><h2>Dein Leben nach der Arbeit</h2><p class="b-lead">Gewünscht sind ${eur(v.wunsch)} im Monat in heutiger Kaufkraft. Die gesetzliche Rente deckt davon rund ${eur(v.gesetzlich)}.</p>
      <div class="b-zwei">${renteSaeulen(v)}<div class="b-kacheln b-spalte"><div><small>Lücke pro Monat (heute)</small><b>${eur(v.luecke)}</b></div><div><small>Dafür nötiges Kapital mit ${v.rentenalter || 67}</small><b>${eur(v.kapital)}</b></div><div><small>Sparrate zum Start</small><b>${eur(v.sparrate)}</b><small>wächst jährlich mit der Inflation</small></div></div></div></section>`;
    if (d.absicherung && d.absicherung.length) h += `<section><h2>Deine Absicherung</h2><p class="b-lead">Wie stark dich ein Ereignis laut deinen Antworten treffen würde, und die Einschätzung deines Versicherungsmaklers.</p>${absicherung(d.absicherung)}</section>`;
    if (d.naechste_schritte) h += `<section class="b-schritte"><h2>Deine nächsten Schritte</h2>${esc(d.naechste_schritte).split(/\n+/).filter(Boolean).map((z) => `<p>✓ ${z}</p>`).join("")}</section>`;
    h += `<footer class="b-fuss"><p>Dieser Bericht fasst deine Angaben und unsere Rechnungen zusammen. Alle Werte sind Näherungen und Rechenbeispiele auf Basis von Annahmen${v ? ` (Rendite ${(zahl(v.annahmen && v.annahmen.rendite) * 100).toLocaleString("de-DE")} % vor Kosten, Kosten ${(zahl(v.annahmen && v.annahmen.kosten) * 100).toLocaleString("de-DE")} %, Inflation ${(zahl(v.annahmen && v.annahmen.inflation) * 100).toLocaleString("de-DE")} %)` : ""}, keine Prognose. Geldanlagen können an Wert verlieren. Er ersetzt keine Geeignetheitserklärung und keine Rechts- oder Steuerberatung.</p></footer></article>`;
    return h;
  }

  const CSS = `
  .bericht{background:#fff;color:${F.tinte};max-width:760px;margin:0 auto;padding:28px 24px;border-radius:18px;font-size:15px;line-height:1.5}
  .bericht h1{font-size:30px;letter-spacing:-.02em;margin:6px 0} .bericht h2{font-size:21px;margin:0 0 4px;letter-spacing:-.01em}
  .bericht section{padding:22px 0;border-top:1px solid #E5E5EA;break-inside:avoid}
  .b-eyebrow{color:${F.spar};font-weight:600;font-size:13px;letter-spacing:.04em;text-transform:uppercase;margin:18px 0 0}
  .b-lead{color:${F.leise};margin:0 0 14px} .b-marke svg{display:block}
  .b-legenden{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:8px;font-size:13px;color:${F.leise}}
  .b-leg span{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:0} .b-leg b{color:${F.tinte}}
  .b-kacheln{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}
  .b-kacheln div{background:#F5F5F7;border-radius:14px;padding:12px} .b-kacheln small{display:block;color:${F.leise};font-size:12px} .b-kacheln b{font-size:21px;letter-spacing:-.01em}
  .b-zwei{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center} .b-spalte{grid-template-columns:1fr;margin-top:0}
  @media (max-width:600px){.b-zwei{grid-template-columns:1fr}}
  .b-tab{width:100%;border-collapse:collapse;font-size:14px} .b-tab th{text-align:left;color:${F.leise};font-size:12px;font-weight:600;padding:6px 4px;border-bottom:1px solid #E5E5EA}
  .b-tab td{padding:8px 4px;border-bottom:1px solid #F0F0F2}
  .b-schritte p{margin:6px 0;font-weight:500} .b-liste{margin:8px 0 0;padding-left:18px}
  .b-hinweis{color:${F.rot};font-size:13px} .b-fuss{border-top:1px solid #E5E5EA;padding-top:14px;color:${F.leise};font-size:11.5px}
  .bericht, .bericht *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  @media print{ .bericht{max-width:none;padding:0;border-radius:0} .bericht section{padding:14px 0} }`;

  const api = { html, CSS };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Bericht = api;
})(this);
