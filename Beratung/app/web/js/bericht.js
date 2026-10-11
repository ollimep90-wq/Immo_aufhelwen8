/* Kundenbericht „Dein Finanzbericht“: verständliche Aufbereitung mit Grafiken.
 * Eingabe ist ein Schnappschuss (keine Rohdaten, keine internen Notizen), erzeugt im Beraterbereich
 * mit Bericht.schnappschuss(); gezeigt im Beraterbereich (Vorschau) und im Kundenbereich nach Freigabe.
 * Alle Texte aus Daten werden escaped; Grafiken sind SVG ohne externe Bibliotheken.
 * Zwei Darstellungen, hell und dunkel. Die Farben für feste Ausgaben, Sparen und frei sind mit dem Palette-Validator
 * geprüft (hell auf Weiß, dunkel auf #1C1C1E: Helligkeit, Farbfehlsichtigkeit, Kontrast). Ampelfarben stehen immer mit Text. */
(function (root) {
  "use strict";
  const HELL = { fix: "#3F6FB0", spar: "#2E7D32", frei: "#C98A00", grau: "#D2D2D7", tinte: "#1D1D1F", leise: "#6E6E73", rot: "#D64545", gelb: "#C98A00", gruen: "#2E7D32",
    grund: "#FFFFFF", spur: "#EEF0F2", zone: "#DCEFD9", band: "#AEAEB2", weiss: "#FFFFFF" };
  const DUNKEL = { fix: "#3987E5", spar: "#199E70", frei: "#C98500", grau: "#3A3A40", tinte: "#F2F2F5", leise: "#A1A1A8", rot: "#E66767", gelb: "#FAB219", gruen: "#0CA30C",
    grund: "#1C1C1E", spur: "#2C2C31", zone: "#17351F", band: "#8E8E93", weiss: "#FFFFFF" };
  let F = HELL;
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
    quellen.forEach((q) => { svg += band(X[0] + NW, q.y, X[1], ym, q.h, q.farbe === F.rot ? F.rot : F.band, 0.35, q.name + ": " + eur(q.wert)); ym += q.h; });
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
    const halo = `stroke="${F.grund}" stroke-width="4" paint-order="stroke" stroke-linejoin="round"`;
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
      <rect x="0" y="20" width="${W}" height="14" rx="7" fill="${F.spur}"/>
      <rect x="${s(3)}" y="20" width="${s(6) - s(3)}" height="14" fill="${F.zone}"><title>Übliche Faustregel: 3 bis 6 Monate</title></rect>
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
      ${s(g) > 22 ? `<text x="300" y="${H - s(g) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="600" fill="${F.weiss}">${eur(g)}</text>` : ""}
      ${we > 0 ? `<rect x="240" y="${H - s(g) - s(we)}" width="120" height="${Math.max(0, s(we) - 2)}" rx="6" fill="${F.spar}"><title>Weitere Einkünfte: ${eur(we)}</title></rect>
      ${s(we) > 22 ? `<text x="300" y="${H - s(g) - s(we) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="600" fill="${F.weiss}">${eur(we)}</text>` : ""}` : ""}
      ${l > 0 ? `<rect x="240" y="${H - s(w)}" width="120" height="${Math.max(0, s(l) - 2)}" rx="6" fill="${F.rot}"><title>Lücke: ${eur(l)}</title></rect>
      ${s(l) > 40 ? `<text x="300" y="${H - s(w) + s(l) / 2 + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="${F.weiss}">Lücke ${eur(l)}</text>` : ""}` : ""}
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
        mitJahr.map((x, i) => `<circle cx="${s(zahl(x.jahr)).toFixed(1)}" cy="30" r="7" fill="${F.spar}" stroke="${F.grund}" stroke-width="2"><title>${esc(x.text)}</title></circle>
          <text x="${Math.min(W - 10, s(zahl(x.jahr))).toFixed(1)}" y="${56 + i * 22}" font-size="13" fill="${F.tinte}" text-anchor="${s(zahl(x.jahr)) > W - 160 ? "end" : "start"}"><tspan font-weight="700">${zahl(x.jahr)}</tspan> · ${esc(x.text)}${zahl(x.betrag) ? " · " + eur(x.betrag) : ""}</text>`).join("") + "</svg>";
    }
    return svg + (ohne.length ? `<ul class="b-liste">${ohne.map((x) => `<li>${esc(x.text)}</li>`).join("")}</ul>` : "");
  }

  function absicherung(liste) {
    if (!liste || !liste.length) return "";
    const STATUS = { rot: ["stark", F.rot, "●"], gelb: ["spürbar", F.gelb, "●"], gruen: ["wenig", F.gruen, "●"] };
    return `<div class="b-tabwrap"><table class="b-tab"><thead><tr><th>Bereich</th><th>Wie stark es dich treffen würde</th><th>Einschätzung</th></tr></thead><tbody>` +
      liste.map((x) => { const s = STATUS[x.ampel] || ["keine Angabe", F.grau, "○"];
        return `<tr><td>${esc(x.name)}</td><td><span style="color:${s[1]}" aria-hidden="true">${s[2]}</span> ${s[0]}</td><td>${esc(x.einschaetzung || "besprechen wir noch")}</td></tr>`; }).join("") + "</tbody></table></div>";
  }

  /* ---------- Bericht ---------- */
  /* ---------- Vision Board: Ziele als Bildkacheln ---------- */
  const SYMBOLE = {
    haus: '<path d="M8 24 L24 10 L40 24"/><path d="M12 21 V38 H36 V21"/><path d="M21 38 V29 H27 V38"/>',
    reise: '<path d="M6 26 L42 14 L36 22 L42 30 Z" /><path d="M20 22 L14 34 L20 32 L26 24"/>',
    ruhestand: '<circle cx="24" cy="18" r="6"/><path d="M24 6 V8 M24 28 V30 M12 18 H14 M34 18 H36 M15.5 9.5 L17 11 M31 25 L32.5 26.5 M15.5 26.5 L17 25 M31 11 L32.5 9.5"/><path d="M8 40 Q24 32 40 40"/>',
    bildung: '<path d="M6 20 L24 12 L42 20 L24 28 Z"/><path d="M14 24 V32 Q24 38 34 32 V24"/><path d="M42 20 V30"/>',
    auto: '<path d="M8 30 V24 L13 16 H35 L40 24 V30 Z"/><circle cx="15" cy="32" r="4"/><circle cx="33" cy="32" r="4"/>',
    herz: '<path d="M24 38 C10 28 8 20 12 15 C16 10 22 12 24 17 C26 12 32 10 36 15 C40 20 38 28 24 38 Z"/>',
    schild: '<path d="M24 6 L38 12 V22 C38 31 32 37 24 41 C16 37 10 31 10 22 V12 Z"/><path d="M18 23 L23 28 L31 19"/>',
    stern: '<path d="M24 7 L28.5 18 L40 18.5 L31 26 L34 37.5 L24 31 L14 37.5 L17 26 L8 18.5 L19.5 18 Z"/>'
  };
  function symbol(text) {
    const t = String(text || "").toLowerCase();
    if (/haus|wohnung|eigenheim|immobilie|abbezahl|kredit/.test(t)) return "haus";
    if (/reise|urlaub|welt|ferien/.test(t)) return "reise";
    if (/rente|ruhestand|aufhören|aufhoeren|früher|frueher|arbeit/.test(t)) return "ruhestand";
    if (/kind|studium|ausbildung|schule|bildung/.test(t)) return "bildung";
    if (/auto|wagen|fahrzeug|motorrad/.test(t)) return "auto";
    if (/hochzeit|heirat|familie|baby/.test(t)) return "herz";
    if (/reserve|notgroschen|sicherheit|absicher/.test(t)) return "schild";
    return "stern";
  }
  function visionBoard(ziele, v, jahr, wir) {
    const kacheln = (ziele || []).filter((x) => x && x.text).map((x) => ({ text: x.text, jahr: zahl(x.jahr) || null, betrag: zahl(x.betrag) || null, sym: symbol(x.text) }));
    if (v && zahl(v.wunsch) > 0) {
      const r = kacheln.find((k) => k.sym === "ruhestand");
      const zusatz = `${eur(v.wunsch)} im Monat zum Leben`;
      if (r) r.unter = zusatz; else kacheln.push({ text: wir ? "Ein entspannter Ruhestand" : "Ein entspannter Ruhestand", jahr: null, sym: "ruhestand", unter: zusatz });
    }
    if (!kacheln.length) return "";
    const farben = [F.spar, F.fix, F.frei];
    return `<div class="b-board">${kacheln.map((k, i) => { const f = farben[i % farben.length];
      return `<div class="b-vision" style="--vf:${f}"><svg viewBox="0 0 48 48" width="52" height="52" aria-hidden="true" fill="none" stroke="${f}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${SYMBOLE[k.sym]}</svg>
        <div><b>${esc(k.text)}</b><span>${[k.jahr ? `${k.jahr}${k.jahr > jahr ? ` · in ${k.jahr - jahr} Jahren` : ""}` : "", k.betrag ? eur(k.betrag) : "", k.unter || ""].filter(Boolean).map(esc).join(" · ")}</span></div></div>`; }).join("")}</div>`;
  }

  /* ---------- Weg: vom Heute über die nächsten Schritte zu den Zielen ---------- */
  function weg(schritte, ziele, v, jahr) {
    const punkte = [{ art: "heute", titel: "Heute", text: "Der Ausgangspunkt ist das, was schon da ist." }];
    schritte.forEach((s, i) => punkte.push({ art: "schritt", titel: `Schritt ${i + 1}`, text: s }));
    if (v && zahl(v.sparrate) > 0) punkte.push({ art: "schritt", titel: "Jeden Monat", text: `Rund ${eur(v.sparrate)} für das Alter zurücklegen (Rechenbeispiel).` });
    (ziele || []).filter((x) => x && x.text).map((x) => ({ j: zahl(x.jahr), t: x.text })).filter((x) => x.j >= jahr).sort((a, b) => a.j - b.j)
      .forEach((x) => punkte.push({ art: "ziel", titel: String(x.j), text: esc(x.t) }));   // Schritte sind schon escaped
    if (punkte.length < 2) return "";
    const farbe = { heute: F.leise, schritt: F.spar, ziel: F.fix };
    return `<ol class="b-weg">${punkte.map((p) => `<li class="b-weg-${p.art}" style="--wf:${farbe[p.art]}"><span class="b-weg-punkt"></span><div><b>${esc(p.titel)}</b><span>${p.text}</span></div></li>`).join("")}</ol>`;
  }

  /* ---------- Bericht als Geschichte: Wo du stehst – Wo du hinwillst – Wie du dahin kommst ---------- */
  function html(d, opt) {
    opt = opt || {};
    F = opt.dunkel ? DUNKEL : HELL;
    const ak = (farbe) => ` style="--akzent:${farbe}"`;
    const jahr = new Date(d.erstellt * 1000).getFullYear();
    const b = d.budget, v = d.vorsorge, m = d.vermoegen;
    const wir = !!(v && zahl(v.haushalt) === 2);
    const W = wir ? { stehst: "Wo ihr steht", willst: "Wo ihr hinwollt", kommst: "Wie ihr dahin kommt", dein: "euer", euch: "euch" }
      : { stehst: "Wo du stehst", willst: "Wo du hinwillst", kommst: "Wie du dahin kommst", dein: "dein", euch: "dich" };
    const schritte = d.naechste_schritte ? esc(d.naechste_schritte).split(/\n+/).map((z) => z.trim()).filter(Boolean) : [];
    const kapitel = (nr, titel, satz, farbe) => `<div class="b-kapitel" style="--kf:${farbe}"><span>${nr}</span><div><h2 class="b-kap-titel">${titel}</h2><p>${satz}</p></div></div>`;
    let h = `<article class="bericht${opt.dunkel ? " dunkel" : ""}"><div class="b-marke">${opt.marke || ""}</div>
      <header class="b-titel"><p class="b-eyebrow">Dein Finanzbericht</p><h1>${esc(d.vorname ? d.vorname + ", so steht es um dein Geld" : "So steht es um dein Geld")}</h1>
        <p>Stand ${new Date(d.erstellt * 1000).toLocaleDateString("de-DE")} · erstellt von ${esc(d.berater)}</p></header>`;
    // Auf einen Blick
    const blick = [
      b ? ["Heute", zahl(b.ueberschuss2) >= 0 ? `${eur(b.ueberschuss2)} frei im Monat` : `${eur(-zahl(b.ueberschuss2))} fehlen im Monat`, F.fix] : null,
      (d.ziele && d.ziele.length) || v ? ["Ziel", (d.ziele || []).filter((x) => x && x.text).slice(0, 2).map((x) => esc(x.text)).join(" · ") || `${eur(v.wunsch)} im Monat im Ruhestand`, F.spar] : null,
      v || schritte.length ? ["Weg", [schritte.length ? `${schritte.length} nächste ${schritte.length === 1 ? "Schritt" : "Schritte"}` : "", v && zahl(v.sparrate) > 0 ? `${eur(v.sparrate)} im Monat fürs Alter` : ""].filter(Boolean).join(" · "), F.frei] : null
    ].filter(Boolean);
    if (blick.length) h += `<div class="b-blick">${blick.map(([t, x, f]) => `<div style="--bf:${f}"><small>${t}</small><b>${x}</b></div>`).join("")}</div>`;

    // 1 Wo du stehst
    h += kapitel(1, W.stehst, wir ? "Euer Geld heute: was reinkommt, was rausgeht, was schon da ist und wie gut ihr abgesichert seid." : "Dein Geld heute: was reinkommt, was rausgeht, was schon da ist und wie gut du abgesichert bist.", F.fix);
    if (b) h += `<section${ak(F.fix)}><h2>Dein Geld im Monat</h2><p class="b-lead">${zahl(b.ueberschuss2) >= 0 ? `Von ${eur(b.einnahmen)} Einnahmen bleiben nach festen Ausgaben und Sparen <b>${eur(b.ueberschuss2)}</b> frei.` : `Nach festen Ausgaben und Sparen fehlen im Monat rund <b>${eur(-zahl(b.ueberschuss2))}</b>.`}</p>
      ${geldFluss(b)}<div class="b-kacheln"><div class="b-k-gruen"><small>Sparquote</small><b>${pct(b.sparquote)}</b></div><div><small>Frei nach festen Ausgaben</small><b>${eur(b.ueberschuss1)}</b></div><div class="${zahl(b.ueberschuss2) >= 0 ? "b-k-gelb" : "b-k-rot"}"><small>Frei nach dem Sparen</small><b>${eur(b.ueberschuss2)}</b></div></div></section>`;
    if (b && b.reserve_monate != null) h += `<section${ak(F.frei)}><h2>Deine Notreserve</h2><p class="b-lead">Dein Konto und Tagesgeld reichen für rund <b>${zahl(b.reserve_monate).toLocaleString("de-DE", { maximumFractionDigits: 1 })} Monate</b> feste Ausgaben.</p>${reserveSkala(b.reserve_monate)}</section>`;
    if (m && (m.vermoegen || m.schulden)) h += `<section${ak(F.fix)}><h2>Was du schon hast</h2><div class="b-kacheln"><div class="b-k-blau"><small>Vermögen</small><b>${eur(m.vermoegen)}</b></div><div><small>Offene Kredite (Restschuld)</small><b>${eur(m.schulden)}</b></div><div><small>Unterm Strich</small><b>${eur(zahl(m.vermoegen) - zahl(m.schulden))}</b></div></div></section>`;
    if (d.absicherung && d.absicherung.length) h += `<section${ak(F.fix)}><h2>Deine Absicherung</h2><p class="b-lead">Wie stark dich ein Ereignis laut deinen Antworten treffen würde, und ${d.ansprechpartner_versicherung ? `die Einschätzung deines Versicherungsmaklers ${esc(d.ansprechpartner_versicherung)}` : "unsere erste Einschätzung"}.</p>${absicherung(d.absicherung)}</section>`;

    // 2 Wo du hinwillst
    const board = visionBoard(d.ziele, v, jahr, wir);
    if (board || (d.ziele && d.ziele.length)) {
      h += kapitel(2, W.willst, `Das ist ${W.euch} wichtig. Daran messen wir alle Zahlen.`, F.spar);
      h += `<section${ak(F.spar)}><h2>${wir ? "Euer" : "Dein"} Vision Board</h2>${board}${zeitstrahl(d.ziele, jahr)}</section>`;
    }

    // 3 Wie du dahin kommst
    if (v || schritte.length) h += kapitel(3, W.kommst, `Was zwischen heute und ${wir ? "euren" : "deinen"} Zielen liegt, und die ersten Schritte dorthin.`, F.frei);
    if (v) {
      const pz = (x) => (zahl(x) * 100).toLocaleString("de-DE", { maximumFractionDigits: 1 }) + " %";
      const vz = Array.isArray(v.vorzeitig) ? v.vorzeitig : v.vorzeitig ? [{ name: "", beginn_alter: v.vorzeitig.beginn_alter, abschlag: v.vorzeitig.abschlag }] : [];
      const fehlt = Array.isArray(v.fehlt) ? v.fehlt : [];
      const kopf = wir ? "Gerechnet für euren Haushalt: beide Renten und weitere Einkünfte, so wie es aussieht, wenn alle Renten laufen."
        : v.gerechnet_fuer ? (v.gerechnet_fuer === d.vorname ? "Gerechnet nur für dich" : `Gerechnet nur für ${esc(v.gerechnet_fuer)}`) + ", die Rente der zweiten Person im Haushalt ist nicht enthalten." : "";
      const frueh = vz.length ? ` (${vz.map((x) => `${x.name ? esc(x.name) + " beginnt" : "Beginn"} mit ${zahl(x.beginn_alter)}: weniger Beitragsjahre und ${pz(x.abschlag)} Abschlag`).join("; ")})` : " laut Renteninformation";
      const rente = v.gesetzlich_brutto
        ? `${wir ? "Eure gesetzlichen Renten bringen zusammen" : "Deine gesetzliche Rente bringt"} rund ${eur(v.gesetzlich_brutto)} brutto${frueh}. Nach Kranken- und Pflegeversicherung und Steuern bleiben davon rund ${eur(v.gesetzlich)}.`
        : `${wir ? "Eure gesetzlichen Renten" : "Deine gesetzliche Rente"} nach Abzügen ${wir ? "decken" : "deckt"} davon rund ${eur(v.gesetzlich)} (Schätzung auf Basis ${wir ? "eurer" : "deiner"} Angaben).`;
      h += `<section${ak(F.spar)}><h2>${wir ? "Euer" : "Dein"} Leben nach der Arbeit</h2><p class="b-lead">Rechenbeispiel mit Annahmen (siehe unten), keine Prognose. ${kopf}${fehlt.length ? ` Die Rente von ${fehlt.map(esc).join(" und ")} fehlt noch in der Rechnung.` : ""}</p>
      <p class="b-lead">Als Ziel rechnen wir mit ${eur(v.wunsch)} im Monat in heutiger Kaufkraft${v.annahmen && v.annahmen.zielquote ? `, das sind ${pct(v.annahmen.zielquote)} ${wir ? "eures heutigen Haushaltsnettos" : "deines heutigen Nettos"}` : ""}. ${rente}${zahl(v.weitere) > 0 ? ` Dazu kommen weitere Einkünfte, zum Beispiel aus Vermietung oder Kapital, mit rund ${eur(v.weitere)} netto.` : ""}</p>
      <div class="b-zwei">${renteSaeulen(v)}<div class="b-kacheln b-spalte"><div class="b-k-rot"><small>Lücke pro Monat (heutige Kaufkraft)</small><b>${eur(v.luecke)}</b></div><div><small>Nötiges Kapital ${wir ? "zum ersten Rentenbeginn" : "mit " + (v.rentenalter || 67)} (heutige Kaufkraft)</small><b>${eur(v.kapital)}</b></div>${zahl(v.vorhanden) > 0 ? `<div><small>Davon schon angespart (hochgerechnet)</small><b>${eur(v.vorhanden)}</b></div>` : ""}<div class="b-k-gruen"><small>${zahl(v.vorhanden) > 0 ? "Rechnerische Sparrate für den Rest" : "Rechnerische Sparrate"}</small><b>${eur(v.sparrate)}</b><small>Rechenbeispiel, steigt jährlich mit der Inflation</small></div></div></div></section>`;
    }
    const w = weg(schritte, d.ziele, v, jahr);
    if (w) h += `<section${ak(F.frei)}><h2>${wir ? "Euer" : "Dein"} Weg</h2>${w}</section>`;
    const A = (v && v.annahmen) || {}, p1 = (x) => (zahl(x) * 100).toLocaleString("de-DE", { maximumFractionDigits: 1 }) + " %";
    h += `<footer class="b-fuss"><p>Dieser Bericht fasst deine Angaben und unsere Rechnungen zusammen. Alle Werte sind Näherungen und Rechenbeispiele auf Basis von Annahmen${v ? ` (Ziel ${p1(A.zielquote)} vom heutigen Netto, Rendite ${p1(A.rendite)} vor Kosten, Kosten ${p1(A.kosten)}, Inflation ${p1(A.inflation)}, Auszahlung über ${zahl(A.rentendauer)} Jahre mit ${p1(A.entnahme_real)} realer Verzinsung${v.gesetzlich_brutto ? ", gesetzliche Rente netto nach den Abgaben- und Steuerregeln von 2026" : ""})` : ""}, keine Prognose. Geldanlagen können an Wert verlieren.</p>
      <p>Der Bericht ist keine Empfehlung für ein bestimmtes Produkt. Bevor du einen Vertrag abschließt, bekommst du die gesetzlich vorgeschriebenen Unterlagen und eine eigene Beratung. Die Einschätzungen zur Absicherung sind ein erster Überblick, keine Versicherungsberatung im Einzelfall. Der Bericht ersetzt keine Rechts- oder Steuerberatung.</p></footer></article>`;
    return h;
  }

  const CSS = `
  .bericht{--b-grund:#FFFFFF;--b-karte:#F5F5F7;--b-linie:#E5E5EA;--b-linie2:#F0F0F2;--b-tinte:${HELL.tinte};--b-leise:${HELL.leise};
    --b-kopf:#2E7D32;--b-kopf-text:#FFFFFF;--b-kopf-leise:#D7EED9;--b-spar:${HELL.spar};
    --b-gruen-l:#E8F3E6;--b-blau-l:#E8EEFB;--b-gelb-l:#FFF3DC;--b-rot-l:#FBEAEA;--b-ring:#2E7D32;
    background:var(--b-grund);color:var(--b-tinte);max-width:760px;margin:0 auto;padding:24px 24px 28px;border-radius:18px;font-size:15px;line-height:1.5}
  .bericht.dunkel{--b-grund:${DUNKEL.grund};--b-karte:#26262B;--b-linie:#34343A;--b-linie2:#2A2A2F;--b-tinte:${DUNKEL.tinte};--b-leise:${DUNKEL.leise};
    --b-kopf:#173D25;--b-kopf-text:#F2F2F5;--b-kopf-leise:#9FD3AE;--b-spar:${DUNKEL.spar};
    --b-gruen-l:#12301E;--b-blau-l:#16243B;--b-gelb-l:#3A2C10;--b-rot-l:#3A1818;--b-ring:#199E70}
  .bericht h1{font-size:30px;letter-spacing:-.02em;margin:4px 0} .bericht h2{font-size:21px;margin:0 0 4px;letter-spacing:-.01em}
  .bericht h2::before{content:"";display:inline-block;width:6px;height:18px;border-radius:3px;background:var(--akzent,var(--b-spar));margin-right:10px;vertical-align:-2px}
  .bericht section{padding:22px 0;border-top:1px solid var(--b-linie);break-inside:avoid}
  .b-marke{margin-bottom:12px} .b-marke svg{display:block} .bericht.dunkel .b-marke span{color:var(--b-tinte)}
  .b-titel{background:var(--b-kopf);color:var(--b-kopf-text);border-radius:14px;padding:20px 22px;margin-bottom:6px}
  .b-titel p{margin:0;color:var(--b-kopf-leise)} .b-eyebrow{font-weight:600;font-size:13px;letter-spacing:.06em;text-transform:uppercase}
  .b-lead{color:var(--b-leise);margin:0 0 14px}
  .b-fluss{overflow-x:auto} .b-tabwrap{overflow-x:auto} .b-tab th,.b-tab td{overflow-wrap:anywhere} .b-fluss svg{min-width:560px}
  .b-kacheln{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}
  .b-kacheln div{background:var(--b-karte);border-radius:14px;padding:12px} .b-kacheln small{display:block;color:var(--b-leise);font-size:12px} .b-kacheln b{font-size:21px;letter-spacing:-.01em}
  .b-kacheln .b-k-gruen{background:var(--b-gruen-l)} .b-kacheln .b-k-blau{background:var(--b-blau-l)} .b-kacheln .b-k-gelb{background:var(--b-gelb-l)} .b-kacheln .b-k-rot{background:var(--b-rot-l)}
  .b-zwei{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:center} .b-spalte{grid-template-columns:1fr;margin-top:0}
  @media (max-width:600px){.b-zwei{grid-template-columns:1fr}}
  .b-tab{width:100%;border-collapse:collapse;font-size:14px} .b-tab th{text-align:left;color:var(--b-leise);font-size:12px;font-weight:600;padding:6px 4px;border-bottom:1px solid var(--b-linie)}
  .b-tab td{padding:8px 4px;border-bottom:1px solid var(--b-linie2)}
  .b-blick{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:14px 0 6px}
  .b-blick div{border-radius:14px;padding:12px 14px;background:var(--b-karte);border-top:4px solid var(--bf)} .b-blick small{display:block;color:var(--b-leise);font-size:12px;text-transform:uppercase;letter-spacing:.06em;font-weight:600}
  .b-blick b{font-size:16px;line-height:1.35}
  .b-kapitel{display:flex;gap:14px;align-items:center;margin:30px 0 4px;padding:14px 16px;border-radius:14px;background:var(--b-karte);break-after:avoid;break-inside:avoid}
  .b-kapitel>span{flex:0 0 40px;height:40px;border-radius:50%;background:var(--kf);color:#fff;font-weight:800;font-size:20px;display:flex;align-items:center;justify-content:center}
  .b-kapitel h2.b-kap-titel{font-size:24px;margin:0} .b-kapitel h2.b-kap-titel::before{display:none} .b-kapitel p{margin:2px 0 0;color:var(--b-leise)}
  .b-board{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:12px 0 8px}
  .b-vision{display:flex;gap:12px;align-items:center;padding:14px;border-radius:16px;background:var(--b-karte);border:1px solid var(--b-linie);box-shadow:inset 5px 0 0 var(--vf);break-inside:avoid}
  .b-vision svg{flex:0 0 auto} .b-vision b{display:block;font-size:16px} .b-vision span{display:block;color:var(--b-leise);font-size:13px}
  .b-weg{list-style:none;margin:12px 0 0;padding:0}
  .b-weg li{position:relative;display:flex;gap:14px;padding:0 0 16px 0;break-inside:avoid}
  .b-weg li::after{content:"";position:absolute;left:10px;top:22px;bottom:0;width:2px;background:var(--b-linie)} .b-weg li:last-child::after{display:none}
  .b-weg-punkt{flex:0 0 22px;height:22px;border-radius:50%;background:var(--wf);box-shadow:0 0 0 4px var(--b-grund);position:relative;z-index:1;margin-top:1px}
  .b-weg-ziel .b-weg-punkt{border-radius:6px} .b-weg-heute .b-weg-punkt{background:var(--b-grund);box-shadow:inset 0 0 0 3px var(--wf)}
  .b-weg b{display:block} .b-weg span{color:var(--b-leise)} .b-weg-schritt b{color:var(--b-tinte)}
  .b-schritte ol{list-style:none;counter-reset:schritt;margin:10px 0 0;padding:0} .b-schritte li{counter-increment:schritt;display:flex;gap:12px;align-items:baseline;margin:8px 0;font-weight:500}
  .b-schritte li::before{content:counter(schritt);flex:0 0 26px;height:26px;line-height:26px;border-radius:50%;text-align:center;font-weight:700;font-size:13px;background:var(--b-gruen-l);color:var(--b-tinte);box-shadow:inset 0 0 0 2px var(--b-ring)}
  .b-liste{margin:8px 0 0;padding-left:18px}
  .b-hinweis{color:${HELL.rot};font-size:13px} .b-fuss{border-top:1px solid var(--b-linie);padding-top:14px;color:var(--b-leise);font-size:11.5px}
  .bericht, .bericht *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  @media print{ .bericht{max-width:none;border-radius:0} .bericht:not(.dunkel){padding:0} .bericht section{padding:14px 0}
    /* Druckregeln des Aktenauszugs (app.css, #druck) gelten nicht für den Bericht */
    #druck .bericht td, #druck .bericht th{color:inherit;width:auto;padding:8px 4px;border-bottom:1px solid var(--b-linie2)} #druck .bericht th{color:var(--b-leise)}
    #druck .bericht h1{font-size:30px} #druck .bericht h2{font-size:21px;margin-top:0} }`;

  /* Druck: dunkel ohne weißen Seitenrand. Wird vor window.print() eingesetzt. */
  function druckStil(dunkel) {
    let st = document.getElementById("bericht-druck");
    if (!st) { st = document.createElement("style"); st.id = "bericht-druck"; document.head.appendChild(st); }
    st.textContent = dunkel ? `@media print{@page{margin:0} html,body.druckmodus{background:${DUNKEL.grund}!important}
      body.druckmodus #druck .bericht{padding:14mm 13mm;min-height:100vh}}` : `@media print{@page{margin:12mm}}`;
  }
  const standardDunkel = () => { try { return !!(root.matchMedia && root.matchMedia("(prefers-color-scheme: dark)").matches); } catch (e) { return false; } };

  const api = { html, CSS, druckStil, standardDunkel };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Bericht = api;
})(this);
