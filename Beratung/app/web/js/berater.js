/* Beraterbereich: Kundenakten mit Bedarfsanalyse.
 * Rechnungen: Rechenkern (Netto, Budget, Risiko-Wertung) und Vorsorge (Rentenlücke) –
 * beide getestet, siehe tests/. Hier nur Oberfläche und Datenfluss. */
(function () {
  "use strict";
  const { api, $, esc, eur, pct, num, lies, fuelle } = App;
  const R = Rechenkern, V = Vorsorge;

  const ARTEN = {
    bu: "Berufsunfähigkeit", grundfaehigkeit: "Grundfähigkeit", unfall: "Unfall", risikoleben: "Risikoleben",
    pkv: "Private Krankenversicherung", krankenzusatz: "Krankenzusatz", zahnzusatz: "Zahnzusatz",
    rechtsschutz: "Rechtsschutz", hausrat: "Hausrat", wohngebaeude: "Wohngebäude", haftpflicht: "Privathaftpflicht",
    tierkranken: "Tierkranken", tier_op: "Tier-OP"
  };
  const FIX = [["fk_wohnen", "Wohnen"], ["fk_essen", "Essen und Drogerie"], ["fk_mobil", "Mobilität"], ["fk_kinder", "Kinder"],
    ["fk_vers", "Versicherungen"], ["fk_vertr", "Verträge und Abos"], ["fk_kredit", "Kredite und Leasing"],
    ["fk_urlaub", "Urlaub und Freizeit"], ["fk_sonst", "Sonstiges"]];
  const LAENDER = [["BW", "Baden-Württemberg"], ["BY", "Bayern"], ["BE", "Berlin"], ["BB", "Brandenburg"], ["HB", "Bremen"], ["HH", "Hamburg"],
    ["HE", "Hessen"], ["MV", "Mecklenburg-Vorpommern"], ["NI", "Niedersachsen"], ["NW", "Nordrhein-Westfalen"], ["RP", "Rheinland-Pfalz"],
    ["SL", "Saarland"], ["SN", "Sachsen"], ["ST", "Sachsen-Anhalt"], ["SH", "Schleswig-Holstein"], ["TH", "Thüringen"]];
  const TABS = [["ueberblick", "Überblick", null], ["haushalt", "Haushalt & Netto", "haushalt"], ["budget", "Budget", "budget"],
    ["vorsorge", "Vermögen & Vorsorge", "altersvorsorge"], ["risiko", "Risiko-Check", "risiko"],
    ["absicherung", "Absicherung", "absicherung_bewertung"], ["ziele", "Ziele & Notizen", "ziele"], ["zugang", "Zugang & Daten", null]];

  let ich = null, akte = null, tab = "ueberblick", fragenVoll = null, geaendert = false;

  /* ---------- Hilfen ---------- */
  const daten = (s) => (akte.abschnitte[s] && akte.abschnitte[s].daten) || null;
  const version = (s) => (akte.abschnitte[s] && akte.abschnitte[s].version) || null;
  const vorab = () => { const v = daten("vorab"); return v && v.auswertung; };
  const feld = (f, label, typ = "number", extra = "") =>
    `<div><label for="i_${f}">${label}</label><input id="i_${f}" data-f="${f}" type="${typ}" ${typ === "number" ? 'inputmode="decimal" step="any"' : ""} ${extra}></div>`;
  const seg = (f, label, optionen) => `<div><label>${label}</label><div class="seg" role="radiogroup" aria-label="${esc(label)}">` +
    optionen.map(([w, t]) => `<label><input type="radio" name="${f}" data-f="${f}" value="${w}"><span>${t}</span></label>`).join("") + "</div></div>";
  const fehler = (t) => { $("fehler").textContent = t || ""; };
  const datum = (t) => t ? new Date(t * 1000).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" }) : "–";

  /* ---------- Rechnungen aus den Abschnitten ---------- */
  function haushaltRechnung(h) {
    if (!h) return null;
    const pers = [1, 2].map((i) => ({ brutto: num(h["brutto" + i]), kv: h["kv" + i] || "gkv", pkv_eigenanteil_monat: num(h["pkv" + i]),
      zusatzbeitrag: h["zb" + i] ? num(h["zb" + i]) / 100 : undefined, alter: num(h["alter" + i]) || 40,
      kinder_u25: num(h.kinder_u25), eltern: num(h.kinder_u25) > 0 || h.eltern === "ja", sachsen: h.land === "SN" }));
    const brutto = pers.filter((p) => p.brutto > 0);
    const r = brutto.length ? R.nettoHaushalt({ personen: brutto, verheiratet: h.familie === "verheiratet", kinder: num(h.kinder_u25),
      kirche: h.kirche === "ja", bundesland: h.land, alleinerziehend: h.familie === "allein" && num(h.kinder_u25) > 0 }) : null;
    const nettoDirekt = num(h.netto1) + num(h.netto2);
    return { rechnung: r, netto_monat: (r ? r.netto_monat : 0) + nettoDirekt, kindergeld: num(h.kinder_kg) * R.P2026.kindergeld_monat };
  }
  function budgetRechnung(b, hr) {
    if (!b) return null;
    const fk = FIX.reduce((a, [k]) => a + num(b[k]), 0);
    return Object.assign({ fixkosten: fk }, R.budget({ netto_monat: hr ? hr.netto_monat : num(b.netto_manuell),
      kindergeld_monat: hr ? hr.kindergeld : 0, sonstige_einnahmen: num(b.sonstige), fixkosten: fk, sparen: num(b.sparen), liquide: num(b.liquide) }));
  }
  function vorsorgeRechnung(v, h, hr) {
    if (!v) return null;
    const alter = num(h && h.alter1) || num(v.alter);
    const jahre = Math.max(0, (num(v.rentenalter) || 67) - alter);
    if (!jahre) return null;
    // Standard: Person 1 (die gesetzliche Rente ist eine Einzelangabe); Haushalt nur bewusst über netto_basis
    const p1 = hr && hr.rechnung && hr.rechnung.personen[0];
    const netto = num(v.netto_basis) || (h && num(h.netto1)) || (p1 ? p1.netto_monat : 0);
    return V.rentenluecke({ netto, gesetzl_netto: num(v.gesetzl), jahre_bis_rente: jahre, vorhanden: num(v.av_kapital) },
      { zielquote: num(v.zielquote) / 100 || V.STANDARD.zielquote, rendite: v.rendite !== "" && v.rendite != null ? num(v.rendite) / 100 : V.STANDARD.rendite,
        kosten: v.kosten !== "" && v.kosten != null ? num(v.kosten) / 100 : V.STANDARD.kosten, inflation: v.inflation !== "" && v.inflation != null ? num(v.inflation) / 100 : V.STANDARD.inflation,
        entnahme_real: v.entnahme !== "" && v.entnahme != null ? num(v.entnahme) / 100 : V.STANDARD.entnahme_real, rentendauer: num(v.rentendauer) || V.STANDARD.rentendauer });
  }
  function filterKontext() {
    const h = daten("haushalt") || {}, va = vorab() || {}, p = va.person || {};
    return { kinder: num(h.kinder_u25) > 0 || num(p.kinder) > 0, tier: num(h.tiere) > 0 || num(p.tiere) > 0,
      partner: ["partner", "verheiratet"].includes(h.familie || p.familie), eigentum: (h.wohnen || p.wohnen) === "eigentum" };
  }
  function sichtbar(q, k) { return !q.filter.length || q.filter.some((f) => k[f]); }
  function risikoRechnung(r) {
    if (!r || !fragenVoll) return null;
    const k = filterKontext(), antworten = {};
    fragenVoll.fragen.filter((q) => sichtbar(q, k)).forEach((q) => {
      const v = r["q_" + q.id];
      if (v === undefined || v === "") return;
      antworten[q.id] = v === "na" ? null : Number(v);
    });
    return R.risikoAuswertung(fragenVoll.fragen.map((q) => ({ id: q.id, block: q.block, gewichte: q.gewichte })), antworten);
  }

  /* ---------- Liste ---------- */
  async function zeigeListe() {
    akte = null; $("akte").hidden = true; $("liste").hidden = false; fehler();
    history.replaceState(null, "", "/berater.html");
    const rows = await api.get("/api/akten");
    $("akten").innerHTML = rows.map((a) => `<tr class="klick" data-id="${a.id}" tabindex="0"><td><b>${esc(a.titel)}</b></td>
      <td>${a.kunde_id ? '<span class="badge gr">aktiv</span>' : '<span class="badge">keiner</span>'}</td>
      <td>${a.vorab_da ? '<span class="badge gr">ausgefüllt</span>' : '<span class="badge">offen</span>'}</td>
      <td class="n hint">${datum(a.geaendert)}</td></tr>`).join("") || '<tr><td colspan="4" class="hint">Noch keine Akten.</td></tr>';
    document.querySelectorAll("#akten tr.klick").forEach((tr) => {
      const oeffnen = () => oeffneAkte(Number(tr.dataset.id));
      tr.addEventListener("click", oeffnen);
      tr.addEventListener("keydown", (e) => { if (e.key === "Enter") oeffnen(); });
    });
  }

  /* ---------- Akte ---------- */
  async function oeffneAkte(id, neuerTab) {
    if (geaendert && !confirm("Ungespeicherte Änderungen verwerfen?")) return;
    fehler();
    akte = await api.get("/api/akten/" + id);
    if (!fragenVoll) fragenVoll = await (await fetch("/data/fragen_voll.json")).json();
    $("liste").hidden = true; $("akte").hidden = false;
    $("akte-titel").textContent = akte.titel;
    history.replaceState(null, "", "/berater.html#akte=" + id);
    zeigeTab(neuerTab || tab);
  }

  function zeigeTab(t) {
    tab = t; geaendert = false;
    $("tabs").innerHTML = TABS.map(([k, n]) => `<button type="button" role="tab" aria-selected="${k === t}" data-tab="${k}">${n}</button>`).join("");
    $("tabs").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
      if (geaendert && !confirm("Ungespeicherte Änderungen verwerfen?")) return;
      zeigeTab(b.dataset.tab);
    }));
    const abschnitt = TABS.find(([k]) => k === t)[2];
    const darfSchreiben = abschnitt && !(abschnitt === "absicherung_bewertung" && ich.bereich !== "versicherung");
    $("speicher").hidden = !darfSchreiben; $("speicher-status").textContent = "";
    $("inhalt").innerHTML = RENDER[t]();
    const box = $("inhalt");
    if (abschnitt) {
      fuelle(box, daten(abschnitt));
      if (!darfSchreiben) box.querySelectorAll("input,select,textarea").forEach((e) => { e.disabled = true; });
    }
    (NACH[t] || (() => {}))();
    (BINDEN[t] || (() => {}))();
  }

  async function speichern() {
    const abschnitt = TABS.find(([k]) => k === tab)[2];
    if (!abschnitt) return;
    const d = lies($("inhalt"));
    try {
      const r = await api.put(`/api/akten/${akte.id}/abschnitte/${abschnitt}`, { daten: d, version: version(abschnitt) });
      akte.abschnitte[abschnitt] = { daten: d, version: r.version, geaendert: Date.now() / 1000 };
      geaendert = false; $("speicher-status").textContent = "gespeichert"; fehler();
    } catch (e) { fehler(e.message); $("speicher-status").textContent = "nicht gespeichert"; }
  }

  function uebernehmenKnopf(text) {
    return vorab() ? `<p class="info">Der Kunde hat den Vorab-Check ausgefüllt. <button type="button" class="ghost" id="uebernehmen">${text || "Angaben übernehmen"}</button></p>` : "";
  }

  /* ---------- Tabs: Inhalt ---------- */
  const RENDER = {
    ueberblick() {
      const va = vorab(), h = daten("haushalt"), hr = haushaltRechnung(h), b = budgetRechnung(daten("budget"), hr);
      const vs = vorsorgeRechnung(daten("altersvorsorge"), h, hr), rk = risikoRechnung(daten("risiko")), ab = daten("absicherung_bewertung") || {};
      const ziele = daten("ziele") || {};
      const quelle = b ? "aus der Beratung" : va ? "aus dem Vorab-Check des Kunden" : null;
      const bb = b || (va && va.budget);
      let html = `<div class="card"><h2 style="margin-top:0">Geld im Monat <span class="badge">${quelle || "noch keine Angaben"}</span></h2>`;
      if (bb) html += `<div class="kpi">
        <div><small>Einnahmen</small><b>${eur(bb.einnahmen)}</b></div>
        <div><small>Feste Ausgaben</small><b>${eur(b ? b.fixkosten : va.fixkosten_summe)}</b></div>
        <div><small>Überschuss I</small><b>${eur(bb.ueberschuss1)}</b><small>${pct(bb.quote1)}</small></div>
        <div><small>Sparquote</small><b>${pct(bb.sparquote)}</b></div>
        <div><small>Überschuss II</small><b>${eur(bb.ueberschuss2)}</b><small>${pct(bb.quote2)}</small></div>
        <div><small>Notreserve</small><b><span class="amp ${bb.reserve_ampel}"></span>${bb.reserve_monate == null ? "–" : bb.reserve_monate.toLocaleString("de-DE", { maximumFractionDigits: 1 }) + " Mon."}</b></div></div>`;
      html += "</div>";
      html += `<div class="card"><h2 style="margin-top:0">Altersvorsorge</h2>${vs ? `<div class="kpi">
        <div><small>Lücke heute</small><b>${eur(vs.luecke)}</b><small>pro Monat, heutige Kaufkraft</small></div>
        <div><small>Kapitalbedarf</small><b>${eur(vs.kapital)}</b></div>
        <div><small>Sparrate</small><b>${eur(vs.sparrate)}</b><small>Start, wächst mit Inflation</small></div></div>` : '<p class="hint">Noch nicht gerechnet (Tab Vermögen & Vorsorge).</p>'}</div>`;
      const arten = rk ? Object.keys(ARTEN).filter((k) => rk[k]).sort((a, z) => rk[z].quote - rk[a].quote) : [];
      html += `<div class="card"><h2 style="margin-top:0">Absicherung</h2>`;
      if (arten.length) html += `<table><thead><tr><th>Bereich</th><th class="n">Betroffenheit</th><th>Bewertung Jan</th></tr></thead><tbody>` +
        arten.map((k) => `<tr><td><span class="amp ${rk[k].ampel}"></span>${ARTEN[k]}</td><td class="n">${pct(rk[k].quote)}</td><td>${esc(BEW[ab["s_" + k]] || "–")}</td></tr>`).join("") + "</tbody></table>";
      else if (va && va.risiko) html += '<p class="hint">Nur Kurzcheck des Kunden vorhanden:</p>' + Object.entries(va.risiko.ergebnis || {}).map(([k, e]) =>
        `<div><span class="amp ${e.ampel}"></span>${esc(Fragen.THEMEN[k] || k)} · ${pct(e.quote)}</div>`).join("");
      else html += '<p class="hint">Risiko-Check noch nicht ausgefüllt.</p>';
      html += "</div>";
      const zl = [1, 2, 3, 4, 5].map((i) => ziele["z" + i]).filter(Boolean);
      const vw = va && va.wuensche ? va.wuensche.map((w) => w.text + (w.jahr ? " · " + w.jahr : "")) : [];
      html += `<div class="card"><h2 style="margin-top:0">Ziele</h2>${(zl.length ? zl : vw).map((z) => `<div>· ${esc(z)}</div>`).join("") || '<p class="hint">Noch keine.</p>'}</div>`;
      html += `<div class="nav"><button type="button" class="quiet" id="drucken">Ergebnisbogen drucken</button></div>`;
      return html;
    },
    haushalt() {
      const person = (i, titel) => `<div class="card"><h2 style="margin-top:0">${titel}</h2><div class="row3">
        ${feld("name" + i, "Name", "text")}${feld("alter" + i, "Alter")}${feld("brutto" + i, "Brutto im Jahr in €")}</div>
        <div class="row3">${seg("kv" + i, "Krankenversicherung", [["gkv", "Gesetzlich"], ["pkv", "Privat"]])}
        ${feld("zb" + i, 'Zusatzbeitrag in % <span class="hint">leer = Ø 2,9</span>')}${feld("pkv" + i, 'PKV-Basisanteil im Monat <span class="hint">nach AG-Zuschuss</span>')}</div>
        <div class="row3">${feld("netto" + i, 'oder Netto im Monat direkt <span class="hint">z. B. Beamte, Selbstständige</span>')}</div></div>`;
      return uebernehmenKnopf("Aus dem Vorab-Check übernehmen") + `<div class="card"><h2 style="margin-top:0">Haushalt</h2><div class="row3">
        ${seg("familie", "Familienstand", [["allein", "Allein"], ["partner", "Partnerschaft"], ["verheiratet", "Verheiratet"]])}
        ${feld("kinder_u25", "Kinder unter 25")}${feld("kinder_kg", "davon mit Kindergeld")}</div><div class="row3">
        ${seg("eltern", "Erwachsene Kinder?", [["ja", "Ja"], ["nein", "Nein"]])}${feld("tiere", "Haustiere")}
        ${seg("wohnen", "Wohnen", [["miete", "Miete"], ["eigentum", "Eigentum"], ["sonst", "Anders"]])}</div><div class="row3">
        <div><label for="i_land">Bundesland</label><select id="i_land" data-f="land"><option value="">–</option>${LAENDER.map(([k, n]) => `<option value="${k}">${n}</option>`).join("")}</select></div>
        ${seg("kirche", "Kirchensteuer", [["ja", "Ja"], ["nein", "Nein"]])}<div></div></div></div>
        ${person(1, "Person 1")}${person(2, "Person 2")}
        <div class="card"><h2 style="margin-top:0">Netto (Schätzung)</h2><div id="netto-erg"></div>
        <p class="hint">Jahresrechnung mit Rechengrößen 2026, ohne Steuerklassen III/V, Freibeträge, Minijob. Unverheiratete werden einzeln gerechnet.</p></div>`;
    },
    budget() {
      return uebernehmenKnopf("Aus dem Vorab-Check übernehmen") + `<div class="card"><h2 style="margin-top:0">Feste Ausgaben pro Monat</h2><div class="row3">
        ${FIX.map(([k, n]) => feld(k, n)).join("")}</div></div>
        <div class="card"><h2 style="margin-top:0">Sparen und Reserve</h2><div class="row3">
        ${feld("sonstige", "Weitere Einnahmen im Monat")}${feld("sparen", "Sparraten im Monat")}${feld("liquide", "Konto und Tagesgeld")}</div>
        <div class="row3">${feld("netto_manuell", 'Netto im Monat <span class="hint">nur wenn im Tab Haushalt leer</span>')}</div></div>
        <div class="card"><h2 style="margin-top:0">Ergebnis</h2><div class="kpi" id="budget-erg"></div></div>`;
    },
    vorsorge() {
      return uebernehmenKnopf("Aus dem Vorab-Check übernehmen") + `<div class="card"><h2 style="margin-top:0">Vermögen</h2><div class="row3">
        ${feld("depot", "Depots und Fonds")}${feld("immobilien", "Immobilien (Verkehrswert)")}${feld("sonstverm", "Sonstiges Vermögen")}
        ${feld("schulden", "Kredite (Restschuld)")}${feld("av_kapital", 'Kapital fürs Alter heute <span class="hint">z. B. Riester, bAV-Wert</span>')}<div></div></div></div>
        <div class="card"><h2 style="margin-top:0">Rentenlücke</h2><div class="row3">
        ${feld("rentenalter", "Rentenbeginn mit Alter")}${feld("gesetzl", 'Gesetzliche Rente netto <span class="hint">heutige Kaufkraft, Renteninformation</span>')}
        ${feld("netto_basis", 'Netto heute <span class="hint">leer = Person 1 aus Haushalt</span>')}</div>
        <p class="hint">Gerechnet wird für eine Person (Standard: Person 1). Für Person 2 oder den Haushalt Netto und gesetzliche Renten hier passend eintragen.</p>
        <h3>Annahmen <span class="hint">leer = Standard wie in den Präsentationen</span></h3><div class="row3">
        ${feld("zielquote", "Ziel in % vom Netto (80)")}${feld("rendite", "Rendite vor Kosten % (6)")}${feld("kosten", "Kosten % (1,3)")}
        ${feld("inflation", "Inflation % (2)")}${feld("entnahme", "Reale Rendite in der Auszahlung % (1)")}${feld("rentendauer", "Auszahlungsdauer Jahre (25)")}</div>
        <div class="kpi" id="vorsorge-erg" style="margin-top:12px"></div>
        <p class="hint">Rechenbeispiel in heutiger Kaufkraft, ohne Steuern und Sozialabgaben. Annahmen, keine Prognose.</p></div>`;
    },
    risiko() {
      const k = filterKontext();
      const skala = (q) => (q.skala === "zustimmung" ? Fragen.SKALA_ZUSTIMMUNG : Fragen.SKALA);
      let html = `<p class="info">Der Kunde schätzt ein, wie stark ihn eine Situation treffen würde. Das Ergebnis zeigt Betroffenheit, nicht ob er versichert ist. Fragen zu Kindern, Tieren, Partner und Eigentum erscheinen je nach Angaben im Tab Haushalt. Gewichte laut Excel-Prototyp, Klärung mit Jan offen.</p>`;
      fragenVoll.bloecke.forEach((b) => {
        const qs = fragenVoll.fragen.filter((q) => q.block === b.nr && sichtbar(q, k));
        if (!qs.length) return;
        html += `<div class="card"><h2 style="margin-top:0">${b.nr} · ${esc(b.titel)}</h2>` + (b.nr === 9 ? '<p class="note">Selbstbild und eigene Erfahrungen: nur im Gespräch mit Jan, keine Gesundheitsdetails notieren.</p>' : "") +
          qs.map((q) => `<p class="q" id="l_${q.id}">${esc(q.text)}${q.quelle === "neu" ? ' <span class="badge">neu</span>' : ""}</p>
          <div class="seg" role="radiogroup" aria-labelledby="l_${q.id}">${skala(q).map((s) => `<label><input type="radio" name="q_${q.id}" data-f="q_${q.id}" value="${s.wert === null ? "na" : s.wert}"><span>${s.text}</span></label>`).join("")}</div>`).join("") + "</div>";
      });
      return html + `<div class="card"><h2 style="margin-top:0">Ergebnis</h2><table id="risiko-erg"></table></div>`;
    },
    absicherung() {
      const rk = risikoRechnung(daten("risiko")) || {};
      const lese = ich.bereich !== "versicherung";
      return (lese ? '<p class="note">Die fachliche Bewertung der Absicherung schreibt Jan (Versicherungsmakler, § 34d GewO). Du siehst sie hier nur.</p>' : "") +
        `<div class="card"><table><thead><tr><th>Bereich</th><th class="n">Betroffenheit</th><th>Status</th><th>Notiz</th></tr></thead><tbody>` +
        Object.entries(ARTEN).map(([k, n]) => `<tr><td>${rk[k] ? `<span class="amp ${rk[k].ampel}"></span>` : ""}${n}</td><td class="n">${rk[k] ? pct(rk[k].quote) : "–"}</td>
          <td><select data-f="s_${k}" aria-label="Status ${n}"><option value="">–</option>${Object.entries(BEW).map(([w, t]) => `<option value="${w}">${t}</option>`).join("")}</select></td>
          <td><input type="text" data-f="n_${k}" aria-label="Notiz ${n}" maxlength="300"></td></tr>`).join("") + "</tbody></table></div>";
    },
    ziele() {
      return uebernehmenKnopf("Wünsche aus dem Vorab-Check übernehmen") + `<div class="card"><h2 style="margin-top:0">Ziele</h2>` +
        [1, 2, 3, 4, 5].map((i) => `<div class="row3">${feld("z" + i, "Ziel " + i, "text")}${feld("zb" + i, "Betrag in €")}${feld("zj" + i, "Bis Jahr")}</div>`).join("") +
        `</div><div class="card"><h2 style="margin-top:0">Notizen zum Gespräch</h2><textarea data-f="notizen" aria-label="Notizen" style="min-height:200px"></textarea>
        <p class="hint">Keine Gesundheitsdetails hier notieren.</p></div>`;
    },
    zugang() {
      const e = akte.einwilligung;
      return `<div class="card"><h2 style="margin-top:0">Kundenzugang</h2>${akte.kunde ? `<p>Aktiv: <b>${esc(akte.kunde.name)}</b> (${esc(akte.kunde.email)})</p>` :
        `<p class="hint">Noch kein Zugang. Erzeuge einen Einladungslink und schick ihn dem Kunden. Er ist 14 Tage gültig.</p>
        <div class="row">${feld("e_name", 'Vorname für die Anrede <span class="hint">sieht der Kunde</span>', "text")}${feld("e_email", "E-Mail", "email")}</div>
        <div class="nav" style="justify-content:flex-start"><button type="button" class="primary" id="einladen">Einladungslink erzeugen</button></div>
        <p id="einladung-link" class="info" hidden></p>`}
        <p>Einwilligung: ${e ? (e.widerrufen ? `<span class="err">widerrufen am ${datum(e.widerrufen)}</span>` : `erteilt am ${datum(e.zeit)} (Text ${esc(e.text_version)})`) : "keine"}</p></div>
        <div class="card"><h2 style="margin-top:0">Berater</h2><p>${akte.berater.map((b) => esc(b.name) + (b.bereich ? ` <span class="badge">${b.bereich}</span>` : "")).join(", ")}</p>
        <div class="row"><div><label for="zuordnen-wer">Weiteren Berater zuordnen</label><select id="zuordnen-wer"></select></div>
        <div style="align-self:end"><button type="button" class="quiet" id="zuordnen">Zuordnen</button></div></div></div>
        <div class="card"><h2 style="margin-top:0">Daten</h2><div class="nav" style="justify-content:flex-start">
        <button type="button" class="quiet" id="export">Akte exportieren (JSON)</button>
        <button type="button" class="danger" id="loeschen">Akte endgültig löschen</button></div>
        <p class="hint">Löschen entfernt alle Angaben und den Kundenzugang. Das lässt sich nicht rückgängig machen.</p></div>`;
    }
  };
  const BEW = { passt: "passt", pruefen: "prüfen", fehlt: "fehlt", nicht_noetig: "nicht nötig", kunde_lehnt_ab: "Kunde lehnt ab" };

  /* ---------- Tabs: Berechnung nach jeder Eingabe ---------- */
  const NACH = {
    haushalt() {
      const hr = haushaltRechnung(lies($("inhalt")));
      const r = hr && hr.rechnung;
      $("netto-erg").innerHTML = (r ? `<table><thead><tr><th>Person</th><th class="n">Brutto</th><th class="n">Sozialabgaben</th><th class="n">Lohnsteuer</th><th class="n">Soli + KiSt</th><th class="n">Netto/Monat</th></tr></thead><tbody>` +
        r.personen.map((p, i) => `<tr><td>${i + 1}</td><td class="n">${eur(p.brutto)}</td><td class="n">${eur(p.sozialabgaben)}</td><td class="n">${eur(p.est)}</td><td class="n">${eur(p.soli + p.kist)}</td><td class="n"><b>${eur(p.netto_monat)}</b></td></tr>`).join("") + "</tbody></table>" : "") +
        `<div class="kpi" style="margin-top:10px"><div><small>Haushaltsnetto</small><b>${eur(hr ? hr.netto_monat : 0)}</b></div><div><small>Kindergeld</small><b>${eur(hr ? hr.kindergeld : 0)}</b></div></div>`;
    },
    budget() {
      const b = budgetRechnung(lies($("inhalt")), haushaltRechnung(daten("haushalt")));
      $("budget-erg").innerHTML = b ? `<div><small>Einnahmen</small><b>${eur(b.einnahmen)}</b></div><div><small>Feste Ausgaben</small><b>${eur(b.fixkosten)}</b></div>
        <div><small>Überschuss I</small><b>${eur(b.ueberschuss1)}</b><small>${pct(b.quote1)}</small></div><div><small>Sparquote</small><b>${pct(b.sparquote)}</b></div>
        <div><small>Überschuss II</small><b>${eur(b.ueberschuss2)}</b><small>${pct(b.quote2)}</small></div>
        <div><small>Notreserve</small><b><span class="amp ${b.reserve_ampel}"></span>${b.reserve_monate == null ? "–" : b.reserve_monate.toLocaleString("de-DE", { maximumFractionDigits: 1 }) + " Monate"}</b></div>` : "";
    },
    vorsorge() {
      const h = daten("haushalt"), vs = vorsorgeRechnung(lies($("inhalt")), h, haushaltRechnung(h));
      $("vorsorge-erg").innerHTML = vs ? `<div><small>Wunsch</small><b>${eur(vs.wunsch)}</b></div><div><small>Lücke heute</small><b>${eur(vs.luecke)}</b><small>nominal ${eur(vs.luecke_nominal)}</small></div>
        <div><small>Kapitalbedarf</small><b>${eur(vs.kapital)}</b></div><div><small>Davon gedeckt</small><b>${eur(vs.vorhanden_real)}</b></div>
        <div><small>Sparrate</small><b>${eur(vs.sparrate)}</b><small>real ${(vs.real_anspar * 100).toLocaleString("de-DE", { maximumFractionDigits: 1 })} % p. a.</small></div>` : '<div><small>Für die Rechnung fehlen Alter (Tab Haushalt) oder Rentenbeginn.</small></div>';
    },
    risiko() {
      const rk = risikoRechnung(lies($("inhalt"))) || {};
      const ks = Object.keys(ARTEN).filter((k) => rk[k]).sort((a, z) => rk[z].quote - rk[a].quote);
      $("risiko-erg").innerHTML = ks.length ? "<thead><tr><th>Versicherungsart</th><th class='n'>Betroffenheit</th></tr></thead><tbody>" +
        ks.map((k) => `<tr><td><span class="amp ${rk[k].ampel}"></span>${ARTEN[k]}</td><td class="n">${pct(rk[k].quote)}</td></tr>`).join("") + "</tbody>" : "<tr><td class='hint'>Noch keine Antworten.</td></tr>";
    }
  };

  /* ---------- Tabs: Knöpfe ---------- */
  const BINDEN = {
    ueberblick() { $("drucken").addEventListener("click", () => window.print()); },
    haushalt() { uebernehmen((va) => {
      const p = va.person || {}, e = (va.einkommen && va.einkommen.eingaben) || [];
      const o = { familie: p.familie === "single" ? "allein" : p.familie, kinder_u25: p.kinder, kinder_kg: p.kinder, tiere: p.tiere, wohnen: p.wohnen, land: p.bundesland, alter1: p.alter };
      e.forEach((x, i) => { const n = i + 1; o["kv" + n] = x.kv; if (x.art === "brutto") o["brutto" + n] = x.betrag; else o["netto" + n] = x.betrag; if (x.pkv) o["pkv" + n] = x.pkv; if (i === 1) o.alter2 = x.alter; });
      if (p.vorname) o.name1 = p.vorname;
      return o; }); },
    budget() { uebernehmen((va) => Object.assign({}, va.fixkosten, { sparen: va.sparen, liquide: va.vermoegen && va.vermoegen.liquide, sonstige: va.einkommen && va.einkommen.sonstige })); },
    vorsorge() { uebernehmen((va) => ({ depot: va.vermoegen && va.vermoegen.depot, sonstverm: va.vermoegen && va.vermoegen.sonstiges,
      schulden: va.vermoegen && va.vermoegen.schulden, gesetzl: va.vermoegen && va.vermoegen.rente_erwartet, rentenalter: va.ruhestand_alter })); },
    ziele() { uebernehmen((va) => { const o = {}; (va.wuensche || []).forEach((w, i) => { o["z" + (i + 1)] = w.text; o["zj" + (i + 1)] = w.jahr || ""; }); if (va.sorge) o.notizen = "Sorge laut Vorab-Check: " + va.sorge; return o; }); },
    async zugang() {
      if ($("einladen")) $("einladen").addEventListener("click", async () => {
        const name = $("i_e_name").value.trim(), email = $("i_e_email").value.trim();
        if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { fehler("Bitte Name und gültige E-Mail angeben."); return; }
        try {
          const r = await api.post(`/api/akten/${akte.id}/einladung`, { name, email });
          const link = location.origin + r.pfad;
          $("einladung-link").hidden = false;
          $("einladung-link").innerHTML = `Link für ${esc(name)} (gültig ${r.gueltig_tage} Tage, wird nur jetzt angezeigt):<br><input type="text" readonly value="${esc(link)}" id="link-feld"> <button type="button" class="ghost" id="kopieren">Kopieren</button>`;
          $("kopieren").addEventListener("click", () => { $("link-feld").select(); navigator.clipboard && navigator.clipboard.writeText(link); });
          fehler();
        } catch (e) { fehler(e.message); }
      });
      const alle = await api.get("/api/berater");
      const schon = akte.berater.map((b) => b.id);
      $("zuordnen-wer").innerHTML = alle.filter((b) => !schon.includes(b.id)).map((b) => `<option value="${b.id}">${esc(b.name)}</option>`).join("") || "<option value=''>–</option>";
      $("zuordnen").addEventListener("click", async () => {
        const id = Number($("zuordnen-wer").value); if (!id) return;
        try { await api.post(`/api/akten/${akte.id}/berater`, { user_id: id }); oeffneAkte(akte.id, "zugang"); } catch (e) { fehler(e.message); }
      });
      $("export").addEventListener("click", async () => {
        const d = await api.get(`/api/akten/${akte.id}/export`);
        const url = URL.createObjectURL(new Blob([JSON.stringify(d, null, 2)], { type: "application/json" }));
        const a = document.createElement("a"); a.href = url; a.download = `akte-${akte.id}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 2000);
      });
      $("loeschen").addEventListener("click", async () => {
        if (prompt(`Zum Löschen den Namen der Akte eintippen: ${akte.titel}`) !== akte.titel) return;
        try { await api.del(`/api/akten/${akte.id}`); geaendert = false; zeigeListe(); } catch (e) { fehler(e.message); }
      });
    }
  };
  function uebernehmen(abbild) {
    const k = $("uebernehmen"); if (!k) return;
    k.addEventListener("click", () => {
      const o = abbild(vorab());
      Object.keys(o).forEach((x) => { if (o[x] === undefined || o[x] === null) delete o[x]; else o[x] = String(o[x]); });
      fuelle($("inhalt"), o); geaendert = true; $("speicher-status").textContent = "übernommen, noch nicht gespeichert";
      (NACH[tab] || (() => {}))();
    });
  }

  /* ---------- Start ---------- */
  $("speichern").addEventListener("click", speichern);
  // Eingaben einmalig überwachen (nicht je Tab neu anmelden)
  $("inhalt").addEventListener("input", (ev) => {
    const abschnitt = TABS.find(([k]) => k === tab)[2];
    if (abschnitt && ev.target.dataset && ev.target.dataset.f && !ev.target.dataset.f.startsWith("e_")) {
      geaendert = true; $("speicher-status").textContent = "nicht gespeichert";
    }
    (NACH[tab] || (() => {}))();
  });
  $("inhalt").addEventListener("change", () => (NACH[tab] || (() => {}))());
  $("zurueck").addEventListener("click", () => { if (!geaendert || confirm("Ungespeicherte Änderungen verwerfen?")) { geaendert = false; zeigeListe(); } });
  $("abmelden").addEventListener("click", async () => { await api.post("/api/logout"); location.href = "/"; });
  $("neu").addEventListener("click", () => { $("neu-form").hidden = false; $("neu-titel").focus(); });
  $("neu-abbruch").addEventListener("click", () => { $("neu-form").hidden = true; });
  $("neu-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const t = $("neu-titel").value.trim(); if (!t) return;
    try { const r = await api.post("/api/akten", { titel: t }); $("neu-form").hidden = true; $("neu-titel").value = ""; oeffneAkte(r.id, "zugang"); }
    catch (e) { fehler(e.message); }
  });
  window.addEventListener("beforeunload", (e) => { if (geaendert) { e.preventDefault(); e.returnValue = ""; } });

  (async function start() {
    try { ich = await api.get("/api/ich"); } catch (e) { location.href = "/"; return; }
    if (ich.rolle === "kunde") { location.href = "/kunde.html"; return; }
    $("wer").textContent = ich.name + (ich.bereich ? " · " + (ich.bereich === "versicherung" ? "Versicherung" : "Anlage") : "");
    const m = location.hash.match(/akte=(\d+)/);
    if (m) { try { await oeffneAkte(Number(m[1])); return; } catch (e) { fehler(e.message); } }
    zeigeListe().catch((e) => fehler(e.message));
  })();
})();
