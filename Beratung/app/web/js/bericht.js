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
  /* Geldfluss (Sankey) wie eine Cashflow-Darstellung: Einnahmen → Geld im Monat → feste Ausgaben, Sparen, frei → Ausgabenposten.
   * Farben: nur drei Gruppen (feste Ausgaben, Sparen, frei); die Posten tragen Namen und Betrag direkt am Knoten. */
  function geldFluss(b) {
    const ein = zahl(b.einnahmen), fix = Math.max(0, zahl(b.fixkosten)), spar = Math.max(0, zahl(b.sparen));
    if (!(ein > 0)) return "";
    const frei = ein - fix - spar;
    const quellen = (Array.isArray(b.quellen) && b.quellen.length ? b.quellen : [{ name: "Einnahmen", betrag: ein }]).map((q) => ({ name: q.name, wert: zahl(q.betrag), farbe: F.leise }));
    if (frei < 0) quellen.push({ name: "Fehlbetrag", wert: -frei, farbe: F.rot });
    const ziele = [{ name: "Feste Ausgaben", wert: fix, farbe: F.fix }, { name: "Sparen", wert: spar, farbe: F.spar }, { name: "Frei verfügbar", wert: Math.max(0, frei), farbe: F.frei }].filter((x) => x.wert > 0);
    const posten = (b.ausgaben || []).filter((x) => zahl(x.betrag) > 0).map((x) => ({ name: x.name, wert: zahl(x.betrag), farbe: F.fix }));
    const W = 800, H = 330, oben = 30, NW = 12, GAP = 10, X = [175, 320, 465, 610];
    const summe = Math.max(ein - Math.min(0, frei), fix + spar);
    const maxPost = posten.reduce((a, x) => a + x.wert, 0) || 1;
    const k = Math.min((H - (quellen.length - 1) * GAP) / summe, (H - (ziele.length - 1) * GAP) / summe, posten.length ? (H - (posten.length - 1) * GAP) / maxPost : Infinity);
    const stapel = (liste, start) => { let y = start; liste.forEach((n) => { n.h = Math.max(2, n.wert * k); n.y = y; y += n.h + GAP; }); return y - GAP; };
    const hA = stapel(quellen, oben), mitte = { y: oben, h: summe * k };
    // mittlere Spalte mittig zur linken
    stapel(ziele, oben);
    const fest = ziele.find((z) => z.name === "Feste Ausgaben");
    if (posten.length) { const hoehe = posten.reduce((a, x) => a + Math.max(2, x.wert * k), 0) + (posten.length - 1) * GAP;
      stapel(posten, Math.max(oben, Math.min(fest ? fest.y + fest.h / 2 - hoehe / 2 : oben, oben + H - hoehe))); }
    const band = (x1, y1, x2, y2, h, farbe, op, titel) => { const xm = (x1 + x2) / 2;
      return `<path d="M${x1} ${y1.toFixed(1)}C${xm} ${y1.toFixed(1)} ${xm} ${y2.toFixed(1)} ${x2} ${y2.toFixed(1)}L${x2} ${(y2 + h).toFixed(1)}C${xm} ${(y2 + h).toFixed(1)} ${xm} ${(y1 + h).toFixed(1)} ${x1} ${(y1 + h).toFixed(1)}Z" fill="${farbe}" fill-opacity="${op}"><title>${esc(titel)}</title></path>`; };
    let svg = "";
    // Bänder: Quellen → Mitte
    let ym = mitte.y;
    quellen.forEach((q) => { svg += band(X[0] + NW, q.y, X[1], ym, q.h, q.farbe === F.rot ? F.rot : "#AEAEB2", 0.35, q.name + ": " + eur(q.wert)); ym += q.h; });
    // Mitte → Ziele
    ym = mitte.y;
    ziele.forEach((z) => { svg += band(X[1] + NW, ym, X[2], z.y, z.h, z.farbe, 0.3, z.name + ": " + eur(z.wert)); ym += z.h; });
    // feste Ausgaben → Posten
    if (fest) { let yf = fest.y; posten.forEach((p) => { const h = fest.h * p.wert / maxPost; svg += band(X[2] + NW, yf, X[3], p.y, h, F.fix, 0.22, p.name + ": " + eur(p.wert)); yf += h; }); }
    // Knoten
    const knoten = (x, n) => `<rect x="${x}" y="${n.y.toFixed(1)}" width="${NW}" height="${n.h.toFixed(1)}" rx="3" fill="${n.farbe}"><title>${esc(n.name)}: ${eur(n.wert)}</title></rect>`;
    svg += quellen.map((q) => knoten(X[0], q)).join("") + `<rect x="${X[1]}" y="${mitte.y}" width="${NW}" height="${mitte.h.toFixed(1)}" rx="3" fill="${F.tinte}"><title>Dein Geld im Monat: ${eur(ein)}</title></rect>`
      + ziele.map((z) => knoten(X[2], z)).join("") + posten.map((p) => knoten(X[3], p)).join("");
    // Beschriftungen: Abstand mindestens 15, damit sich nichts überlappt
    const verteile = (liste) => { const ys = liste.map((n) => n.y + n.h / 2); for (let i = 1; i < ys.length; i++) ys[i] = Math.max(ys[i], ys[i - 1] + 15);
      const ueber = ys.length ? ys[ys.length - 1] - (oben + H) : 0; if (ueber > 0) for (let i = ys.length - 1; i >= 0; i--) ys[i] = Math.min(ys[i] - ueber, i < ys.length - 1 ? ys[i + 1] - 15 : Infinity); return ys; };
    const halo = `stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round"`;
    const label = (x, y, anker, name, wert, fett) => `<text x="${x}" y="${(y + 4).toFixed(1)}" font-size="12.5" text-anchor="${anker}" fill="${F.tinte}" ${halo}>${fett ? `<tspan font-weight="700">${esc(name)}</tspan>` : esc(name)} <tspan font-weight="600">${eur(wert)}</tspan></text>`;
    verteile(quellen).forEach((y, i) => { svg += label(X[0] - 6, y, "end", quellen[i].name, quellen[i].wert); });
    svg += `<text x="${X[1] + NW / 2}" y="${oben - 10}" font-size="12.5" text-anchor="middle" fill="${F.tinte}"><tspan font-weight="700">Im Monat</tspan> ${eur(ein)}</text>`;
    verteile(ziele).forEach((y, i) => { svg += label(X[2] + NW + 6, y, "start", ziele[i].name, ziele[i].wert, true); });
    verteile(posten).forEach((y, i) => { svg += label(X[3] + NW + 6, y, "start", posten[i].name, posten[i].wert); });
    return `<div class="b-fluss"><svg viewBox="0 0 ${W} ${oben + H + 10}" width="100%" role="img" aria-label="Geldfluss: Einnahmen ${eur(ein)}, feste Ausgaben ${eur(fix)}, Sparen ${eur(spar)}, ${frei >= 0 ? "frei " + eur(frei) : "Fehlbetrag " + eur(-frei)}">${svg}</svg></div>`;
  }

  function reserveSkala(m) {
    if (m == null) return "";
    const max = 9, W = 640, s = (v) => Math.min(v, max) / max * W, wert = zahl(m);
    const farbe = wert < 1 ? F.rot : wert < 3 ? F.gelb : F.gruen;
    return `<svg viewBox="0 0 ${W} 74" width="100%" role="img" aria-label="Notreserve in Monaten">
      <rect x="0" y="20" width="${W}" height="14" rx="7" fill="#EEF0F2"/>
      <rect x="${s(3)}" y="20" width="${s(6) - s(3)}" height="14" fill="#DCEFD9"><title>Übliche Faustregel: 3 bis 6 Monate</title></rect>
      <rect x="0" y="20" width="${Math.max(6, s(wert)).toFixed(1)}" height="14" rx="7" fill="${farbe}"><title>${wert.toLocaleString("de-DE", { maximumFractionDigits: 1 })} Monate</title></rect>
      ${[0, 3, 6, 9].map((v) => `<text x="${Math.min(W - 10, s(v)).toFixed(1)}" y="52" font-size="12" fill="${F.leise}" text-anchor="${v === 0 ? "start" : v === 9 ? "end" : "middle"}">${v}${v === 9 ? "+" : ""}</text>`).join("")}
      <text x="${((s(3) + s(6)) / 2).toFixed(1)}" y="68" font-size="12" fill="${F.leise}" text-anchor="middle">Übliche Faustregel: 3–6 Monate</text></svg>`;
  }

  function renteSaeulen(v) {
    const w = zahl(v.wunsch), g = Math.min(zahl(v.gesetzlich), w), we = Math.min(Math.max(0, zahl(v.weitere)), w - g), l = Math.max(0, w - g - we);
    if (!w) return "";
    const H = 220, s = (x) => x / w * (H - 30);
    return `<svg viewBox="0 0 420 ${H + 20}" width="100%" style="max-width:420px" role="img" aria-label="Zielrente, gesetzliche Rente und Lücke">
      <rect x="40" y="${H - s(w)}" width="120" height="${s(w)}" rx="6" fill="${F.grau}"><title>Ziel: ${eur(w)}</title></rect>
      <text x="100" y="${H - s(w) / 2}" text-anchor="middle" font-size="13" font-weight="600" fill="${F.tinte}">Ziel</text>
      <text x="100" y="${H - s(w) / 2 + 18}" text-anchor="middle" font-size="14" font-weight="700" fill="${F.tinte}">${eur(w)}</text>
      <rect x="240" y="${H - s(g)}" width="120" height="${s(g)}" rx="6" fill="${F.fix}"><title>Gesetzliche Rente: ${eur(g)}</title></rect>
      ${s(g) > 40 ? `<text x="300" y="${H - s(g) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="600" fill="#fff">${eur(g)}</text>` : ""}
      ${we > 0 ? `<rect x="240" y="${H - s(g) - s(we)}" width="120" height="${Math.max(0, s(we) - 2)}" rx="6" fill="${F.spar}"><title>Weitere Einkünfte: ${eur(we)}</title></rect>
      ${s(we) > 40 ? `<text x="300" y="${H - s(g) - s(we) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="600" fill="#fff">${eur(we)}</text>` : ""}` : ""}
      ${l > 0 ? `<rect x="240" y="${H - s(w)}" width="120" height="${Math.max(0, s(l) - 2)}" rx="6" fill="${F.rot}"><title>Lücke: ${eur(l)}</title></rect>
      ${s(l) > 40 ? `<text x="300" y="${H - s(w) + s(l) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">Lücke ${eur(l)}</text>` : ""}` : ""}
      <text x="300" y="${H + 16}" text-anchor="middle" font-size="12" fill="${F.leise}">${we > 0 ? "Rente + weitere Einkünfte + Lücke" : "Gesetzliche Rente + Lücke"}</text></svg>`;
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
    return `<div class="b-tabwrap"><table class="b-tab"><thead><tr><th>Bereich</th><th>Wie stark es dich treffen würde</th><th>Einschätzung</th></tr></thead><tbody>` +
      liste.map((x) => { const s = STATUS[x.ampel] || ["keine Angabe", F.grau, "○"];
        return `<tr><td>${esc(x.name)}</td><td><span style="color:${s[1]}" aria-hidden="true">${s[2]}</span> ${s[0]}</td><td>${esc(x.einschaetzung || "besprechen wir noch")}</td></tr>`; }).join("") + "</tbody></table></div>";
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
    if (d.ziele && d.ziele.length) h += `<section><h2>Deine Ziele</h2><p class="b-lead">Das ist dir wichtig. Daran messen wir die Zahlen unten.</p>${zeitstrahl(d.ziele, jahr)}</section>`;
    if (b) h += `<section><h2>Dein Geld im Monat</h2><p class="b-lead">${zahl(b.ueberschuss2) >= 0 ? `Von ${eur(b.einnahmen)} Einnahmen bleiben nach festen Ausgaben und Sparen <b>${eur(b.ueberschuss2)}</b> frei.` : `Nach festen Ausgaben und Sparen fehlen im Monat rund <b>${eur(-zahl(b.ueberschuss2))}</b>.`}</p>
      ${geldFluss(b)}<div class="b-kacheln"><div><small>Sparquote</small><b>${pct(b.sparquote)}</b></div><div><small>Frei nach festen Ausgaben</small><b>${eur(b.ueberschuss1)}</b></div><div><small>Frei nach dem Sparen</small><b>${eur(b.ueberschuss2)}</b></div></div></section>`;
    if (b && b.reserve_monate != null) h += `<section><h2>Deine Notreserve</h2><p class="b-lead">Dein Konto und Tagesgeld reichen für rund <b>${zahl(b.reserve_monate).toLocaleString("de-DE", { maximumFractionDigits: 1 })} Monate</b> feste Ausgaben.</p>${reserveSkala(b.reserve_monate)}</section>`;
    if (m && (m.vermoegen || m.schulden)) h += `<section><h2>Was du schon hast</h2><div class="b-kacheln"><div><small>Vermögen</small><b>${eur(m.vermoegen)}</b></div><div><small>Offene Kredite (Restschuld)</small><b>${eur(m.schulden)}</b></div><div><small>Unterm Strich</small><b>${eur(zahl(m.vermoegen) - zahl(m.schulden))}</b></div></div></section>`;
    if (v) h += `<section><h2>Dein Leben nach der Arbeit</h2><p class="b-lead">Rechenbeispiel mit Annahmen (siehe unten), keine Prognose.${v.gerechnet_fuer ? (v.gerechnet_fuer === d.vorname ? " Gerechnet nur für dich" : ` Gerechnet nur für ${esc(v.gerechnet_fuer)}`) + ", die Rente der zweiten Person im Haushalt ist nicht enthalten." : ""}</p>
      <p class="b-lead">Als Ziel rechnen wir mit ${eur(v.wunsch)} im Monat in heutiger Kaufkraft${v.annahmen && v.annahmen.zielquote ? `, das sind ${pct(v.annahmen.zielquote)} deines heutigen Nettos` : ""}. ${v.gesetzlich_brutto ? `Von deiner gesetzlichen Rente (${v.vorzeitig ? `bei Beginn mit ${zahl(v.vorzeitig.beginn_alter)}, mit weniger Beitragsjahren und ${(zahl(v.vorzeitig.abschlag) * 100).toLocaleString("de-DE", { maximumFractionDigits: 1 })} % Abschlag rund` : "laut Renteninformation"} ${eur(v.gesetzlich_brutto)} brutto) bleiben nach Kranken- und Pflegeversicherung und Steuern rund ${eur(v.gesetzlich)}.${zahl(v.weitere) > 0 ? ` Dazu kommen weitere Einkünfte, zum Beispiel aus Vermietung oder Kapital, mit rund ${eur(v.weitere)} netto.` : ""}` : `Deine gesetzliche Rente nach Abzügen deckt davon rund ${eur(v.gesetzlich)} (Schätzung auf Basis deiner Angaben).`}</p>
      <div class="b-zwei">${renteSaeulen(v)}<div class="b-kacheln b-spalte"><div><small>Lücke pro Monat (heutige Kaufkraft)</small><b>${eur(v.luecke)}</b></div><div><small>Nötiges Kapital mit ${v.rentenalter || 67} (heutige Kaufkraft)</small><b>${eur(v.kapital)}</b></div>${zahl(v.vorhanden) > 0 ? `<div><small>Davon schon angespart (hochgerechnet)</small><b>${eur(v.vorhanden)}</b></div>` : ""}<div><small>${zahl(v.vorhanden) > 0 ? "Rechnerische Sparrate für den Rest" : "Rechnerische Sparrate"}</small><b>${eur(v.sparrate)}</b><small>Rechenbeispiel, steigt jährlich mit der Inflation</small></div></div></div></section>`;
    if (d.absicherung && d.absicherung.length) h += `<section><h2>Deine Absicherung</h2><p class="b-lead">Wie stark dich ein Ereignis laut deinen Antworten treffen würde, und ${d.ansprechpartner_versicherung ? `die Einschätzung deines Versicherungsmaklers ${esc(d.ansprechpartner_versicherung)}` : "unsere erste Einschätzung"}.</p>${absicherung(d.absicherung)}</section>`;
    if (d.naechste_schritte) h += `<section class="b-schritte"><h2>Deine nächsten Schritte</h2><ol>${esc(d.naechste_schritte).split(/\n+/).map((z) => z.trim()).filter(Boolean).map((z) => `<li>${z}</li>`).join("")}</ol></section>`;
    const A = (v && v.annahmen) || {}, p1 = (x) => (zahl(x) * 100).toLocaleString("de-DE", { maximumFractionDigits: 1 }) + " %";
    h += `<footer class="b-fuss"><p>Dieser Bericht fasst deine Angaben und unsere Rechnungen zusammen. Alle Werte sind Näherungen und Rechenbeispiele auf Basis von Annahmen${v ? ` (Ziel ${p1(A.zielquote)} vom heutigen Netto, Rendite ${p1(A.rendite)} vor Kosten, Kosten ${p1(A.kosten)}, Inflation ${p1(A.inflation)}, Auszahlung über ${zahl(A.rentendauer)} Jahre mit ${p1(A.entnahme_real)} realer Verzinsung${v.gesetzlich_brutto ? ", gesetzliche Rente netto nach den Abgaben- und Steuerregeln von 2026" : ""})` : ""}, keine Prognose. Geldanlagen können an Wert verlieren.</p>
      <p>Der Bericht ist keine Empfehlung für ein bestimmtes Produkt. Bevor du einen Vertrag abschließt, bekommst du die gesetzlich vorgeschriebenen Unterlagen und eine eigene Beratung. Die Einschätzungen zur Absicherung sind ein erster Überblick, keine Versicherungsberatung im Einzelfall. Der Bericht ersetzt keine Rechts- oder Steuerberatung.</p></footer></article>`;
    return h;
  }

  const CSS = `
  .bericht{background:#fff;color:${F.tinte};max-width:760px;margin:0 auto;padding:28px 24px;border-radius:18px;font-size:15px;line-height:1.5}
  .bericht h1{font-size:30px;letter-spacing:-.02em;margin:6px 0} .bericht h2{font-size:21px;margin:0 0 4px;letter-spacing:-.01em}
  .bericht section{padding:22px 0;border-top:1px solid #E5E5EA;break-inside:avoid}
  .b-eyebrow{color:${F.spar};font-weight:600;font-size:13px;letter-spacing:.04em;text-transform:uppercase;margin:18px 0 0}
  .b-lead{color:${F.leise};margin:0 0 14px} .b-marke svg{display:block}
  .b-fluss{overflow-x:auto} .b-tabwrap{overflow-x:auto} .b-tab th,.b-tab td{overflow-wrap:anywhere} .b-fluss svg{min-width:560px}
  .b-kacheln{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}
  .b-kacheln div{background:#F5F5F7;border-radius:14px;padding:12px} .b-kacheln small{display:block;color:${F.leise};font-size:12px} .b-kacheln b{font-size:21px;letter-spacing:-.01em}
  .b-zwei{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center} .b-spalte{grid-template-columns:1fr;margin-top:0}
  @media (max-width:600px){.b-zwei{grid-template-columns:1fr}}
  .b-tab{width:100%;border-collapse:collapse;font-size:14px} .b-tab th{text-align:left;color:${F.leise};font-size:12px;font-weight:600;padding:6px 4px;border-bottom:1px solid #E5E5EA}
  .b-tab td{padding:8px 4px;border-bottom:1px solid #F0F0F2}
  .b-schritte ol{margin:6px 0 0;padding-left:22px} .b-schritte li{margin:6px 0;font-weight:500} .b-liste{margin:8px 0 0;padding-left:18px}
  .b-hinweis{color:${F.rot};font-size:13px} .b-fuss{border-top:1px solid #E5E5EA;padding-top:14px;color:${F.leise};font-size:11.5px}
  .bericht, .bericht *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  @media print{ .bericht{max-width:none;padding:0;border-radius:0} .bericht section{padding:14px 0} }`;

  const api = { html, CSS };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Bericht = api;
})(this);
