/* Altersvorsorge-Rechnungen, gleiche Formeln wie Beratung/Privat/zahlen.py
 * (Test: tests/test_vorsorge.py vergleicht beide). Alle Werte Annahmen, keine Prognose. */
(function (root) {
  "use strict";
  function fvSparplan(rate, jahre, rendite, kosten) {
    const i = (rendite - (kosten || 0)) / 12, n = jahre * 12;
    return i === 0 ? rate * n : rate * ((1 + i) ** n - 1) / i;
  }
  function renteBarwert(jahresbetrag, jahre, zins) {
    const i = zins / 12, n = jahre * 12;
    return i === 0 ? jahresbetrag / 12 * n : jahresbetrag / 12 * (1 - (1 + i) ** -n) / i;
  }
  function sparrateFuer(ziel, jahre, rendite) {
    const i = rendite / 12, n = jahre * 12;
    if (n <= 0) return null;
    return i === 0 ? ziel / n : ziel * i / ((1 + i) ** n - 1);
  }
  const STANDARD = { zielquote: 0.8, rendite: 0.06, kosten: 0.013, inflation: 0.02, entnahme_real: 0.01, rentendauer: 25 };
  /* e: {netto, gesetzl_netto, jahre_bis_rente, vorhanden (Kapital heute für das Alter, optional)} */
  function rentenluecke(e, a) {
    a = Object.assign({}, STANDARD, a || {});
    const wunsch = e.netto * a.zielquote;
    const luecke = Math.max(0, wunsch - (e.gesetzl_netto || 0));
    const realAnspar = (1 + a.rendite - a.kosten) / (1 + a.inflation) - 1;
    const kapital = renteBarwert(luecke * 12, a.rentendauer, a.entnahme_real);
    const vorhandenReal = (e.vorhanden || 0) * (1 + realAnspar) ** e.jahre_bis_rente;
    const fehlt = Math.max(0, kapital - vorhandenReal);
    return {
      wunsch, luecke, luecke_nominal: luecke * (1 + a.inflation) ** e.jahre_bis_rente,
      kapital, real_anspar: realAnspar, vorhanden_real: vorhandenReal, fehlt,
      sparrate: sparrateFuer(fehlt, e.jahre_bis_rente, realAnspar), annahmen: a
    };
  }
  const api = { fvSparplan, renteBarwert, sparrateFuer, rentenluecke, STANDARD };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Vorsorge = api;
})(this);
