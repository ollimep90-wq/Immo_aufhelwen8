/* Rechenkern Vorab-Check (Privat).
 * Läuft im Browser und unter Node (Tests: test_rechenkern.py vergleicht mit einer
 * unabhängigen Python-Umsetzung).
 *
 * Netto aus Brutto ist eine NÄHERUNG für Angestellte: Jahresbetrachtung,
 * Lohnsteuer ohne Kinderfreibetrag (wie auf der Gehaltsabrechnung),
 * Soli und Kirchensteuer mit Kinderfreibetrag. Nicht abgebildet: Steuerklassen III/V,
 * Freibeträge, geldwerte Vorteile, Minijob, Beamte, Selbstständige.
 */
(function (root) {
  "use strict";

  // Rechengrößen 2026. Quellen siehe vorab-check/QUELLEN.md
  const P2026 = {
    jahr: 2026,
    grundfreibetrag: 12348,          // § 32a EStG
    tarif: { z2: 17799, z3: 69878, z4: 277825,
             a2: 914.51, b2: 1400, a3: 173.10, b3: 2397, c3: 1034.87,
             s4: 0.42, k4: 11135.63, s5: 0.45, k5: 19470.38 },
    an_pauschbetrag: 1230,
    sonderausgaben_pauschbetrag: 36,
    kinderfreibetrag: 9756,          // Freibeträge für Kinder § 32 Abs. 6 je Kind, zusammenveranlagt
    entlastung_alleinerziehend: 4260, // § 24b EStG, Steuerklasse II
    kindergeld_monat: 259,
    soli: { freigrenze: 20350, satz: 0.055, milderung: 0.119 },
    kist: { BY: 0.08, BW: 0.08, sonst: 0.09 },
    bbg_kv: 69750, bbg_rv: 101400,
    kv_satz: 0.146, kv_satz_ermaessigt: 0.14, zusatzbeitrag_schnitt: 0.029,
    pv_satz: 0.036, pv_an_sachsen_plus: 0.005, pv_kinderlos: 0.006,
    pv_abschlag_je_kind: 0.0025, pv_abschlag_max_kinder: 5,
    rv_satz: 0.186, av_satz: 0.026,
    vsp_grenze_sonstige: 1900
  };

  const r2 = (x) => Math.round(x * 100) / 100;

  function tarif(zve, p) {
    const t = p.tarif, x = Math.floor(Math.max(0, zve));
    let st;
    if (x <= p.grundfreibetrag) st = 0;
    else if (x <= t.z2) { const y = (x - p.grundfreibetrag) / 10000; st = (t.a2 * y + t.b2) * y; }
    else if (x <= t.z3) { const z = (x - t.z2) / 10000; st = (t.a3 * z + t.b3) * z + t.c3; }
    else if (x <= t.z4) st = t.s4 * x - t.k4;
    else st = t.s5 * x - t.k5;
    return Math.floor(st);
  }

  function est(zve, verheiratet, p) {
    return verheiratet ? 2 * tarif(zve / 2, p) : tarif(zve, p);
  }

  /* Sozialabgaben Arbeitnehmer pro Jahr.
   * person: {brutto, kv:'gkv'|'pkv', pkv_eigenanteil_monat, zusatzbeitrag, alter, kinder_u25, sachsen} */
  function sozialabgaben(person, p) {
    const b = person.brutto;
    const bkv = Math.min(b, p.bbg_kv), brv = Math.min(b, p.bbg_rv);
    const rv = brv * p.rv_satz / 2, av = brv * p.av_satz / 2;
    let kv = 0, pv = 0, kv_vsp = 0;
    if (person.kv === "pkv") {
      kv = (person.pkv_eigenanteil_monat || 0) * 12;   // KV+PV nach Arbeitgeberzuschuss
      kv_vsp = kv;
    } else {
      const zb = person.zusatzbeitrag != null ? person.zusatzbeitrag : p.zusatzbeitrag_schnitt;
      kv = bkv * (p.kv_satz + zb) / 2;
      kv_vsp = bkv * (p.kv_satz_ermaessigt + zb) / 2;
      let pvsatz = p.pv_satz / 2 + (person.sachsen ? p.pv_an_sachsen_plus : 0);
      const k = person.kinder_u25 || 0;
      if (k === 0 && !person.eltern && (person.alter || 0) >= 23) pvsatz += p.pv_kinderlos;
      if (k >= 2) pvsatz -= (Math.min(k, p.pv_abschlag_max_kinder) - 1) * p.pv_abschlag_je_kind;
      pv = bkv * pvsatz;
    }
    return { kv: r2(kv), pv: r2(pv), rv: r2(rv), av: r2(av), summe: r2(kv + pv + rv + av),
             kv_vsp: r2(kv_vsp) };
  }

  function vorsorgepauschale(sv, person) {
    const kvpv = sv.kv_vsp + (person.kv === "pkv" ? 0 : sv.pv);
    const av_teil = Math.max(0, Math.min(sv.av, P2026.vsp_grenze_sonstige - kvpv));
    return sv.rv + kvpv + av_teil;
  }

  /* Haushalt: personen = [p1, p2?] mit brutto>0; verheiratet → Splitting.
   * Ergebnis je Person und gesamt, Jahreswerte. */
  function nettoHaushalt(h, p) {
    p = p || P2026;
    const kist = h.kirche ? (p.kist[h.bundesland] || p.kist.sonst) : 0;
    const personen = h.personen.filter((x) => x && x.brutto > 0);
    const rows = personen.map((x) => {
      const sv = sozialabgaben(x, p);
      const entl = !h.verheiratet && h.alleinerziehend ? p.entlastung_alleinerziehend : 0;
      const zve = Math.max(0, x.brutto - p.an_pauschbetrag - p.sonderausgaben_pauschbetrag - vorsorgepauschale(sv, x) - entl);
      return { brutto: x.brutto, sv, zve: r2(zve) };
    });
    const kfb_gesamt = (h.kinder || 0) * p.kinderfreibetrag;
    let steuer = [];
    if (h.verheiratet) {
      const zve = rows.reduce((a, r) => a + r.zve, 0);
      const e = est(zve, true, p);
      const e_kfb = est(Math.max(0, zve - kfb_gesamt), true, p);
      const fg = 2 * p.soli.freigrenze;
      const soli = e_kfb > fg ? Math.min(e_kfb * p.soli.satz, (e_kfb - fg) * p.soli.milderung) : 0;
      const k = e_kfb * kist;
      // Aufteilung nach Anteil am zvE (Näherung für die Anzeige je Person)
      rows.forEach((r) => {
        const a = zve > 0 ? r.zve / zve : 1 / rows.length;
        steuer.push({ est: e * a, soli: soli * a, kist: k * a });
      });
    } else {
      rows.forEach((r) => {
        // Nicht zusammenveranlagt: je Elternteil der halbe Kinderfreibetrag (Regelfall)
        const kfb = kfb_gesamt / 2;
        const e = est(r.zve, false, p);
        const e_kfb = est(Math.max(0, r.zve - kfb), false, p);
        const fg = p.soli.freigrenze;
        const soli = e_kfb > fg ? Math.min(e_kfb * p.soli.satz, (e_kfb - fg) * p.soli.milderung) : 0;
        steuer.push({ est: e, soli, kist: e_kfb * kist });
      });
    }
    const out = rows.map((r, i) => {
      const s = steuer[i];
      const netto = r.brutto - r.sv.summe - s.est - s.soli - s.kist;
      return { brutto: r.brutto, sozialabgaben: r.sv.summe, est: r2(s.est), soli: r2(s.soli),
               kist: r2(s.kist), netto_jahr: r2(netto), netto_monat: r2(netto / 12), zve: r.zve };
    });
    const netto_jahr = out.reduce((a, x) => a + x.netto_jahr, 0);
    return { personen: out, netto_jahr: r2(netto_jahr), netto_monat: r2(netto_jahr / 12) };
  }

  /* Risiko-Kurzcheck. antworten: {frageId: 0..4 | null (trifft nicht zu)}
   * fragen: [{id, block, gewichte:{art: 0..3}}]. Wertung wie im Excel-Prototyp:
   * je Block Mittelwert(gewicht × punkte) / Mittelwert(gewicht × 4), über Blöcke summiert. */
  function risikoAuswertung(fragen, antworten) {
    const proBlock = {};
    fragen.forEach((f) => {
      const a = antworten[f.id];
      if (a === null || a === undefined) return;
      (proBlock[f.block] = proBlock[f.block] || []).push({ f, a });
    });
    const ist = {}, max = {};
    Object.values(proBlock).forEach((liste) => {
      const n = liste.length;
      liste.forEach(({ f, a }) => {
        Object.entries(f.gewichte).forEach(([art, w]) => {
          ist[art] = (ist[art] || 0) + (w * a) / n;
          max[art] = (max[art] || 0) + (w * 4) / n;
        });
      });
    });
    const ergebnis = {};
    Object.keys(max).forEach((art) => {
      if (max[art] <= 0) return;
      const q = ist[art] / max[art];
      ergebnis[art] = { quote: q, ampel: q >= 0.6 ? "rot" : q >= 0.3 ? "gelb" : q > 0 ? "gruen" : "keine" };
    });
    return ergebnis;
  }

  function budget(b) {
    const einnahmen = b.netto_monat + (b.kindergeld_monat || 0) + (b.sonstige_einnahmen || 0);
    const u1 = einnahmen - b.fixkosten;
    const u2 = u1 - b.sparen;
    const reserveMonate = b.fixkosten > 0 ? b.liquide / b.fixkosten : null;
    return {
      einnahmen: r2(einnahmen), ueberschuss1: r2(u1), quote1: einnahmen > 0 ? u1 / einnahmen : 0,
      ueberschuss2: r2(u2), quote2: einnahmen > 0 ? u2 / einnahmen : 0,
      sparquote: einnahmen > 0 ? b.sparen / einnahmen : 0,
      reserve_monate: reserveMonate,
      reserve_ampel: reserveMonate === null ? "keine" : reserveMonate < 1 ? "rot" : reserveMonate < 3 ? "gelb" : "gruen"
    };
  }

  const api = { P2026, tarif, est, sozialabgaben, nettoHaushalt, risikoAuswertung, budget };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.Rechenkern = api;
})(this);
