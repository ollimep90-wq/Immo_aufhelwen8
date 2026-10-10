(function () {
"use strict";
/* erzeugt aus Privat/vorab-check/vorab.html durch tools/baue_kunde.py, nicht von Hand ändern */
/* Versand: Hier die Adresse des Empfangsdienstes eintragen (offen, siehe STATUS.md).
 * Leer = kein Versand, nur PDF. Erwartet POST mit JSON, Antwort 2xx. */

const R = Rechenkern, F = Fragen;
const $ = (id) => document.getElementById(id);
const num = (id) => { const v = parseFloat(($(id).value || "").replace(",", ".")); return isFinite(v) && v > 0 ? v : 0; };
const radio = (n) => { const e = document.querySelector(`input[name="${n}"]:checked`); return e ? e.value : ""; };
const eur = (x) => (Math.round(x)).toLocaleString("de-DE") + " €";
const pct = (x) => (Math.round(x * 100)).toLocaleString("de-DE") + " %";
const steps = [...document.querySelectorAll(".step")];
const LETZTER = steps.length - 1;
let akt = 0;

function hatPartner() { const f = radio("familie"); return f === "partner" || f === "verheiratet"; }
function filterAktiv(f) {
  if (!f) return true;
  if (f === "kinder") return num("kinder") > 0;
  if (f === "tier") return num("tiere") > 0;
  if (f === "eigentum") return radio("wohnen") === "eigentum";
  if (f === "familie") return hatPartner() || num("kinder") > 0;
  return true;
}

function baueRisikofragen() {
  const box = $("risikofragen"); box.innerHTML = "";
  F.FRAGEN.filter((q) => filterAktiv(q.filter)).forEach((q) => {
    const skala = q.skala === "zustimmung" ? F.SKALA_ZUSTIMMUNG : F.SKALA;
    const d = document.createElement("div");
    d.innerHTML = `<p class="q" id="lbl-${q.id}">${q.text}</p><div class="seg" role="radiogroup" aria-labelledby="lbl-${q.id}">` +
      skala.map((s, i) => `<label><input type="radio" name="r_${q.id}" value="${s.wert === null ? "na" : s.wert}"><span>${s.text}</span></label>`).join("") + "</div>";
    box.appendChild(d);
  });
  const v = $("vorhanden");
  if (!v.childElementCount) {
    Object.entries(F.THEMEN).forEach(([k, t]) => {
      v.insertAdjacentHTML("beforeend", `<label><input type="checkbox" name="hat" value="${k}"><span>${t}</span></label>`);
    });
  }
}

function personenEingabe() {
  const kinder = num("kinder");
  const land = $("land").value;
  const pers = [];
  [1, 2].forEach((i) => {
    if (i === 2 && !hatPartner()) return;
    const art = radio("eart" + i), betrag = num("betrag" + i);
    pers.push({ art, betrag, kv: radio("kv" + i) || "gkv", pkv: num("pkv" + i),
                alter: num(i === 1 ? "alter" : "alter2") || 40, kinder_u25: kinder, sachsen: land === "SN",
                eltern: kinder > 0 || radio("eltern") === "ja" });
  });
  return pers;
}

function nettoMonat() {
  const pers = personenEingabe();
  const brutto = pers.filter((p) => p.art === "brutto" && p.betrag > 0);
  const nettoDirekt = pers.filter((p) => p.art === "netto").reduce((a, p) => a + p.betrag, 0);
  let geschaetzt = 0, info = null;
  if (brutto.length) {
    const verh = radio("familie") === "verheiratet";
    // Splitting braucht beide Einkommen brutto; bei gemischter Angabe Einzelrechnung (Näherung)
    const mitEinkommen = pers.filter((p) => p.betrag > 0);
    const splitting = verh && mitEinkommen.every((p) => p.art === "brutto");
    const r = R.nettoHaushalt({
      personen: brutto.map((p) => ({ brutto: p.betrag, kv: p.kv, pkv_eigenanteil_monat: p.pkv, alter: p.alter, kinder_u25: p.kinder_u25, sachsen: p.sachsen, eltern: p.eltern })),
      alleinerziehend: radio("familie") === "single" && num("kinder") > 0,
      verheiratet: splitting, kinder: num("kinder"), kirche: radio("kirche") === "ja", bundesland: $("land").value
    });
    geschaetzt = r.netto_monat; info = r;
    const hinweise = [];
    if (verh && !splitting) hinweise.push("Ihr seid verheiratet, aber nur eine Angabe ist brutto. Dann rechnen wir ohne Ehegattensplitting, das Netto kann deutlich zu niedrig sein. Tragt am besten beide brutto ein.");
    if (brutto.some((p) => p.betrag < 24000)) hinweise.push("Bei niedrigem Brutto (Minijob, Übergangsbereich) sind die Abzüge in der Schätzung zu hoch. Trag dein Netto besser direkt ein.");
    if (num("kinder") > 0) hinweise.push("Mit Kindern kann das Netto nach der Steuererklärung höher sein (Kinderfreibetrag statt Kindergeld).");
    info.hinweise = hinweise;
  }
  return { netto: nettoDirekt + geschaetzt, geschaetzt, info };
}

function fixkosten() {
  return [...document.querySelectorAll("#fixkosten input")].reduce((a, e) => a + num(e.id), 0);
}

function risiko() {
  const antworten = {};
  F.FRAGEN.filter((q) => filterAktiv(q.filter)).forEach((q) => {
    const v = radio("r_" + q.id);
    if (v === "") return;
    antworten[q.id] = v === "na" ? null : Number(v);
  });
  const fr = F.FRAGEN.map((q) => ({ id: q.id, block: q.block, gewichte: q.gewichte }));
  return { antworten, ergebnis: R.risikoAuswertung(fr, antworten) };
}

function sammle() {
  const n = nettoMonat(), fk = fixkosten();
  const b = R.budget({ netto_monat: n.netto, kindergeld_monat: num("kinder") * R.P2026.kindergeld_monat,
                       sonstige_einnahmen: num("sonstein"), fixkosten: fk, sparen: num("sparen"), liquide: num("liquide") });
  const rk = risiko();
  const hat = [...document.querySelectorAll('input[name="hat"]:checked')].map((e) => e.value);
  const wuensche = [1, 2, 3].map((i) => ({ text: $("w" + i).value.trim(), jahr: num("w" + i + "j") || null })).filter((w) => w.text);
  return {
    version: "vorab-check 2026-10", erstellt: new Date().toISOString(),
    person: { vorname: $("vorname").value.trim(), alter: num("alter"), familie: radio("familie"), kinder: num("kinder"),
              tiere: num("tiere"), wohnen: radio("wohnen"), beruf: radio("beruf"), bundesland: $("land").value },
    einkommen: { eingaben: personenEingabe(), netto_monat: n.netto, davon_geschaetzt: n.geschaetzt, sonstige: num("sonstein") },
    fixkosten: Object.fromEntries([...document.querySelectorAll("#fixkosten input")].map((e) => [e.id, num(e.id)])),
    fixkosten_summe: fk, sparen: num("sparen"),
    vermoegen: { liquide: num("liquide"), depot: num("depot"), sonstiges: num("sonstverm"), schulden: num("schulden"), rente_erwartet: num("rente") },
    budget: b, wuensche, ruhestand_alter: num("ruhestand") || null, sorge: $("sorge").value.trim(), schlaf: num("schlaf") || null,
    risiko: { antworten: rk.antworten, ergebnis: rk.ergebnis, vorhanden: hat }
  };
}

function zeigeErgebnis() {
  const d = sammle(), b = d.budget;
  $("erg-titel").textContent = d.person.vorname ? `${d.person.vorname}, dein Finanz-Check` : "Dein Finanz-Check";
  $("kpi").innerHTML = [
    ["Einnahmen", eur(b.einnahmen), d.einkommen.davon_geschaetzt ? "Netto teils geschätzt" : "inkl. Kindergeld"],
    ["Feste Ausgaben", eur(d.fixkosten_summe), b.einnahmen ? pct(d.fixkosten_summe / b.einnahmen) + " der Einnahmen" : ""],
    ["Bleibt nach festen Ausgaben", eur(b.ueberschuss1), pct(b.quote1) + " deiner Einnahmen"],
    ["Sparen", eur(d.sparen), pct(b.sparquote) + " deiner Einnahmen"],
    ["Bleibt nach dem Sparen", eur(b.ueberschuss2), pct(b.quote2) + " deiner Einnahmen"]
  ].map(([t, v, s]) => `<div><small>${t}</small><b>${v}</b><small>${s}</small></div>`).join("");
  $("erg-netto-hinweis").textContent = d.einkommen.davon_geschaetzt
    ? `Davon ${eur(d.einkommen.davon_geschaetzt)} netto aus deinem Brutto geschätzt (Rechengrößen 2026). Deine Gehaltsabrechnung kann abweichen.` : "";
  const m = b.reserve_monate;
  $("erg-reserve").innerHTML = m === null ? '<span class="amp keine"></span>Ohne feste Ausgaben können wir die Reserve nicht einschätzen.'
    : `<span class="amp ${b.reserve_ampel}"></span>Dein Konto und Tagesgeld reichen für rund <b>${m.toLocaleString("de-DE", { maximumFractionDigits: 1 })} Monate</b> feste Ausgaben. Als Faustregel gelten drei bis sechs Monate, wenn du selbstständig bist, eher mehr.`;
  const T = F.THEMEN, e = d.risiko.ergebnis;
  const zeilen = Object.keys(T).filter((k) => e[k]).sort((a, z) => e[z].quote - e[a].quote).map((k) => {
    const hat = d.risiko.vorhanden.includes(k);
    const txt = { rot: "laut deinen Antworten: stark", gelb: "laut deinen Antworten: spürbar", gruen: "laut deinen Antworten: wenig", keine: "nicht bewertet" }[e[k].ampel];
    const hinweis = hat ? "vorhanden, schaut sich Jan mit dir an" : e[k].ampel === "rot" ? "zuerst besprechen" : "";
    return `<tr><td><span class="amp ${e[k].ampel}"></span><b>${T[k]}</b><br><span class="hint" style="margin-left:20px">${txt}${hinweis ? " · " + hinweis : ""}</span></td></tr>`;
  });
  $("erg-risiko").innerHTML = zeilen.join("") || '<tr><td class="hint">Keine Antworten zu den Situationen.</td></tr>';
  $("erg-wuensche").innerHTML = d.wuensche.map((w) => `<li>${esc(w.text)}${w.jahr ? " · bis " + w.jahr : ""}</li>`).join("");
  $("erg-wuensche-box").hidden = !d.wuensche.length;
}
function esc(s) { return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

function zeige(i) {
  akt = Math.max(0, Math.min(LETZTER, i));
  steps.forEach((s, k) => s.classList.toggle("on", k === akt));
  $("bar").style.width = (akt / LETZTER * 100) + "%";
  $("schritt-text").textContent = akt === 0 ? "" : akt === LETZTER ? "Ergebnis" : `Schritt ${akt} von ${LETZTER - 1}`;
  $("zurueck").style.visibility = akt === 0 ? "hidden" : "visible";
  $("weiter").style.display = akt === LETZTER ? "none" : "";
  $("weiter").textContent = akt === 0 ? "Los geht's" : akt === LETZTER - 1 ? "Ergebnis zeigen" : "Weiter";
  if (akt === 6) baueRisikofragen();
  if (akt === LETZTER) zeigeErgebnis();
  window.scrollTo({ top: 0, behavior: "smooth" });
  const h = steps[akt].querySelector("h1"); if (h && akt > 0) { h.tabIndex = -1; h.focus({ preventScroll: true }); }
}

function aktualisiere() {
  $("einkommen-partner").hidden = !hatPartner();
  [1, 2].forEach((i) => {
    const brutto = radio("eart" + i) === "brutto";
    $("betrag" + i + "-label").textContent = brutto ? "Brutto im Jahr in € (inkl. Sonderzahlungen)" : "Netto im Monat in €";
    document.querySelector(`.brutto-only[data-p="${i}"]`).hidden = !brutto;
    document.querySelector(`.pkv-only[data-p="${i}"]`).hidden = !(brutto && radio("kv" + i) === "pkv");
  });
  $("kirche-box").hidden = ![1, 2].some((i) => radio("eart" + i) === "brutto");
  const n = nettoMonat();
  $("netto-schaetzung").textContent = n.geschaetzt ? `Geschätztes Netto aus Brutto: ${eur(n.geschaetzt)} im Monat. ` + (n.info.hinweise || []).join(" ") : "";
  $("eltern-box").hidden = num("kinder") > 0;
  const fk = fixkosten();
  $("fk-summe").textContent = fk ? `Zusammen ${eur(fk)} im Monat.` : "";
}

$("f").addEventListener("input", aktualisiere);
$("f").addEventListener("change", aktualisiere);
$("weiter").addEventListener("click", weiterKlick);
$("zurueck").addEventListener("click", () => zeige(akt - 1));
$("drucken").addEventListener("click", () => window.print());

// Barrierefreiheit: Auswahlgruppen und Ausgabenfelder beschriften
document.querySelectorAll(".seg").forEach((g) => {
  if (g.hasAttribute("role")) return;
  let l = g.previousElementSibling;
  while (l && l.tagName !== "LABEL" && l.tagName !== "H2") l = l.previousElementSibling;
  g.setAttribute("role", "radiogroup");
  if (l) g.setAttribute("aria-label", l.textContent.trim());
});
document.querySelectorAll("#fixkosten input").forEach((e) => e.setAttribute("aria-describedby", "fk-intro"));


/* ---- Ergänzung für die App: Einladung, Einwilligung, Speichern über die API ---- */
const A = App.api;
let version = null, eingewilligt = false, einwVersion = null;

function formularLesen() {
  const o = { felder: {}, radios: {}, hat: [] };
  document.querySelectorAll("#f input, #f select, #f textarea").forEach((e) => {
    if (e.id === "einwilligung") return;
    if (e.type === "radio") { if (e.checked) o.radios[e.name] = e.value; }
    else if (e.type === "checkbox") { if (e.name === "hat" && e.checked) o.hat.push(e.value); }
    else if (e.id) o.felder[e.id] = e.value;
  });
  return o;
}
function formularSetzen(o) {
  if (!o) return;
  Object.entries(o.felder || {}).forEach(([id, v]) => { const e = $(id); if (e) e.value = v; });
  Object.entries(o.radios || {}).forEach(([n, v]) => {
    if (n.startsWith("r_")) return;   // Risikofragen werden beim Aufbau gesetzt
    const e = document.querySelector(`input[name="${n}"][value="${v}"]`); if (e) e.checked = true;
  });
  window.__gespeicherteRadios = o.radios || {};
  window.__gespeichertesHat = o.hat || [];
}
function risikoAntwortenSetzen() {
  Object.entries(window.__gespeicherteRadios || {}).forEach(([n, v]) => {
    if (!n.startsWith("r_")) return;
    const e = document.querySelector(`input[name="${n}"][value="${v}"]`); if (e) e.checked = true;
  });
  (window.__gespeichertesHat || []).forEach((v) => { const e = document.querySelector(`input[name="hat"][value="${v}"]`); if (e) e.checked = true; });
}

async function speichere() {
  if (!eingewilligt) return;
  const daten = { formular: formularLesen(), auswertung: sammle() };
  try {
    const r = await A.put("/api/kunde/vorab", { daten, version });
    version = r.version;
    $("lade-fehler").textContent = "";
  } catch (e) {
    $("lade-fehler").textContent = "Speichern hat nicht geklappt: " + e.message;
    throw e;
  }
}

function endStatus(ok, text) {
  $("gespeichert-titel").textContent = ok === true ? "Gespeichert" : ok === "geloescht" ? "Gelöscht" : "Noch nicht gespeichert";
  $("gespeichert-text").textContent = text;
  $("nochmal").hidden = ok !== false;
  $("export").hidden = ok === "geloescht";
}
async function speichereEnde() {
  endStatus(null, "");
  $("gespeichert-titel").textContent = "Wird gespeichert …";
  try { await speichere(); endStatus(true, "Deine Angaben sind bei uns. Wir melden uns bei dir für das Gespräch."); }
  catch (e) { endStatus(false, e.message); }
}
async function weiterKlick() {
  if (akt === 0) {
    if (!eingewilligt) {
      if (!$("einwilligung").checked) { $("einw-fehler").textContent = "Bitte stimme zu, damit wir deine Angaben speichern können."; $("einwilligung").focus(); return; }
      try { await A.post("/api/kunde/einwilligung", { text_version: einwVersion, text: $("einwilligung-text").textContent }); }
      catch (e) { $("einw-fehler").textContent = e.message; return; }
      eingewilligt = true; $("einw-fehler").textContent = ""; meineDatenZeigen();
    }
  } else {
    try { await speichere(); } catch (e) { return; }
  }
  zeige(akt + 1);
  if (akt === 6) risikoAntwortenSetzen();
  if (akt === LETZTER) await speichereEnde();
}
function meineDatenZeigen() {
  $("meine-daten").hidden = !eingewilligt;
  $("einwilligung").checked = eingewilligt; $("einwilligung").disabled = eingewilligt;
}

async function ladeAkte() {
  const k = await A.get("/api/kunde/akte");
  einwVersion = k.einwilligung_aktuell;
  eingewilligt = !!(k.einwilligung && k.einwilligung.version === einwVersion);
  meineDatenZeigen();
  $("hallo").textContent = `Hallo ${k.name}, schön, dass du da bist`;
  if (k.vorab) { version = k.vorab.version; formularSetzen(k.vorab.daten.formular); }
  $("f").hidden = false; $("abmelden").hidden = false;
  zeige(0); aktualisiere();
}

async function start() {
  const m = location.hash.match(/einladung=([\w-]+)/);
  if (m) {
    try {
      const e = await A.post("/api/einladung/pruefen", { token: m[1] });
      $("einladung-titel").textContent = `Willkommen, ${e.name}`;
      $("einladung-email").value = e.email; $("einladung-email-text").textContent = e.email;
      $("einladung-box").hidden = false;
      $("einladung-form").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const p1 = $("neu-pw").value, p2 = $("neu-pw2").value;
        if (p1.length < 10) { $("einladung-fehler").textContent = "Dein Passwort braucht mindestens 10 Zeichen."; return; }
        if (p1 !== p2) { $("einladung-fehler").textContent = "Die beiden Passwörter stimmen nicht überein."; return; }
        try {
          await A.post("/api/einladung/annehmen", { token: m[1], passwort: p1 });
          history.replaceState(null, "", "/kunde.html");
          $("einladung-box").hidden = true;
          await ladeAkte();
        } catch (err) { $("einladung-fehler").textContent = err.message; }
      });
      return;
    } catch (e) {
      $("lade-fehler").innerHTML = e.status === 404
        ? 'Dieser Einladungslink ist ungültig oder abgelaufen. Hast du schon ein Passwort festgelegt? Dann <a href="/">melde dich hier an</a>. Sonst schicken wir dir gern einen neuen Link.'
        : App.esc(e.message);
      return;
    }
  }
  try { await ladeAkte(); }
  catch (e) { if (e.status === 401 || e.status === 403) location.href = "/"; else $("lade-fehler").textContent = e.message; }
}

$("abmelden").addEventListener("click", async () => { await A.post("/api/logout"); location.href = "/"; });
$("drucken").addEventListener("click", () => window.print());
async function exportieren(status) {
  try {
    const d = await A.get("/api/kunde/export");
    const url = URL.createObjectURL(new Blob([JSON.stringify(d, null, 2)], { type: "application/json" }));
    const a = document.createElement("a"); a.href = url; a.download = "meine-daten.json"; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  } catch (e) { $(status).textContent = e.message; }
}
async function widerrufen(status) {
  if (!confirm("Einwilligung widerrufen? Alle deine Angaben in der App werden dann gelöscht. Wenn du sie behalten willst, lade sie vorher herunter.")) return;
  try { await A.post("/api/kunde/widerruf"); }
  catch (e) { $(status).textContent = "Das Widerrufen hat nicht geklappt. Deine Angaben sind noch gespeichert. Bitte versuch es noch einmal oder schreib uns. (" + e.message + ")"; return; }
  eingewilligt = false; version = null; meineDatenZeigen();
  endStatus("geloescht", "Du hast deine Einwilligung widerrufen. Deine Angaben sind gelöscht. Was du jetzt noch siehst, steht nur in diesem Browserfenster.");
  $(status).textContent = "Widerrufen. Deine Angaben sind gelöscht.";
}
$("export").addEventListener("click", () => exportieren("konto-status"));
$("export0").addEventListener("click", () => exportieren("konto-status0"));
$("widerruf").addEventListener("click", () => widerrufen("konto-status"));
$("widerruf0").addEventListener("click", () => widerrufen("konto-status0"));
$("nochmal").addEventListener("click", speichereEnde);

start();

})();
