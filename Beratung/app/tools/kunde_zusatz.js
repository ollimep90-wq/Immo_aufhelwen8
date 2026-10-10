
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
  try { berichtDaten = await A.get("/api/kunde/bericht"); $("bericht-box").hidden = false; } catch (e) { berichtDaten = null; }
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

let berichtDaten = null;
function berichtRendern(ziel) {
  if (!document.getElementById("bericht-css")) { const st = document.createElement("style"); st.id = "bericht-css"; st.textContent = Bericht.CSS; document.head.appendChild(st); }
  const m = document.querySelector(".marke");
  ziel.innerHTML = Bericht.html(berichtDaten, { marke: m ? m.innerHTML : "" });
}
$("bericht-zeigen").addEventListener("click", () => {
  const v = $("bericht-ansicht"), offen = !v.hidden;
  v.hidden = offen; $("f").hidden = !offen;
  $("bericht-zeigen").textContent = offen ? "Ansehen" : "Zurück zum Finanz-Check";
  if (!offen) { berichtRendern(v); v.scrollIntoView({ behavior: "smooth" }); }
});
$("bericht-drucken").addEventListener("click", () => {
  let box = $("druck"); if (!box) { box = document.createElement("div"); box.id = "druck"; document.body.appendChild(box); }
  berichtRendern(box); document.body.classList.add("druckmodus"); window.print();
  setTimeout(() => document.body.classList.remove("druckmodus"), 500);
});

start();
