(function () {
  "use strict";
  const { api, $ } = App;
  function weiter(rolle) { location.href = rolle === "kunde" ? "/kunde.html" : "/berater.html"; }
  api.get("/api/ich").then((u) => weiter(u.rolle)).catch(() => {});
  $("login").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    $("fehler").textContent = "";
    try {
      const r = await api.post("/api/login", { email: $("email").value.trim(), passwort: $("pw").value });
      weiter(r.rolle);
    } catch (e) { $("fehler").textContent = e.message; }
  });
})();
