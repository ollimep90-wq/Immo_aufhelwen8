/* DEMO-Ersatz für den Server der Beratungs-App.
 * Läuft nur im Browser, mit erfundenen Daten. Ahmt die Antworten und Rechte von server/app.py nach,
 * aber ohne echte Sicherheit: keine Passwort-Hashes, keine echte Zwei-Faktor-Prüfung, keine Verschlüsselung.
 * Zustand: localStorage dieses Browsers (Ersatz: window.name), „Demo zurücksetzen“ stellt den Anfang wieder her. */
(function () {
  "use strict";
  const SEED = /*SEED*/null;
  const QR = /*QR*/"";
  const GEHEIMNIS = "DEMODEMODEMODEMODEMODEMODEMODEMO";
  const EINW_VERSION = "2026-10-v3";
  const KEY = "beratungs-demo-v1";
  const TAG = 86400;

  /* ---------- Zustand ---------- */
  function frisch() {
    const s = JSON.parse(JSON.stringify(SEED));
    // Zeiten so verschieben, dass die letzte Änderung zwei Stunden her ist
    let max = 0;
    const lauf = (o, f) => { if (o && typeof o === "object") Object.keys(o).forEach((k) => {
      if (typeof o[k] === "number" && o[k] > 1.6e9 && /^(erstellt|geaendert|zeit|freigegeben_am|widerrufen)$/.test(k)) f(o, k); else lauf(o[k], f); }); };
    lauf(s, (o, k) => { max = Math.max(max, o[k]); });
    const delta = Date.now() / 1000 - 7200 - max;
    lauf(s, (o, k) => { o[k] += delta; });
    s.users.forEach((u) => { u.pw = "demo"; u.totp = false; u.aktiv = true; });
    s.einladungen = []; s.sitzung = null; s.einladungOffen = null;
    s.naechste = { akte: Math.max(...s.akten.map((a) => a.id)) + 1, user: Math.max(...s.users.map((u) => u.id)) + 1 };
    return s;
  }
  function laden() {
    try { const t = localStorage.getItem(KEY); if (t) return JSON.parse(t); } catch (e) { /* ohne Speicher weiter */ }
    try { if (window.name && window.name.indexOf(KEY) === 0) return JSON.parse(window.name.slice(KEY.length)); } catch (e) { /* ignorieren */ }
    return frisch();
  }
  let st = laden();
  function sichern() {
    const t = JSON.stringify(st);
    try { localStorage.setItem(KEY, t); } catch (e) { /* ignorieren */ }
    try { window.name = KEY + t; } catch (e) { /* ignorieren */ }
  }
  sichern();

  /* ---------- Hilfen ---------- */
  class F extends Error { constructor(status, text) { super(text); this.status = status; } }
  const jetzt = () => Date.now() / 1000;
  const user = (id) => st.users.find((u) => u.id === id && u.aktiv);
  const akteById = (id) => st.akten.find((a) => a.id === id);
  const abschnitt = (akteId, k) => { const a = st.abschnitte.find((x) => x.akte_id === akteId && x.schluessel === k);
    return a ? { daten: a.daten, version: a.version, geaendert: a.geaendert, geaendert_von: a.geaendert_von } : null; };
  const akteDaten = (id) => Object.fromEntries(st.abschnitte.filter((x) => x.akte_id === id).map((x) => [x.schluessel, abschnitt(id, x.schluessel)]));
  const zufall = (n) => Array.from(crypto.getRandomValues(new Uint8Array(n)), (b) => "abcdefghijkmnpqrstuvwxyz23456789"[b % 32]).join("");
  function ich() {
    const s = st.sitzung; const u = s && s.stufe === "fertig" && user(s.uid);
    if (!u) throw new F(401, "Bitte melde dich an.");
    return u;
  }
  function nur(...rollen) { const u = ich(); if (!rollen.includes(u.rolle)) throw new F(403, "Keine Berechtigung"); return u; }
  function akteFuer(u, id) {
    const a = akteById(id);
    if (!a) throw new F(404, "Akte nicht gefunden");
    if (u.rolle === "admin") return a;
    if (u.rolle === "berater" && st.akte_berater.some((b) => b.akte_id === id && b.user_id === u.id)) return a;
    throw new F(404, "Akte nicht gefunden");
  }
  const darfVerwalten = (u, a) => u.rolle === "admin" || a.erstellt_von === u.id;
  const einwilligung = (akteId) => st.einwilligungen.filter((e) => e.akte_id === akteId).sort((a, b) => b.zeit - a.zeit)[0] || null;
  const aktiveEinw = (akteId, uid) => st.einwilligungen.filter((e) => e.akte_id === akteId && e.user_id === uid && !e.widerrufen).sort((a, b) => b.zeit - a.zeit)[0] || null;
  function speichernOder409(akteId, k, daten, uid, version, text) {
    const a = st.abschnitte.find((x) => x.akte_id === akteId && x.schluessel === k);
    if (version == null) {
      if (a) throw new F(409, text);
      st.abschnitte.push({ akte_id: akteId, schluessel: k, daten, version: 1, geaendert: jetzt(), geaendert_von: uid });
      akteById(akteId).geaendert = jetzt(); return 1;
    }
    if (!a || a.version !== version) throw new F(409, text);
    a.daten = daten; a.version += 1; a.geaendert = jetzt(); a.geaendert_von = uid; akteById(akteId).geaendert = jetzt();
    return a.version;
  }
  function akteLesen(u, id) {
    const a = Object.assign({}, akteFuer(u, id));
    a.abschnitte = akteDaten(id);
    a.berater = st.akte_berater.filter((b) => b.akte_id === id).map((b) => user(b.user_id)).filter(Boolean).map((x) => ({ id: x.id, name: x.name, bereich: x.bereich }));
    const e = einwilligung(id); a.einwilligung = e ? { text_version: e.text_version, zeit: e.zeit, widerrufen: e.widerrufen || null } : null;
    const k = a.kunde_id && user(a.kunde_id); a.kunde = k ? { name: k.name, email: k.email } : null;
    a.darf_verwalten = darfVerwalten(u, a);
    return a;
  }
  function kanonisch(x) {
    if (Array.isArray(x)) return "[" + x.map(kanonisch).join(",") + "]";
    if (x && typeof x === "object") return "{" + Object.keys(x).sort().map((k) => JSON.stringify(k) + ":" + kanonisch(x[k])).join(",") + "}";
    return JSON.stringify(x);
  }
  async function sha256(t) {
    try { const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)); return Array.from(new Uint8Array(h), (b) => b.toString(16).padStart(2, "0")).join(""); }
    catch (e) { return "in dieser Ansicht nicht verfügbar"; }
  }
  const eigeneAkte = (u) => { const a = st.akten.find((x) => x.kunde_id === u.id); if (!a) throw new F(404, "Für deinen Zugang ist noch nichts angelegt. Bitte melde dich bei uns."); return a; };
  const basis = () => location.pathname.replace(/[^/]*$/, "");

  /* ---------- Routen ---------- */
  async function route(m, pfad, d) {
    const [p, q] = pfad.split("?");
    let t;
    if (m === "POST" && p === "/api/login") {
      const u = st.users.find((x) => x.aktiv && x.email === String(d.email || "").trim().toLowerCase());
      if (!u || d.passwort !== u.pw) throw new F(401, "E-Mail oder Passwort falsch");
      if (u.rolle === "kunde") { st.sitzung = { uid: u.id, stufe: "fertig" }; return { schritt: "fertig", rolle: u.rolle, name: u.name }; }
      st.sitzung = { uid: u.id, stufe: u.totp ? "2fa" : "2fa_einrichten" };
      return { schritt: st.sitzung.stufe, name: u.name };
    }
    if (m === "POST" && p === "/api/2fa/einrichten") {
      if (!st.sitzung || st.sitzung.stufe !== "2fa_einrichten") throw new F(401, "Bitte melde dich erneut an.");
      return { geheimnis: GEHEIMNIS, uri: "otpauth://totp/Demo", qr: QR };
    }
    if (m === "POST" && p === "/api/2fa/bestaetigen") {
      if (!st.sitzung || st.sitzung.stufe !== "2fa_einrichten") throw new F(409, "Bitte starte die Einrichtung neu.");
      if (!/^\d{6}$/.test(String(d.code || "").trim())) throw new F(401, "Der Code stimmt nicht. In der Demo reicht jede 6-stellige Zahl.");
      const u = user(st.sitzung.uid); u.totp = true; st.sitzung.stufe = "fertig";
      return { wiederherstellungscodes: Array.from({ length: 10 }, () => zufall(4) + "-" + zufall(4) + "-" + zufall(4)), rolle: u.rolle };
    }
    if (m === "POST" && p === "/api/login/2fa") {
      if (!st.sitzung || st.sitzung.stufe !== "2fa") throw new F(401, "Bitte melde dich erneut an.");
      const c = String(d.code || "").trim();
      if (!/^\d{6}$/.test(c) && !/^\w{4}-\w{4}-\w{4}$/.test(c)) throw new F(401, "Der Code stimmt nicht. In der Demo reicht jede 6-stellige Zahl.");
      st.sitzung.stufe = "fertig"; return { rolle: user(st.sitzung.uid).rolle };
    }
    if (m === "POST" && p === "/api/logout") { st.sitzung = null; return { ok: true }; }
    if (m === "GET" && p === "/api/ich") { const u = ich(); return { id: u.id, email: u.email, name: u.name, rolle: u.rolle, bereich: u.bereich }; }
    if (m === "GET" && p === "/api/kurse") { nur("admin", "berater");
      return { stand: "2026-10-09", quelle: "EZB-Referenzkurse", hinweis: "Demo: fest hinterlegter Stand",
        kurse: { USD: 1.1206, JPY: 177.34, CZK: 24.369, DKK: 7.4751, GBP: 0.84763, HUF: 365.08, PLN: 4.3835, SEK: 11.1675, CHF: 0.9313, NOK: 10.7155, TRY: 55.1033, AUD: 1.6052 } }; }
    if (m === "GET" && p === "/api/berater") { nur("admin", "berater");
      return st.users.filter((u) => u.aktiv && (u.rolle === "berater" || u.rolle === "admin")).map((u) => ({ id: u.id, name: u.name, email: u.email, bereich: u.bereich })); }
    if (p === "/api/akten") {
      const u = nur("admin", "berater");
      if (m === "GET") return st.akten.filter((a) => u.rolle === "admin" || st.akte_berater.some((b) => b.akte_id === a.id && b.user_id === u.id))
        .sort((a, b) => b.geaendert - a.geaendert)
        .map((a) => Object.assign({}, a, { kunde_email: a.kunde_id && user(a.kunde_id) ? user(a.kunde_id).email : null,
          vorab_da: !!abschnitt(a.id, "vorab"), loeschung_am: a.geaendert + 365 * TAG }));
      if (m === "POST") {
        const titel = String(d.titel || "").trim(); if (!titel) throw new F(422, "Bitte prüf deine Eingaben.");
        const id = st.naechste.akte++; st.akten.push({ id, titel, kunde_id: null, erstellt_von: u.id, erstellt: jetzt(), geaendert: jetzt() });
        st.akte_berater.push({ akte_id: id, user_id: u.id }); return { id };
      }
    }
    if ((t = p.match(/^\/api\/akten\/(\d+)(\/.*)?$/))) {
      const u = nur("admin", "berater"), id = Number(t[1]), rest = t[2] || "";
      if (rest === "" && m === "GET") return akteLesen(u, id);
      if (rest === "" && m === "DELETE") {
        const a = akteFuer(u, id); if (!darfVerwalten(u, a)) throw new F(403, "Löschen darf, wer die Akte angelegt hat, oder der Admin");
        st.akten = st.akten.filter((x) => x.id !== id); st.abschnitte = st.abschnitte.filter((x) => x.akte_id !== id);
        st.akte_berater = st.akte_berater.filter((x) => x.akte_id !== id); st.einladungen = st.einladungen.filter((x) => x.akte_id !== id);
        if (a.kunde_id && user(a.kunde_id)) { const k = user(a.kunde_id); k.aktiv = false; k.email = "geloescht-" + k.id + "@invalid"; k.name = "gelöscht"; }
        return { ok: true };
      }
      if (rest === "/berater" && m === "POST") {
        const a = akteFuer(u, id); if (!darfVerwalten(u, a)) throw new F(403, "Berater zuordnen darf, wer die Akte angelegt hat, oder der Admin");
        const b = user(Number(d.user_id)); if (!b || b.rolle !== "berater") throw new F(404, "Berater nicht gefunden");
        if (!st.akte_berater.some((x) => x.akte_id === id && x.user_id === b.id)) st.akte_berater.push({ akte_id: id, user_id: b.id });
        return { ok: true };
      }
      if ((t = rest.match(/^\/berater\/(\d+)$/)) && m === "DELETE") {
        const a = akteFuer(u, id), uid = Number(t[1]); if (!darfVerwalten(u, a)) throw new F(403, "Entziehen darf, wer die Akte angelegt hat, oder der Admin");
        if (uid === a.erstellt_von) throw new F(409, "Wer die Akte angelegt hat, bleibt zugeordnet");
        st.akte_berater = st.akte_berater.filter((x) => !(x.akte_id === id && x.user_id === uid)); return { ok: true };
      }
      if (rest === "/einladung" && m === "POST") {
        const a = akteFuer(u, id); if (a.kunde_id) throw new F(409, "Die Akte hat schon einen Kundenzugang");
        const email = String(d.email || "").trim().toLowerCase();
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new F(422, "Ungültige E-Mail");
        if (st.users.some((x) => x.aktiv && x.email === email)) throw new F(409, "Für diese E-Mail gibt es schon einen Zugang.");
        const token = "demo-" + zufall(16);
        st.einladungen = st.einladungen.filter((x) => x.akte_id !== id);
        st.einladungen.push({ token, akte_id: id, email, name: String(d.name || "").trim(), ablauf: jetzt() + 14 * TAG });
        return { token, pfad: basis() + "kunde.html#einladung=" + token, gueltig_tage: 14 };
      }
      if ((t = rest.match(/^\/abschnitte\/(\w+)$/)) && m === "PUT") {
        akteFuer(u, id); const k = t[1];
        if (k === "vorab") throw new F(403, "Die Angaben des Kunden ändert nur der Kunde");
        if (k === "absicherung_bewertung" && u.bereich !== "versicherung") throw new F(403, "Die Bewertung der Absicherung schreibt nur der Versicherungsmakler");
        const e = einwilligung(id); if (e && e.widerrufen) throw new F(409, "Der Kunde hat seine Einwilligung widerrufen. Die Akte kann nicht mehr bearbeitet werden.");
        if (Object.keys(d.daten || {}).some((x) => /^q_p9_/.test(x))) throw new F(422, "Antworten zu Block 9 (Selbstbild) werden nicht gespeichert");
        return { version: speichernOder409(id, k, d.daten, u.id, d.version, "Inzwischen hat jemand anderes gespeichert. Bitte neu laden.") };
      }
      if (rest === "/export" && m === "GET") {
        const a = akteLesen(u, id); a.erstellt_am = jetzt(); a.erstellt_von_name = u.name;
        a.pruefwert = await sha256(kanonisch(a)); return a;
      }
    }
    if (m === "POST" && p === "/api/einladung/pruefen") {
      const e = st.einladungen.find((x) => x.token === d.token && x.ablauf > jetzt());
      if (!e) throw new F(404, "Die Einladung ist ungültig oder abgelaufen"); return { name: e.name, email: e.email };
    }
    if (m === "POST" && p === "/api/einladung/annehmen") {
      const e = st.einladungen.find((x) => x.token === d.token && x.ablauf > jetzt());
      if (!e) throw new F(404, "Die Einladung ist ungültig oder abgelaufen");
      if (String(d.passwort || "").length < 10) throw new F(422, "Bitte prüf deine Eingaben.");
      const a = akteById(e.akte_id); if (!a || a.kunde_id) throw new F(409, "Diese Einladung ist nicht mehr gültig. Bitte melde dich bei uns.");
      const uid = st.naechste.user++;
      st.users.push({ id: uid, email: e.email, name: e.name, rolle: "kunde", bereich: null, pw: d.passwort, totp: false, aktiv: true });
      a.kunde_id = uid; st.einladungen = st.einladungen.filter((x) => x.akte_id !== a.id);
      st.sitzung = { uid, stufe: "fertig" }; st.einladungOffen = null; return { ok: true };
    }
    if (p.indexOf("/api/kunde/") === 0) {
      const u = nur("kunde"), a = eigeneAkte(u);
      if (m === "GET" && p === "/api/kunde/akte") { const e = aktiveEinw(a.id, u.id);
        return { name: u.name, email: u.email, vorab: abschnitt(a.id, "vorab"), einwilligung: e ? { version: e.text_version, zeit: e.zeit } : null, einwilligung_aktuell: EINW_VERSION }; }
      if (m === "POST" && p === "/api/kunde/einwilligung") {
        if (d.text_version !== EINW_VERSION) throw new F(409, "Der Einwilligungstext hat sich geändert. Bitte lade die Seite neu.");
        st.einwilligungen.push({ akte_id: a.id, user_id: u.id, text_version: d.text_version, zeit: jetzt(), widerrufen: null }); return { ok: true };
      }
      if (m === "PUT" && p === "/api/kunde/vorab") {
        if (!aktiveEinw(a.id, u.id)) throw new F(403, "Ohne Einwilligung können wir nichts speichern");
        return { version: speichernOder409(a.id, "vorab", d.daten, u.id, d.version, "Deine Angaben wurden inzwischen in einem anderen Fenster geändert. Bitte lade die Seite neu.") };
      }
      if (m === "POST" && p === "/api/kunde/widerruf") {
        st.einwilligungen.forEach((e) => { if (e.akte_id === a.id && e.user_id === u.id && !e.widerrufen) e.widerrufen = jetzt(); });
        st.abschnitte = st.abschnitte.filter((x) => x.akte_id !== a.id); return { ok: true };
      }
      if (m === "GET" && p === "/api/kunde/bericht") {
        const b = abschnitt(a.id, "bericht");
        if (!b || !b.daten.freigegeben_am || !b.daten.schnappschuss) throw new F(404, "Noch kein Bericht freigegeben");
        return b.daten.schnappschuss;
      }
      if (m === "GET" && p === "/api/kunde/export") return { name: u.name, email: u.email, angaben: akteDaten(a.id),
        berater_mit_zugriff: st.akte_berater.filter((b) => b.akte_id === a.id).map((b) => ({ name: (user(b.user_id) || {}).name })),
        einwilligungen: st.einwilligungen.filter((e) => e.user_id === u.id).map((e) => ({ text_version: e.text_version, zeit: e.zeit, widerrufen: e.widerrufen || null })) };
    }
    void q;
    throw new F(404, "Nicht gefunden");
  }

  const echtFetch = window.fetch.bind(window);
  window.fetch = async function (eingabe, opt) {
    const url = typeof eingabe === "string" ? eingabe : eingabe.url;
    if (url.indexOf("/api/") !== 0) return echtFetch(eingabe, opt);
    await new Promise((r) => setTimeout(r, 120));
    const methode = (opt && opt.method) || "GET";
    let daten = {};
    try { daten = opt && opt.body ? JSON.parse(opt.body) : {}; } catch (e) { daten = {}; }
    st = laden();
    try {
      const r = await route(methode, url, daten); sichern();
      return new Response(JSON.stringify(r), { status: 200, headers: { "Content-Type": "application/json" } });
    } catch (e) {
      sichern();
      if (e instanceof F) return new Response(JSON.stringify({ detail: e.message }), { status: e.status, headers: { "Content-Type": "application/json" } });
      throw e;
    }
  };

  /* ---------- Was im Vorschaufenster nicht geht: Dialoge, Drucken, Herunterladen ---------- */
  function hinweis(text) {
    let t = document.getElementById("demo-hinweis");
    if (!t) { t = document.createElement("div"); t.id = "demo-hinweis"; t.setAttribute("role", "status"); document.body.appendChild(t); }
    t.textContent = text; t.hidden = false; clearTimeout(t._z); t._z = setTimeout(() => { t.hidden = true; }, 6000);
  }
  function fenster(titel, html, notiz) {
    let o = document.getElementById("demo-fenster");
    if (!o) { o = document.createElement("div"); o.id = "demo-fenster"; document.body.appendChild(o); }
    o.innerHTML = `<div class="demo-fenster-kopf"><div><b></b><small></small></div><button type="button" id="demo-schliessen">Schließen</button></div><div class="demo-papier"></div>`;
    o.querySelector("b").textContent = titel; o.querySelector("small").textContent = notiz || "";
    o.querySelector(".demo-papier").innerHTML = html;
    o.hidden = false; document.body.classList.add("demo-gesperrt");
    o.querySelector("#demo-schliessen").addEventListener("click", () => { o.hidden = true; document.body.classList.remove("demo-gesperrt"); });
    o.querySelector("#demo-schliessen").focus();
  }
  window.confirm = (frage) => { hinweis("Sicherheitsabfrage der App: „" + frage + "“ In der Demo automatisch bestätigt."); return true; };
  window.alert = (text) => { hinweis(text); };
  window.prompt = (frage) => { const m = String(frage).match(/eintippen: (.*)$/); hinweis("Sicherheitsabfrage der App: „" + frage + "“ In der Demo automatisch ausgefüllt."); return m ? m[1] : ""; };
  window.print = () => {
    const box = document.getElementById("druck");
    if (box && box.innerHTML.trim() && document.body.classList.contains("druckmodus")) {
      const istBericht = !!box.querySelector(".bericht");
      fenster(istBericht ? "Druckansicht: Dein Finanzbericht" : "Druckansicht: Aktenauszug fürs Archiv", box.innerHTML,
        "In der echten App öffnet sich hier der Druckdialog. Dort wählst du „Als PDF speichern“.");
    } else hinweis("In der echten App öffnet sich hier der Druckdialog des Browsers.");
  };
  const klick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.download && this.href.indexOf("blob:") === 0) {
      const name = this.download;
      fetch(this.href).then((r) => r.text()).then((t) => {
        const pre = document.createElement("pre"); pre.textContent = t;
        fenster("Download: " + name, pre.outerHTML, "In der echten App wird diese Datei heruntergeladen. Hier siehst du ihren Inhalt.");
      });
      return;
    }
    return klick.call(this);
  };

  /* ---------- Demo-Leiste und Einstiege ---------- */
  const ZIELE = {
    oliver: { uid: 1, ziel: "berater.html", name: "Oliver (Finanzanlagen)" },
    jan: { uid: 2, ziel: "berater.html", name: "Jan (Versicherungen)" },
    lena: { uid: 3, ziel: "kunde.html", name: "Lena Muster (Kundin)" }
  };
  function als(wer) {
    st = laden(); const z = ZIELE[wer]; const u = user(z.uid);
    if (!u) { hinweis("Diesen Zugang gibt es in der Demo nicht mehr. Setz die Demo zurück."); return; }
    st.sitzung = { uid: u.id, stufe: "fertig" }; st.einladungOffen = null; sichern();
    location.href = z.ziel;
  }
  function einladungOeffnen() {
    st = laden();
    let e = st.einladungen[st.einladungen.length - 1];
    if (!e) {
      const a = st.akten.find((x) => !x.kunde_id);
      if (!a) { hinweis("Keine offene Akte für eine Einladung. Leg als Oliver eine neue Akte an oder setz die Demo zurück."); return; }
      e = { token: "demo-" + zufall(16), akte_id: a.id, email: "tom@beispiel.de", name: a.titel, ablauf: jetzt() + 14 * TAG };
      st.einladungen.push(e);
    }
    st.sitzung = null; st.einladungOffen = e.token; sichern();
    location.href = "kunde.html#einladung=" + e.token;
  }
  function zuruecksetzen() {
    try { localStorage.removeItem(KEY); } catch (e) { /* ignorieren */ }
    window.name = ""; st = frisch(); sichern();
    location.href = "anmeldung.html";
  }
  window.DEMO = {
    als, einladungOeffnen, zuruecksetzen,
    // Fallback, falls das Vorschaufenster den Teil hinter # nicht weitergibt
    offeneEinladung: () => { st = laden(); return st.einladungOffen && !st.sitzung ? [null, st.einladungOffen] : null; }
  };

  function leiste() {
    if (document.getElementById("demo-leiste") || document.getElementById("demo-start")) return;
    const l = document.createElement("div"); l.id = "demo-leiste";
    l.innerHTML = `<span><b>Demo</b> mit erfundenen Daten. Gespeichert wird nur in diesem Browser.</span>
      <label for="demo-wechsel" class="demo-unsichtbar">Ansicht wechseln</label>
      <select id="demo-wechsel"><option value="">Ansicht wechseln …</option><option value="anmeldung">Anmeldeseite</option>
        <option value="oliver">Oliver (Finanzanlagen)</option><option value="jan">Jan (Versicherungen)</option>
        <option value="lena">Lena Muster (Kundin)</option><option value="einladung">Neuer Kunde mit Einladungslink</option></select>
      <button type="button" id="demo-reset">Demo zurücksetzen</button>`;
    document.body.insertBefore(l, document.body.firstChild);
    l.querySelector("#demo-wechsel").addEventListener("change", (ev) => {
      const v = ev.target.value; ev.target.value = "";
      if (v === "anmeldung") { st = laden(); st.sitzung = null; st.einladungOffen = null; sichern(); location.href = "anmeldung.html"; }
      else if (v === "einladung") einladungOeffnen(); else if (v) als(v);
    });
    l.querySelector("#demo-reset").addEventListener("click", zuruecksetzen);
  }
  const css = document.createElement("style");
  css.textContent = `
  #demo-leiste{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;
    padding:8px 16px;background:var(--amber-l);color:var(--ink);border-bottom:1px solid var(--line);font-size:14px}
  #demo-leiste span{flex:1 1 260px} #demo-leiste b{color:var(--amber)}
  #demo-leiste select,#demo-leiste button{font:inherit;font-size:14px;padding:6px 10px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);width:auto;margin:0;min-height:0}
  #demo-leiste button{cursor:pointer}
  .demo-unsichtbar{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
  #demo-hinweis{position:fixed;left:16px;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:70;max-width:560px;margin:0 auto;
    background:var(--ink);color:var(--bg);padding:12px 16px;border-radius:12px;font-size:14px;box-shadow:0 6px 24px rgba(0,0,0,.25)}
  #demo-fenster{position:fixed;inset:0;z-index:60;background:var(--bg);overflow:auto;padding:0 16px 40px}
  .demo-fenster-kopf{position:sticky;top:0;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 0;background:var(--bg);border-bottom:1px solid var(--line);margin-bottom:16px}
  .demo-fenster-kopf small{display:block;color:var(--mute);font-size:13px}
  .demo-fenster-kopf button{font:inherit;padding:8px 14px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer;width:auto}
  .demo-papier{background:#fff;color:#1D1D1F;max-width:820px;margin:0 auto;padding:28px;border-radius:6px;box-shadow:0 2px 12px rgba(0,0,0,.12);overflow-x:auto}
  .demo-papier table{border-collapse:collapse;width:100%;font-size:14px} .demo-papier td{padding:4px 6px;border-bottom:1px solid #ddd;vertical-align:top}
  .demo-papier td:first-child{width:45%;color:#444} .demo-papier pre{white-space:pre-wrap;word-break:break-word;font-size:12px;margin:0}
  .demo-papier .bericht{padding:0}
  body.demo-gesperrt{overflow:hidden}
  #demo-leiste select:focus-visible,#demo-leiste button:focus-visible,.demo-fenster-kopf button:focus-visible{outline:2px solid var(--blue);outline-offset:2px}`;
  document.head.appendChild(css);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", leiste); else leiste();
})();
