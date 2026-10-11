/* Oberfläche zum Einlesen von Kontoauszügen. Alles bleibt im Browser: Dateien werden nicht hochgeladen,
 * Buchungen nicht gespeichert. Erst wenn der Kunde auf „Übernehmen“ tippt, gehen Monatssummen in die Felder.
 * PDF-Auszüge liest pdf.js (lokal unter /vendor/pdfjs, Apache-2.0), nachgeladen nur bei Bedarf. */
(function (root) {
  "use strict";
  const K = root.Kontoauszug;
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const eur = (x) => Math.round(Number(x) || 0).toLocaleString("de-DE") + " €";
  const tag = (iso) => iso ? iso.split("-").reverse().join(".") : "";
  const PDFJS = "/vendor/pdfjs/";

  async function pdfZeilen(buffer) {
    // relativ zur Seite auflösen (import() in klassischen Skripten löst sonst relativ zur Skriptdatei auf)
    const basis = new URL(PDFJS, document.baseURI).href;
    const pdfjs = await import(basis + "pdf.min.mjs");
    pdfjs.GlobalWorkerOptions.workerSrc = basis + "pdf.worker.min.mjs";
    const doc = await pdfjs.getDocument({ data: new Uint8Array(buffer), isEvalSupported: false }).promise;
    const zeilen = [];
    for (let s = 1; s <= doc.numPages; s++) {
      const inhalt = await (await doc.getPage(s)).getTextContent();
      const reihen = [];
      inhalt.items.forEach((it) => {
        if (!it.str || !it.str.trim()) return;
        const y = it.transform[5], x = it.transform[4];
        let r = reihen.find((q) => Math.abs(q.y - y) < 2.5);
        if (!r) { r = { y, teile: [] }; reihen.push(r); }
        r.teile.push({ x, t: it.str });
      });
      reihen.sort((a, b) => b.y - a.y).forEach((r) => zeilen.push(r.teile.sort((a, b) => a.x - b.x).map((q) => q.t).join(" ")));
    }
    return zeilen;
  }

  async function leseDatei(datei) {
    const buf = await datei.arrayBuffer();
    const name = datei.name.toLowerCase();
    if (name.endsWith(".pdf")) return { art: "PDF", buchungen: K.lesePDFZeilen(await pdfZeilen(buf)) };
    const text = K.dekodiere(buf);
    if (name.endsWith(".xml") || /^\s*<\?xml|<Document/.test(text.slice(0, 500))) return { art: "CAMT", buchungen: K.leseCAMT(text) };
    return { art: "CSV", buchungen: K.leseCSV(text) };
  }

  /* opt: { anwenden(monat, auswertung) } */
  function einbauen(ziel, opt) {
    let buchungen = [], zuordnung = {}, auswertung = null, meldungen = [];
    ziel.innerHTML = `<div class="card ka">
      <h2 style="margin-top:0">Schneller: Kontoauszüge einlesen</h2>
      <p class="hint" style="margin-top:0">Lade die Umsätze der letzten drei Monate hoch: als CSV-Datei aus dem Online-Banking, als CAMT-Datei (XML) oder als PDF-Kontoauszug. Mehrere Dateien gehen auch.</p>
      <p class="hint"><b>Deine Kontoauszüge bleiben auf deinem Gerät.</b> Die Auswertung passiert nur hier im Browser. Zu uns gehen nur die Monatssummen, die du unten übernimmst, keine einzelnen Buchungen.</p>
      <label class="btn quiet ka-datei">Dateien auswählen<input type="file" id="ka-dateien" multiple accept=".csv,.txt,.xml,.pdf,text/csv,application/pdf,application/xml" hidden></label>
      <div id="ka-status" class="hint" role="status"></div>
      <div id="ka-ergebnis"></div>
    </div>`;
    const $ = (id) => ziel.querySelector("#" + id);

    function zeichne() {
      if (!auswertung) { $("ka-ergebnis").innerHTML = ""; return; }
      const a = auswertung, m = a.monat;
      const zeilen = K.AUSGABEN.map((k) => `<tr><td>${K.BEREICHE[k]}</td><td class="n">${eur(m[k])}</td></tr>`).join("");
      const optionen = (sel) => Object.entries(K.BEREICHE).map(([k, n]) => `<option value="${k}"${k === sel ? " selected" : ""}>${esc(n)}</option>`).join("");
      $("ka-ergebnis").innerHTML = `
        <p><b>${a.gesamt} Buchungen</b> vom ${tag(a.von)} bis ${tag(a.bis)}. Gerechnet wird mit ${a.monate} ${a.monate === 1 ? "Monat" : "vollen Monaten"}.</p>
        ${a.kurz ? '<p class="note">Das ist weniger als ein Monat. Für gute Durchschnittswerte lade bitte mindestens drei Monate hoch.</p>' : ""}
        ${a.ausgelassen && a.ausgelassen.length ? `<p class="note">Nicht vollständig enthalten und deshalb nicht mitgerechnet: ${a.ausgelassen.map((m) => m.split("-").reverse().join("/")).join(" und ")} (${a.gesamt - a.anzahl} Buchungen). So zählen Miete und Gehalt genau einmal je Monat.</p>` : ""}
        ${a.unsicher ? `<p class="note">${a.unsicher} Buchungen im PDF ohne erkennbares Vorzeichen. Bitte prüf unten, ob Ein- und Ausgänge stimmen.</p>` : ""}
        ${meldungen.length ? `<p class="err">${meldungen.map(esc).join("<br>")}</p>` : ""}
        <div class="row"><div><h3>Ausgaben im Monat (Durchschnitt)</h3><table>${zeilen}</table></div>
        <div><h3>Außerdem</h3><table><tr><td>Gehalt und Lohn</td><td class="n">${eur(m.gehalt)}</td></tr><tr><td>Kindergeld</td><td class="n">${eur(m.kindergeld)}</td></tr>
          <tr><td>Weitere Einnahmen</td><td class="n">${eur(m.einnahme)}</td></tr><tr><td>Sparen und Anlegen</td><td class="n">${eur(m.sparen)}</td></tr></table>
          <p class="hint">Umbuchungen zwischen eigenen Konten zählen nicht.</p></div></div>
        <details><summary>Zuordnung prüfen und ändern (${a.gruppen.length} Empfänger und Absender)</summary>
          <table class="ka-gruppen"><thead><tr><th>Name</th><th class="n">pro Monat</th><th>Bereich</th></tr></thead><tbody>
          ${a.gruppen.map((g, i) => `<tr><td>${esc(g.name)}${g.unsicher ? ' <span class="hint">(Vorzeichen unsicher)</span>' : ""}</td><td class="n">${eur(g.summe / a.monate)}</td>
            <td><select data-g="${i}" aria-label="Bereich für ${esc(g.name)}">${optionen(g.kategorie)}</select></td></tr>`).join("")}
          </tbody></table></details>
        <div class="nav" style="justify-content:flex-start"><button type="button" class="primary" id="ka-uebernehmen">In die Felder übernehmen</button>
          <button type="button" class="ghost" id="ka-verwerfen">Verwerfen</button></div>`;
      ziel.querySelectorAll("select[data-g]").forEach((s) => s.addEventListener("change", () => {
        zuordnung[auswertung.gruppen[Number(s.dataset.g)].schluessel] = s.value;
        auswertung = K.auswerten(buchungen, zuordnung); zeichne();
        const d = ziel.querySelector("details"); if (d) d.open = true;
      }));
      $("ka-uebernehmen").addEventListener("click", () => { opt.anwenden(Object.assign({}, auswertung.monat), auswertung); $("ka-status").textContent = "Übernommen. Du kannst die Werte unten noch ändern."; });
      $("ka-verwerfen").addEventListener("click", () => { buchungen = []; zuordnung = {}; auswertung = null; meldungen = []; $("ka-dateien").value = ""; $("ka-status").textContent = "Verworfen."; zeichne(); });
    }

    $("ka-dateien").addEventListener("change", async (ev) => {
      const dateien = Array.from(ev.target.files || []);
      if (!dateien.length) return;
      $("ka-status").textContent = "Wird gelesen …"; meldungen = [];
      for (const d of dateien) {
        try { const r = await leseDatei(d); buchungen = buchungen.concat(r.buchungen); if (!r.buchungen.length) meldungen.push(`${d.name}: keine Buchungen gefunden.`); }
        catch (e) { meldungen.push(`${d.name}: ${e && e.message ? e.message : "konnte nicht gelesen werden"}`); }
      }
      auswertung = K.auswerten(buchungen, zuordnung);
      $("ka-status").textContent = auswertung ? "" : "Es wurden keine Buchungen erkannt. Am besten klappt es mit der CSV-Datei aus dem Online-Banking.";
      zeichne();
    });
  }

  root.KontoauszugUI = { einbauen };
})(this);
