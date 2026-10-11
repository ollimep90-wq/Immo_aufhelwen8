/* Kontoauszüge einlesen: CSV (alle gängigen Banken), CAMT.052/053 (XML) und PDF (über pdf.js, siehe kontoauszug_ui.js).
 * Läuft nur im Browser. Einzelne Buchungen verlassen das Gerät nicht; übernommen werden nur Monatssummen je Bereich.
 * Die Zuordnung zu Bereichen ist eine Schätzung nach Stichworten. Der Kunde prüft und korrigiert sie vor der Übernahme.
 * Getestet mit tests/test_kontoauszug.py (Node). */
(function (root) {
  "use strict";

  const BEREICHE = {
    wohnen: "Wohnen", essen: "Essen und Drogerie", mobil: "Mobilität", kinder: "Kinder", vers: "Versicherungen",
    vertr: "Verträge und Abos", kredit: "Kredite und Leasing", urlaub: "Urlaub und Freizeit", sonst: "Sonstiges",
    sparen: "Sparen und Anlegen", umbuchung: "Umbuchung zwischen eigenen Konten (zählt nicht)",
    gehalt: "Gehalt und Lohn", kindergeld: "Kindergeld", einnahme: "Weitere Einnahmen"
  };
  const AUSGABEN = ["wohnen", "essen", "mobil", "kinder", "vers", "vertr", "kredit", "urlaub", "sonst"];

  // Stichworte, klein geschrieben. Reihenfolge zählt: der erste Treffer gewinnt.
  const REGELN = [
    ["sonst", ["kreditkarte", "kreditkartenabrechnung", "paypal", "klarna"]],
    ["umbuchung", ["umbuchung", "übertrag", "uebertrag", "eigenes konto", "eigenübertrag", "kontoübertrag"]],
    ["sparen", ["sparplan", "wertpapier", "depot", "etf", "trade republic", "scalable", "bausparkasse", "bauspar", "tagesgeld", "festgeld"]],
    ["kindergeld", ["kindergeld", "familienkasse"]],
    ["gehalt", ["gehalt", "lohn", "bezüge", "bezuege", "entgelt", "besoldung", "lohn/gehalt"]],
    ["kredit", ["darlehen", "kredit", "leasing", "finanzierung", "tilgung", "ratenkauf", "santander", "targobank", "easycredit", "bank11"]],
    ["wohnen", ["miete", "nebenkosten", "hausgeld", "stadtwerke", "strom", "erdgas", "gasversorg", "wasser", "fernwärme", "e.on", "eon energie", "vattenfall",
      "enbw", "rwe", "eprimo", "grundsteuer", "rundfunk", "beitragsservice", "müllabfuhr", "abfall", "schornstein", "heizöl"]],
    ["vers", ["versicherung", "versich", "allianz", "huk", "axa", "ergo", "generali", "r+v", "debeka", "signal iduna", "devk", "lvm", "provinzial",
      "gothaer", "zurich", "barmenia", "hansemerkur", "continentale", "wgv", "cosmos", "haftpflicht", "hdi", "württembergische"]],
    ["vertr", ["telekom", "vodafone", "o2 ", "telefonica", "1&1", "congstar", "netflix", "spotify", "amazon prime", "disney", "dazn", "sky deutschland",
      "apple.com", "icloud", "google one", "youtube premium", "fitness", "mcfit", "urban sports", "clever fit", "fitx", "verein", "zeitung", "abo"]],
    ["kinder", ["kita", "kindergarten", "kindertages", "schulgeld", "schule", "musikschule", "hort", "tagesmutter", "babysitter", "nachhilfe"]],
    ["mobil", ["aral", "shell", "esso", "jet tankstelle", "tankstelle", "totalenergies", "deutsche bahn", "db vertrieb", "db fernverkehr", "bvg", "mvg",
      "kvb", "hvv", "rmv", "vrr", "deutschlandticket", "flixbus", "uber", "parkhaus", "parken", "kfz-steuer", "hauptzollamt", "adac", "tüv", "dekra",
      "werkstatt", "autohaus", "carsharing", "share now", "miles mobility"]],
    ["essen", ["rewe", "edeka", "aldi", "lidl", "netto marken", "netto filiale", "penny", "kaufland", "dm-drogerie", "dm drogerie", "rossmann",
      "müller drogerie", "mueller drogerie", "globus", "tegut", "norma", "denns", "alnatura", "bäckerei", "baeckerei", "metzgerei", "supermarkt", "hellofresh", "flink", "getir"]],
    ["urlaub", ["hotel", "booking.com", "airbnb", "lufthansa", "ryanair", "eurowings", "condor", "tui", "expedia", "restaurant", "kino", "eventim",
      "lieferando", "wolt", "theater", "museum", "ferien", "reise"]]
  ];

  const klein = (s) => String(s || "").toLowerCase();
  // Kurze Stichworte nur als ganzes Wort (sonst trifft „tui“ in „Intuition“ oder „ergo“ in „Bergold“)
  const L = "a-z0-9äöüß";
  const trifft = (t, w) => w.length > 5 || /[ .&+]/.test(w) ? t.includes(w) : new RegExp(`(^|[^${L}])${w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}($|[^${L}])`).test(t);
  function kategorie(b) {
    const t = klein(b.name + " " + b.zweck);
    if (b.betrag > 0 && /(^|[^a-zäöüß])miete/.test(t) && !/erstattung|rückzahlung|nebenkostenabrechnung/.test(t)) return "einnahme";
    for (const [k, worte] of REGELN) {
      if (worte.some((w) => trifft(t, w))) {
        if (b.betrag > 0 && AUSGABEN.includes(k)) return k;            // Erstattung: mindert den Bereich
        if (b.betrag < 0 && ["gehalt", "kindergeld"].includes(k)) continue;
        return k;
      }
    }
    if (/bargeld|geldautomat|\bgaa\b|auszahlung atm|cash/.test(t)) return "sonst";
    return b.betrag > 0 ? "einnahme" : "sonst";
  }

  /* ---------- Zahlen und Daten ---------- */
  function zahlDE(s) {
    let t = String(s == null ? "" : s).trim().replace(/\s|€|EUR/gi, "");
    if (!t) return null;
    let neg = false;
    if (/^-|-$/.test(t)) { neg = true; t = t.replace(/^-|-$/g, ""); }
    if (/^\+|\+$/.test(t)) t = t.replace(/^\+|\+$/g, "");
    // 1.234,56 oder 1234,56 → deutsch; 1,234.56 oder 1234.56 → englisch
    if (/,\d{1,2}$/.test(t)) t = t.replace(/\./g, "").replace(",", ".");
    else t = t.replace(/,/g, "");
    const n = Number(t);
    return isFinite(n) ? (neg ? -n : n) : null;
  }
  function datum(s) {
    const t = String(s || "").trim();
    let m = t.match(/^(\d{1,2})\.(\d{1,2})\.(\d{2,4})/);
    if (m) { let j = Number(m[3]); if (j < 100) j += 2000; return `${j}-${String(m[2]).padStart(2, "0")}-${String(m[1]).padStart(2, "0")}`; }
    m = t.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (m) return `${m[1]}-${m[2]}-${m[3]}`;
    return null;
  }

  /* ---------- Text aus Datei ---------- */
  function dekodiere(buffer) {
    const b = new Uint8Array(buffer);
    try { return new TextDecoder("utf-8", { fatal: true }).decode(b).replace(/^﻿/, ""); }
    catch (e) { return new TextDecoder("windows-1252").decode(b); }
  }

  /* ---------- CSV ---------- */
  function zeilenCSV(text, trenner) {
    const zeilen = []; let feld = "", zeile = [], inQ = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (inQ) { if (c === '"') { if (text[i + 1] === '"') { feld += '"'; i++; } else inQ = false; } else feld += c; continue; }
      if (c === '"') inQ = true;
      else if (c === trenner) { zeile.push(feld); feld = ""; }
      else if (c === "\n" || c === "\r") { if (c === "\r" && text[i + 1] === "\n") i++; zeile.push(feld); zeilen.push(zeile); zeile = []; feld = ""; }
      else feld += c;
    }
    if (feld || zeile.length) { zeile.push(feld); zeilen.push(zeile); }
    return zeilen.map((z) => z.map((f) => f.trim()));
  }
  const SPALTEN = {
    datum: [/^buchungstag$/, /^buchungsdatum$/, /^buchung$/, /^datum$/, /^valuta/, /^wertstellung/, /^booking date/, /^date$/],
    betrag: [/^betrag/, /^umsatz/, /^amount/, /^betrag \(eur\)/, /^betrag \(€\)/],
    soll: [/^soll/, /^ausgang/, /^belastung/], haben: [/^haben/, /^eingang/, /^gutschrift/],
    kz: [/^soll\/haben$/, /^s\/h$/],
    name: [/beguenstigter|begünstigter|zahlungspflichtiger|auftraggeber|empfänger|empfaenger|name|zahlungsbeteiligter|gegenkonto.*name|payee|counterparty/],
    empf: [/empfänger|empfaenger|begünstigter|beguenstigter|payee/], zahler: [/zahlungspflichtig|auftraggeber|payer/],
    zweck: [/verwendungszweck/, /beschreibung|description|purpose|details/, /buchungstext|vorgang/], art: [/^buchungstext$|^vorgang$|^umsatzart$|^umsatztyp$/]
  };
  function finde(kopf, muster) {
    const k = kopf.map(klein);
    for (const m of muster) { const i = k.findIndex((x) => m.test(x)); if (i >= 0) return i; }
    return -1;
  }
  function leseCSV(text) {
    const probe = text.split(/\r?\n/).slice(0, 40).join("\n");
    const trenner = [";", ",", "\t"].map((t) => [t, (probe.match(new RegExp(t === "\t" ? "\\t" : t, "g")) || []).length]).sort((a, b) => b[1] - a[1])[0][0];
    const zeilen = zeilenCSV(text, trenner);
    // Kopfzeile: erste Zeile mit Datums- und Betragsspalte (Banken setzen oft Kontoinfos davor)
    let kz = -1, sp = null;
    for (let i = 0; i < Math.min(zeilen.length, 40); i++) {
      const k = zeilen[i];
      const d = finde(k, SPALTEN.datum), b = finde(k, SPALTEN.betrag), s = finde(k, SPALTEN.soll), h = finde(k, SPALTEN.haben);
      if (d >= 0 && (b >= 0 || (s >= 0 && h >= 0))) { kz = i; sp = { d, b, s, h, kz: finde(k, SPALTEN.kz), n: finde(k, SPALTEN.name), z: finde(k, SPALTEN.zweck),
        empf: finde(k, SPALTEN.empf), zahler: finde(k, SPALTEN.zahler), art: finde(k, SPALTEN.art) }; break; }
    }
    if (kz < 0) throw new Error("In der CSV-Datei wurden keine Spalten für Datum und Betrag gefunden.");
    // Spalte „Soll/Haben“ darf nicht als Soll-Spalte zählen
    if (sp.kz >= 0 && sp.s === sp.kz) sp.s = -1;
    const out = [];
    for (const z of zeilen.slice(kz + 1)) {
      const d = datum(z[sp.d]);
      if (!d) continue;
      let betrag = null;
      if (sp.b >= 0 && z[sp.b] !== "" && z[sp.b] != null) {
        betrag = zahlDE(z[sp.b]);
        if (betrag != null && sp.kz >= 0 && /^s/i.test(z[sp.kz] || "")) betrag = -Math.abs(betrag);
      } else if (sp.s >= 0 || sp.h >= 0) {
        const s = sp.s >= 0 ? zahlDE(z[sp.s]) : null, h = sp.h >= 0 ? zahlDE(z[sp.h]) : null;
        betrag = (h || 0) - Math.abs(s || 0);
      }
      if (betrag == null || betrag === 0) continue;
      // getrennte Spalten für Zahler und Empfänger (z. B. DKB): bei Ausgaben zählt der Empfänger, bei Eingängen der Zahler
      const ni = sp.empf >= 0 && sp.zahler >= 0 && sp.empf !== sp.zahler ? (betrag < 0 ? sp.empf : sp.zahler) : sp.n;
      // Zweck: Verwendungszweck, dazu die Buchungsart (z. B. „Umbuchung“), wenn es dafür eine eigene Spalte gibt
      const zweck = [sp.z >= 0 ? z[sp.z] : "", sp.art >= 0 && sp.art !== sp.z ? z[sp.art] : ""].filter(Boolean).join(" ");
      out.push({ datum: d, betrag, name: ni >= 0 ? z[ni] || "" : "", zweck });
    }
    return out;
  }

  /* ---------- CAMT.052/053 (XML) ---------- */
  function leseCAMT(xml) {
    const tag = (s, n) => { const m = s.match(new RegExp("<(?:\\w+:)?" + n + "(?:\\s[^>]*)?>([\\s\\S]*?)</(?:\\w+:)?" + n + ">")); return m ? m[1] : ""; };
    const ent = (s) => s.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/\s+/g, " ").trim();
    const out = [];
    const re = /<(?:\w+:)?Ntry(?:\s[^>]*)?>([\s\S]*?)<\/(?:\w+:)?Ntry>/g;
    let m;
    while ((m = re.exec(xml))) {
      const e = m[1];
      const betrag = Number(ent(tag(e, "Amt")));
      if (!isFinite(betrag) || !betrag) continue;
      const soll = ent(tag(e, "CdtDbtInd")) === "DBIT";
      const d = datum(ent(tag(tag(e, "BookgDt"), "Dt")) || ent(tag(tag(e, "BookgDt"), "DtTm")) || ent(tag(tag(e, "ValDt"), "Dt")));
      if (!d) continue;
      const parteien = tag(e, "RltdPties");
      const name = ent(tag(tag(parteien, soll ? "Cdtr" : "Dbtr"), "Nm")) || ent(tag(parteien, "Nm"));
      const zweck = ent(tag(e, "Ustrd")) || ent(tag(e, "AddtlNtryInf"));
      out.push({ datum: d, betrag: soll ? -betrag : betrag, name, zweck });
    }
    if (!out.length && !/<(?:\w+:)?Ntry/.test(xml)) throw new Error("Die XML-Datei ist kein CAMT-Kontoauszug.");
    return out;
  }

  /* ---------- PDF: Zeilen (aus pdf.js) → Buchungen ----------
   * Gängiges Muster: Zeile beginnt mit Datum, endet mit Betrag (mit Vorzeichen, „-“/„+“ dahinter oder S/H).
   * Folgezeilen ohne Datum gehören zum Text der Buchung. Ohne erkennbares Vorzeichen gilt die Buchung als unsicher. */
  function lesePDFZeilen(zeilen) {
    const out = []; let akt = null;
    const betragRe = /([+-]?\s?\d{1,3}(?:\.\d{3})*,\d{2}|[+-]?\d+,\d{2})\s*([+-]|S|H|Soll|Haben)?\s*(?:EUR|€)?\s*$/;
    for (const roh of zeilen) {
      const z = roh.replace(/\s+/g, " ").trim();
      if (!z) continue;
      if (/kontostand|saldo|übertrag aus|uebertrag aus|summe|seite \d/i.test(z) && !/^\d{1,2}\.\d{1,2}\.\d{2,4}.*(lastschrift|überweisung|gutschrift)/i.test(z)) { akt = null; continue; }
      const d = z.match(/^(\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2}))\b/);
      const b = z.match(betragRe);
      if (d && b) {
        let roh2 = b[1].replace(/\s/g, ""), wert = zahlDE(roh2.replace(/^[+-]/, "")) || 0, vz = b[2] || (roh2[0] === "-" || roh2[0] === "+" ? roh2[0] : "");
        const sicher = !!vz;
        if (vz === "-" || /^s/i.test(vz)) wert = -wert;
        else if (!vz) wert = /gutschrift|lohn|gehalt|eingang|überweisungseingang|zahlungseingang/i.test(z) ? wert : -wert;
        let text = z.slice(d[0].length, z.length - b[0].length).replace(/^\s*\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2})?\s*/, "").trim();
        akt = { datum: datum(d[1]), betrag: wert, name: text, zweck: "", unsicher: !sicher };
        out.push(akt);
      } else if (akt && !d) {
        akt.zweck = (akt.zweck + " " + z).trim().slice(0, 300);
      } else akt = null;
    }
    return out.filter((x) => x.datum && x.betrag);
  }

  /* ---------- Auswertung ---------- */
  // Gruppierung nach Empfänger/Absender, ohne Buchungsart davor (PDF: „Dauerauftrag Hausverwaltung Nord“ = „Hausverwaltung Nord“)
  const ART = /^(sepa[- ]?)?(basis-?|folge-?|erst-?)?(lastschrift|dauerauftrag|gutschrift|überweisung|ueberweisung|kartenzahlung|kartenumsatz|echtzeitüberweisung|zahlungseingang|zahlungsausgang|dauerauftrag)\s+/i;
  const schluessel = (b) => klein(String(b.name || b.zweck).replace(ART, "")).replace(/\d{4,}/g, "").replace(/[^a-zäöüß&+. ]/g, " ").replace(/\s+/g, " ").trim().slice(0, 40) || "(ohne Namen)";
  function auswerten(buchungen, zuordnung) {
    zuordnung = zuordnung || {};
    // Doppelte entfernen (mehrere Dateien mit überlappendem Zeitraum)
    const seen = new Set(), liste = [];
    buchungen.forEach((b) => { const k = [b.datum, b.betrag.toFixed(2), klein(b.name), klein(b.zweck)].join("|"); if (!seen.has(k)) { seen.add(k); liste.push(b); } });
    if (!liste.length) return null;
    const ms = (iso) => iso.slice(0, 7);
    const tage = liste.map((b) => Date.parse(b.datum + "T00:00:00Z")).filter(isFinite);
    const von = Math.min(...tage), bis = Math.max(...tage);
    const tageSpanne = (bis - von) / 86400000 + 1;
    // Angebrochene Monate am Anfang und Ende (erste Buchung nach dem 5., letzte mehr als 5 Tage vor Monatsende) zählen nicht mit,
    // solange es mindestens einen vollen Monat gibt. Sonst würden Miete und Gehalt doppelt oder variable Ausgaben zu niedrig gezählt.
    const d0 = new Date(von), d1 = new Date(bis);
    const letzterTag = new Date(Date.UTC(d1.getUTCFullYear(), d1.getUTCMonth() + 1, 0)).getUTCDate();
    const alleMonate = (d1.getUTCFullYear() - d0.getUTCFullYear()) * 12 + d1.getUTCMonth() - d0.getUTCMonth() + 1;
    const raus = [];
    if (d0.getUTCDate() > 5) raus.push(ms(d0.toISOString()));
    if (d1.getUTCDate() < letzterTag - 5) raus.push(ms(d1.toISOString()));
    const ausgelassen = Array.from(new Set(raus));
    let monate = alleMonate - ausgelassen.length, basis = liste;
    if (monate >= 1) basis = liste.filter((b) => !ausgelassen.includes(ms(b.datum)));
    else { monate = Math.max(1, Math.round(tageSpanne / 30.44)); ausgelassen.length = 0; }
    const gruppen = {};
    basis.forEach((b) => {
      const g = schluessel(b);
      const x = gruppen[g] = gruppen[g] || { schluessel: g, name: b.name || b.zweck || "(ohne Namen)", summe: 0, anzahl: 0, vorschlag: kategorie(b), unsicher: false };
      x.summe += b.betrag; x.anzahl++; if (b.unsicher) x.unsicher = true;
    });
    const summen = {};
    Object.keys(BEREICHE).forEach((k) => { summen[k] = 0; });
    Object.values(gruppen).forEach((g) => { g.kategorie = zuordnung[g.schluessel] || g.vorschlag; summen[g.kategorie] += g.summe; });
    const monat = {};
    Object.keys(summen).forEach((k) => { const v = summen[k] / monate; monat[k] = AUSGABEN.includes(k) || k === "sparen" ? Math.max(0, Math.round(-v)) : Math.round(v); });
    return { anzahl: basis.length, gesamt: liste.length, von: new Date(von).toISOString().slice(0, 10), bis: new Date(bis).toISOString().slice(0, 10), monate,
      gruppen: Object.values(gruppen).sort((a, b) => Math.abs(b.summe) - Math.abs(a.summe)), monat, unsicher: liste.filter((b) => b.unsicher).length,
      kurz: tageSpanne < 25, ausgelassen };
  }

  const api = { BEREICHE, AUSGABEN, kategorie, zahlDE, datum, dekodiere, leseCSV, leseCAMT, lesePDFZeilen, auswerten };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Kontoauszug = api;
})(this);
