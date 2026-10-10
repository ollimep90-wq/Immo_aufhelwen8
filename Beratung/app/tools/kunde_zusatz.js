
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

async function weiterKlick() {
  if (akt === 0) {
    if (!eingewilligt) {
      if (!$("einwilligung").checked) { $("lade-fehler").textContent = "Bitte stimme zu, damit wir deine Angaben speichern können."; return; }
      await A.post("/api/kunde/einwilligung", { text_version: einwVersion, text: $("einwilligung-text").textContent });
      eingewilligt = true; $("lade-fehler").textContent = "";
    }
  } else {
    try { await speichere(); } catch (e) { return; }
  }
  zeige(akt + 1);
  if (akt === 6) risikoAntwortenSetzen();
  if (akt === LETZTER) { try { await speichere(); } catch (e) { /* Hinweis steht schon da */ } }
}

async function ladeAkte() {
  const k = await A.get("/api/kunde/akte");
  einwVersion = k.einwilligung_aktuell;
  eingewilligt = !!(k.einwilligung && k.einwilligung.version === einwVersion);
  $("einwilligung").checked = eingewilligt;
  $("einwilligung").disabled = eingewilligt;
  $("hallo").textContent = `Hallo ${k.name}, dein Finanz-Check`;
  if (k.vorab) { version = k.vorab.version; formularSetzen(k.vorab.daten.formular); }
  $("f").hidden = false; $("abmelden").hidden = false;
  zeige(0); aktualisiere();
}

async function start() {
  const m = location.hash.match(/einladung=([\w-]+)/);
  if (m) {
    try {
      const e = await A.get("/api/einladung/" + m[1]);
      $("einladung-titel").textContent = `Willkommen, ${e.name}`;
      $("einladung-email").value = e.email;
      $("einladung-box").hidden = false;
      $("einladung-form").addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const p1 = $("neu-pw").value, p2 = $("neu-pw2").value;
        if (p1.length < 10) { $("einladung-fehler").textContent = "Bitte mindestens 10 Zeichen."; return; }
        if (p1 !== p2) { $("einladung-fehler").textContent = "Die Passwörter sind nicht gleich."; return; }
        try {
          await A.post("/api/einladung/annehmen", { token: m[1], passwort: p1 });
          history.replaceState(null, "", "/kunde.html");
          $("einladung-box").hidden = true;
          await ladeAkte();
        } catch (err) { $("einladung-fehler").textContent = err.message; }
      });
      return;
    } catch (e) {
      $("lade-fehler").textContent = e.message; return;
    }
  }
  try { await ladeAkte(); }
  catch (e) { if (e.status === 401 || e.status === 403) location.href = "/"; else $("lade-fehler").textContent = e.message; }
}

$("abmelden").addEventListener("click", async () => { await A.post("/api/logout"); location.href = "/"; });
$("drucken").addEventListener("click", () => window.print());
$("export").addEventListener("click", async () => {
  const d = await A.get("/api/kunde/export");
  const url = URL.createObjectURL(new Blob([JSON.stringify(d, null, 2)], { type: "application/json" }));
  const a = document.createElement("a"); a.href = url; a.download = "meine-daten.json"; a.click(); URL.revokeObjectURL(url);
});
$("widerruf").addEventListener("click", async () => {
  if (!confirm("Einwilligung widerrufen? Deine Angaben im Finanz-Check werden dann gelöscht.")) return;
  await A.post("/api/kunde/widerruf");
  eingewilligt = false; version = null;
  $("konto-status").textContent = "Widerrufen. Deine Angaben sind gelöscht.";
  $("einwilligung").checked = false; $("einwilligung").disabled = false;
});

start();
