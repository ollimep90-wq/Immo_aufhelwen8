(function () {
  "use strict";
  const { api, $ } = App;
  let rolle = null;
  function weiter(r) { location.href = r === "kunde" ? "/kunde.html" : "/berater.html"; }
  function zeige(id) {
    ["schritt-login", "schritt-code", "schritt-einrichten", "schritt-codes"].forEach((x) => { $(x).hidden = x !== id; });
    const f = $(id).querySelector("input"); if (f) f.focus();
  }
  api.get("/api/ich").then((u) => weiter(u.rolle)).catch(() => {});

  $("login").addEventListener("submit", async (ev) => {
    ev.preventDefault(); $("fehler").textContent = "";
    try {
      const r = await api.post("/api/login", { email: $("email").value.trim(), passwort: $("pw").value });
      $("pw").value = "";
      if (r.schritt === "fertig") return weiter(r.rolle);
      if (r.schritt === "2fa") return zeige("schritt-code");
      const e = await api.post("/api/2fa/einrichten");
      $("qr").src = e.qr; $("geheimnis").textContent = e.geheimnis.replace(/(.{4})/g, "$1 ").trim();
      zeige("schritt-einrichten");
    } catch (e) { $("fehler").textContent = e.message; }
  });

  $("code-form").addEventListener("submit", async (ev) => {
    ev.preventDefault(); $("code-fehler").textContent = "";
    try {
      const r = await api.post("/api/login/2fa", { code: $("code").value.trim() });
      if (r.wiederherstellungscodes_uebrig !== undefined && r.wiederherstellungscodes_uebrig < 3) {
        alert(`Du hast nur noch ${r.wiederherstellungscodes_uebrig} Wiederherstellungscodes. Bitte lass die Zwei-Faktor-Anmeldung vom Admin zurücksetzen und richte sie neu ein.`);
      }
      weiter(r.rolle);
    } catch (e) {
      $("code-fehler").textContent = e.message; $("code").value = "";
      if (e.status === 429 || e.status === 401 && /erneut an/.test(e.message)) setTimeout(() => zeige("schritt-login"), 1500);
    }
  });
  $("neu-anmelden").addEventListener("click", () => zeige("schritt-login"));

  $("einrichten-form").addEventListener("submit", async (ev) => {
    ev.preventDefault(); $("einrichten-fehler").textContent = "";
    try {
      const r = await api.post("/api/2fa/bestaetigen", { code: $("code2").value.trim() });
      rolle = r.rolle;
      $("codes").textContent = r.wiederherstellungscodes.join("\n");
      zeige("schritt-codes");
    } catch (e) { $("einrichten-fehler").textContent = e.message; $("code2").value = ""; }
  });
  $("codes-drucken").addEventListener("click", () => window.print());
  $("codes-weiter").addEventListener("click", () => weiter(rolle));
})();
