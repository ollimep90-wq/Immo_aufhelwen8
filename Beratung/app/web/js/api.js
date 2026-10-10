/* Zugriff auf die API. Alle schreibenden Anfragen tragen den Header gegen CSRF. */
(function (root) {
  "use strict";
  async function anfrage(methode, pfad, daten) {
    const opt = { method: methode, headers: { "X-Requested-With": "app" }, credentials: "same-origin" };
    if (daten !== undefined) { opt.headers["Content-Type"] = "application/json"; opt.body = JSON.stringify(daten); }
    let r;
    try { r = await fetch(pfad, opt); }
    catch (e) { const f = new Error("Keine Verbindung. Bitte prüf dein Internet und versuch es noch einmal."); f.status = 0; throw f; }
    let body = null;
    try { body = await r.json(); } catch (e) { body = null; }
    if (!r.ok) {
      let text = body && typeof body.detail === "string" ? body.detail : null;
      if (!text) text = r.status === 422 ? "Bitte prüf deine Eingaben." : "Da ist bei uns etwas schiefgelaufen. Bitte versuch es gleich noch einmal.";
      if (r.status === 401 && pfad !== "/api/login") text = "Du bist nicht mehr angemeldet. Bitte melde dich neu an. Was du in diesem Schritt eingegeben hast, ist noch nicht gespeichert.";
      const fehler = new Error(text);
      fehler.status = r.status; throw fehler;
    }
    return body;
  }
  const api = {
    get: (p) => anfrage("GET", p), post: (p, d) => anfrage("POST", p, d || {}),
    put: (p, d) => anfrage("PUT", p, d), del: (p) => anfrage("DELETE", p)
  };
  /* Kleine Helfer für alle Seiten */
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const eur = (x) => (x == null || !isFinite(x)) ? "–" : Math.round(x).toLocaleString("de-DE") + " €";
  const pct = (x) => (x == null || !isFinite(x)) ? "–" : Math.round(x * 100).toLocaleString("de-DE") + " %";
  const num = (v) => { const n = parseFloat(String(v == null ? "" : v).replace(",", ".")); return isFinite(n) ? n : 0; };
  /* Formular <-> Objekt: Felder mit data-f (Name), Radios/Checkboxen per name */
  function lies(wurzel) {
    const o = {};
    wurzel.querySelectorAll("[data-f]").forEach((e) => {
      const k = e.dataset.f;
      if (e.type === "radio") { if (e.checked) o[k] = e.value; else if (!(k in o)) o[k] = o[k] || ""; }
      else if (e.type === "checkbox") { o[k] = o[k] || []; if (e.checked) o[k].push(e.value); }
      else o[k] = e.value;
    });
    return o;
  }
  function fuelle(wurzel, o) {
    if (!o) return;
    wurzel.querySelectorAll("[data-f]").forEach((e) => {
      const v = o[e.dataset.f];
      if (v === undefined) return;
      if (e.type === "radio") e.checked = e.value === v;
      else if (e.type === "checkbox") e.checked = Array.isArray(v) && v.includes(e.value);
      else e.value = v;
    });
  }
  root.App = { api, $, esc, eur, pct, num, lies, fuelle };
})(this);
