"""vorsorge.js muss die Werte aus Beratung/Privat/zahlen.py exakt treffen."""
import json, pathlib, subprocess, sys, importlib.util
HIER = pathlib.Path(__file__).resolve().parent
JS = HIER.parent / "web/js/vorsorge.js"
spec = importlib.util.spec_from_file_location("zahlen", HIER.parent.parent / "Privat/zahlen.py")
Z = importlib.util.module_from_spec(spec); spec.loader.exec_module(Z)


def js(code):
    return json.loads(subprocess.check_output(["node", "-e", f"const V=require('{JS}');console.log(JSON.stringify({code}))"]))


def test_wie_deck():
    r = js("V.rentenluecke({netto:3000, gesetzl_netto:1300, jahre_bis_rente:30})")
    assert round(r["kapital"]) == round(Z.rente_barwert(1100 * 12, 25, Z.ENTNAHME_REAL)) == 291876
    real = (1 + Z.RENDITE - Z.KOSTEN) / (1 + Z.INFLATION) - 1
    assert round(r["sparrate"]) == round(Z.sparrate_fuer(Z.rente_barwert(1100 * 12, 25, 0.01), 30, real)) == 532
    assert round(r["luecke_nominal"]) == 1992


def test_endwert_wie_deck():
    assert round(js("V.fvSparplan(200,30,0.06,0.013)")) == round(Z.fv_sparplan(200, 30, 0.06, 0.013)) == 157516


def test_vorhandenes_kapital_senkt_rate():
    a = js("V.rentenluecke({netto:3000, gesetzl_netto:1300, jahre_bis_rente:30, vorhanden:20000})")
    b = js("V.rentenluecke({netto:3000, gesetzl_netto:1300, jahre_bis_rente:30})")
    assert a["sparrate"] < b["sparrate"]
