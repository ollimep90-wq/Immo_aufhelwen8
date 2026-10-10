"""API-Tests: Anmeldung, Rollen, Einladung, Einwilligung, Rechte je Abschnitt."""
import time, pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from server import app as appmod, db as dbmod, sicher

PW = "ein-sicheres-passwort"
H = {"X-Requested-With": "app"}


@pytest.fixture()
def umgebung(tmp_path):
    d = dbmod.oeffne(str(tmp_path / "t.sqlite"))
    appmod.setze_db(d)
    appmod._versuche.clear()
    ph = PasswordHasher()
    for email, name, rolle, bereich in [("admin@x.de", "Admin", "admin", None), ("oliver@x.de", "Oliver", "berater", "anlage"),
                                        ("jan@x.de", "Jan", "berater", "versicherung"), ("fremd@x.de", "Fremd", "berater", "anlage")]:
        d.x("INSERT INTO users (email,name,rolle,bereich,pw_hash,erstellt) VALUES (?,?,?,?,?,?)", email, name, rolle, bereich, ph.hash(PW), time.time())
    return d


def client(email=None):
    """Meldet an; Berater/Admin mit zweitem Faktor (beim ersten Mal Einrichtung)."""
    c = TestClient(appmod.app, base_url="https://testserver")
    if email:
        r = c.post("/api/login", json={"email": email, "passwort": PW}, headers=H)
        assert r.status_code == 200, r.text
        schritt = r.json()["schritt"]
        if schritt == "2fa_einrichten":
            g = c.post("/api/2fa/einrichten", headers=H).json()["geheimnis"]
            r = c.post("/api/2fa/bestaetigen", json={"code": sicher.totp(g)}, headers=H)
            assert r.status_code == 200 and len(r.json()["wiederherstellungscodes"]) == 10, r.text
        elif schritt == "2fa":
            d = appmod.DB
            u = d.eins("SELECT id, totp_geheim FROM users WHERE email=?", email)
            d.x("UPDATE users SET totp_letzter=0 WHERE id=?", u["id"])   # Test: Code im selben Zeitfenster erneut erlauben
            r = c.post("/api/login/2fa", json={"code": sicher.totp(d.krypto.ent(u["totp_geheim"]))}, headers=H)
            assert r.status_code == 200, r.text
    return c


def test_ohne_header_abgelehnt(umgebung):
    r = TestClient(appmod.app, base_url="https://testserver").post("/api/login", json={"email": "oliver@x.de", "passwort": PW})
    assert r.status_code == 403


def test_login_falsch_und_bremse(umgebung):
    c = client()
    for _ in range(10):
        assert c.post("/api/login", json={"email": "oliver@x.de", "passwort": "falsch"}, headers=H).status_code == 401
    assert c.post("/api/login", json={"email": "oliver@x.de", "passwort": PW}, headers=H).status_code == 429


def test_sicherheitsheader_und_cookie(umgebung):
    c = TestClient(appmod.app, base_url="https://testserver")
    r = c.post("/api/login", json={"email": "oliver@x.de", "passwort": PW}, headers=H)
    ck = r.headers["set-cookie"].lower()
    assert "httponly" in ck and "samesite=strict" in ck and "secure" in ck
    assert "script-src 'self'" in r.headers["content-security-policy"]


def test_ablauf_akte_einladung_einwilligung(umgebung):
    oli = client("oliver@x.de")
    akte = oli.post("/api/akten", json={"titel": "Familie Muster"}, headers=H).json()["id"]
    # fremder Berater sieht die Akte nicht
    assert client("fremd@x.de").get(f"/api/akten/{akte}").status_code == 404
    # Jan zuordnen
    jan_id = umgebung.eins("SELECT id FROM users WHERE email='jan@x.de'")["id"]
    assert oli.post(f"/api/akten/{akte}/berater", json={"user_id": jan_id}, headers=H).status_code == 200
    jan = client("jan@x.de")
    # Rechte je Abschnitt
    assert oli.put(f"/api/akten/{akte}/abschnitte/absicherung_bewertung", json={"daten": {"x": 1}}, headers=H).status_code == 403
    assert jan.put(f"/api/akten/{akte}/abschnitte/absicherung_bewertung", json={"daten": {"x": 1}}, headers=H).status_code == 200
    assert oli.put(f"/api/akten/{akte}/abschnitte/vorab", json={"daten": {}}, headers=H).status_code == 403
    assert oli.put(f"/api/akten/{akte}/abschnitte/unsinn", json={"daten": {}}, headers=H).status_code == 404
    # Versionskonflikt
    v1 = oli.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 1}}, headers=H).json()["version"]
    assert oli.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 9}}, headers=H).status_code == 409   # ohne Version kein Überschreiben
    assert jan.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 2}, "version": v1}, headers=H).status_code == 200
    assert oli.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 3}, "version": v1}, headers=H).status_code == 409
    # Einladung
    e = oli.post(f"/api/akten/{akte}/einladung", json={"email": "Kunde@Mail.de", "name": "Lena"}, headers=H).json()
    k = TestClient(appmod.app, base_url="https://testserver")
    assert k.post("/api/einladung/pruefen", json={"token": e["token"]}, headers=H).json()["email"] == "kunde@mail.de"
    assert k.post("/api/einladung/annehmen", json={"token": e["token"], "passwort": "kunde-passwort"}, headers=H).status_code == 200
    assert k.post("/api/einladung/annehmen", json={"token": e["token"], "passwort": "kunde-passwort"}, headers=H).status_code == 404
    # Kunde: ohne Einwilligung kein Speichern
    assert k.put("/api/kunde/vorab", json={"daten": {"netto": 1}}, headers=H).status_code == 403
    vers = k.get("/api/kunde/akte").json()["einwilligung_aktuell"]
    assert k.post("/api/kunde/einwilligung", json={"text_version": "alt", "text": "x"}, headers=H).status_code == 409
    assert k.post("/api/kunde/einwilligung", json={"text_version": vers, "text": "Ich bin einverstanden"}, headers=H).status_code == 200
    assert k.put("/api/kunde/vorab", json={"daten": {"netto": 1}}, headers=H).status_code == 200
    r = k.put("/api/kunde/vorab", content=b'{"daten": {"x": NaN}, "version": 1}', headers={**H, "Content-Type": "application/json"})
    assert r.status_code in (400, 422), r.status_code
    # Kunde kommt nicht an Berater-Endpunkte
    assert k.get("/api/akten").status_code == 403
    assert k.get(f"/api/akten/{akte}").status_code == 403
    # Berater sieht Kundendaten und Einwilligung
    a = oli.get(f"/api/akten/{akte}").json()
    assert a["abschnitte"]["vorab"]["daten"] == {"netto": 1} and a["einwilligung"]["text_version"] == vers
    # Widerruf löscht die Angaben, Nachweis bleibt
    assert k.post("/api/kunde/widerruf", headers=H).status_code == 200
    a = oli.get(f"/api/akten/{akte}").json()
    assert a["abschnitte"] == {} and a["einwilligung"]["widerrufen"]   # auch Beraterabschnitte gelöscht
    assert k.put("/api/kunde/vorab", json={"daten": {"netto": 2}}, headers=H).status_code == 403
    # nach Widerruf schreibt auch kein Berater mehr (auch nicht mit alter Version)
    assert oli.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 1}, "version": 3}, headers=H).status_code == 409
    assert oli.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 1}}, headers=H).status_code == 409
    exp = k.get("/api/kunde/export").json()
    assert exp["angaben"] == {} and {"name": "Oliver"} in exp["berater_mit_zugriff"]
    # Zuordnen/Entziehen nur Ersteller oder Admin
    assert jan.post(f"/api/akten/{akte}/berater", json={"user_id": 1}, headers=H).status_code == 403
    assert oli.delete(f"/api/akten/{akte}/berater/{jan_id}", headers=H).status_code == 200
    assert jan.get(f"/api/akten/{akte}").status_code == 404
    assert oli.post(f"/api/akten/{akte}/berater", json={"user_id": jan_id}, headers=H).status_code == 200
    # Löschen: nur Ersteller oder Admin
    assert jan.delete(f"/api/akten/{akte}", headers=H).status_code == 403
    assert oli.delete(f"/api/akten/{akte}", headers=H).status_code == 200
    assert k.get("/api/kunde/akte").status_code == 401   # Zugang des Kunden ist deaktiviert


def test_admin_legt_berater_an(umgebung):
    adm = client("admin@x.de")
    assert adm.post("/api/admin/berater", json={"email": "neu@x.de", "name": "Neu", "bereich": "anlage", "passwort": "kurz"}, headers=H).status_code == 422
    assert adm.post("/api/admin/berater", json={"email": "neu@x.de", "name": "Neu", "bereich": "anlage", "passwort": PW}, headers=H).status_code == 200
    assert client("oliver@x.de").post("/api/admin/berater", json={"email": "n2@x.de", "name": "N", "bereich": "anlage", "passwort": PW}, headers=H).status_code == 403


def test_groessenlimit(umgebung):
    oli = client("oliver@x.de")
    akte = oli.post("/api/akten", json={"titel": "X"}, headers=H).json()["id"]
    r = oli.put(f"/api/akten/{akte}/abschnitte/notizen", json={"daten": {"t": "x" * 300_000}}, headers=H)
    assert r.status_code == 413


def test_login_ohne_nutzer_gleiche_antwort(umgebung):
    c = client()
    r1 = c.post("/api/login", json={"email": "gibtsnicht@x.de", "passwort": "x"}, headers=H)
    r2 = c.post("/api/login", json={"email": "oliver@x.de", "passwort": "falsch"}, headers=H)
    assert r1.status_code == r2.status_code == 401 and r1.json() == r2.json()


def test_statische_dateien_nur_web(umgebung):
    c = TestClient(appmod.app, base_url="https://testserver")
    for pfad in ("/../server/app.py", "/server/app.py", "/tools/sync.py", "/%2e%2e/server/app.py"):
        assert c.get(pfad).status_code == 404, pfad


def test_zweite_einladung_kapert_nicht(umgebung):
    oli = client("oliver@x.de")
    akte = oli.post("/api/akten", json={"titel": "A"}, headers=H).json()["id"]
    t1 = oli.post(f"/api/akten/{akte}/einladung", json={"email": "a@k.de", "name": "A"}, headers=H).json()["token"]
    t2 = oli.post(f"/api/akten/{akte}/einladung", json={"email": "b@k.de", "name": "B"}, headers=H).json()["token"]
    k = TestClient(appmod.app, base_url="https://testserver")
    # nur die neueste Einladung gilt
    assert k.post("/api/einladung/annehmen", json={"token": t1, "passwort": "kunde-passwort"}, headers=H).status_code == 404
    assert k.post("/api/einladung/annehmen", json={"token": t2, "passwort": "kunde-passwort"}, headers=H).status_code == 200
    assert oli.post(f"/api/akten/{akte}/einladung", json={"email": "c@k.de", "name": "C"}, headers=H).status_code == 409


def test_block9_und_tiefe_abgelehnt(umgebung):
    oli = client("oliver@x.de")
    akte = oli.post("/api/akten", json={"titel": "A"}, headers=H).json()["id"]
    assert oli.put(f"/api/akten/{akte}/abschnitte/risiko", json={"daten": {"q_p9_0_0_4": "3"}}, headers=H).status_code == 422
    tief = {}
    x = tief
    for _ in range(50):
        x["a"] = {}
        x = x["a"]
    assert oli.put(f"/api/akten/{akte}/abschnitte/notizen", json={"daten": tief}, headers=H).status_code == 422
    r = oli.post("/api/login", json={"email": "oliver@x.de", "passwort": 123}, headers=H)
    assert r.status_code == 422 and "input" not in r.text


def test_bremse_normalisiert_und_begrenzt(umgebung):
    c = client()
    codes = [c.post("/api/login", json={"email": " oliver@x.de" + " " * i, "passwort": "falsch"}, headers=H).status_code for i in range(12)]
    assert 429 in codes
    appmod._versuche.clear()
    for i in range(appmod.MAX_SCHLUESSEL + 50):
        try:
            appmod.bremse(f"t{i}")
        except Exception:
            pass
    assert len(appmod._versuche) <= appmod.MAX_SCHLUESSEL


def test_leerlauf_abmeldung(umgebung, monkeypatch):
    c = client("oliver@x.de")
    assert c.get("/api/ich").status_code == 200
    umgebung.x("UPDATE sessions SET letzte=letzte-?", appmod.LEERLAUF + 5)
    assert c.get("/api/ich").status_code == 401


def test_grosse_anfrage_frueh_abgelehnt(umgebung):
    c = client("oliver@x.de")
    r = c.post("/api/akten", content=b"x" * (appmod.MAX_BODY + 10), headers={**H, "Content-Type": "application/json"})
    assert r.status_code == 413


def test_zweiter_faktor(umgebung):
    c = TestClient(appmod.app, base_url="https://testserver")
    r = c.post("/api/login", json={"email": "oliver@x.de", "passwort": PW}, headers=H)
    assert r.json()["schritt"] == "2fa_einrichten"
    assert c.get("/api/ich").status_code == 401                      # ohne zweiten Faktor keine Sitzung
    g = c.post("/api/2fa/einrichten", headers=H).json()
    assert g["qr"].startswith("data:image/svg+xml") and g["uri"].startswith("otpauth://totp/")
    assert c.post("/api/2fa/bestaetigen", json={"code": "000000"}, headers=H).status_code == 401
    codes = c.post("/api/2fa/bestaetigen", json={"code": sicher.totp(g["geheimnis"])}, headers=H).json()["wiederherstellungscodes"]
    assert c.get("/api/ich").status_code == 200
    # Geheimnis verschlüsselt gespeichert, nie ausgeliefert
    roh = umgebung.eins("SELECT totp_geheim FROM users WHERE email='oliver@x.de'")["totp_geheim"]
    assert roh.startswith("f1:") and g["geheimnis"] not in roh
    assert "totp" not in c.get("/api/ich").text
    # neue Anmeldung: derselbe Code gilt nicht noch einmal
    c2 = TestClient(appmod.app, base_url="https://testserver")
    assert c2.post("/api/login", json={"email": "oliver@x.de", "passwort": PW}, headers=H).json()["schritt"] == "2fa"
    assert c2.post("/api/login/2fa", json={"code": sicher.totp(g["geheimnis"])}, headers=H).status_code == 401
    # Wiederherstellungscode genau einmal
    r = c2.post("/api/login/2fa", json={"code": codes[0]}, headers=H)
    assert r.status_code == 200 and r.json()["wiederherstellungscodes_uebrig"] == 9
    c3 = TestClient(appmod.app, base_url="https://testserver")
    c3.post("/api/login", json={"email": "oliver@x.de", "passwort": PW}, headers=H)
    assert c3.post("/api/login/2fa", json={"code": codes[0]}, headers=H).status_code == 401
    # nach 5 Fehlversuchen ist der Zwischenschritt verbraucht
    for _ in range(4):
        c3.post("/api/login/2fa", json={"code": "123456"}, headers=H)
    assert c3.post("/api/login/2fa", json={"code": "123456"}, headers=H).status_code in (401, 429)
    assert c3.post("/api/login/2fa", json={"code": "123456"}, headers=H).status_code == 401
    # Kunden brauchen keinen zweiten Faktor (nur Berater/Admin)


def test_daten_verschluesselt(umgebung):
    oli = client("oliver@x.de")
    akte = oli.post("/api/akten", json={"titel": "A"}, headers=H).json()["id"]
    oli.put(f"/api/akten/{akte}/abschnitte/notizen", json={"daten": {"notizen": "Gehalt 5000"}}, headers=H)
    roh = umgebung.eins("SELECT daten FROM abschnitte WHERE akte_id=?", akte)["daten"]
    assert roh.startswith("f1:") and "5000" not in roh
    assert oli.get(f"/api/akten/{akte}").json()["abschnitte"]["notizen"]["daten"]["notizen"] == "Gehalt 5000"


def test_rfc6238():
    import base64
    g = base64.b32encode(b"12345678901234567890").decode()
    assert [sicher.totp(g, t, 8) for t in (59, 1111111109, 1234567890, 2000000000)] == ["94287082", "07081804", "89005924", "69279037"]


def test_akten_nach_frist_geloescht(umgebung):
    oli = client("oliver@x.de")
    alt = oli.post("/api/akten", json={"titel": "Alt"}, headers=H).json()["id"]
    neu = oli.post("/api/akten", json={"titel": "Neu"}, headers=H).json()["id"]
    umgebung.x("UPDATE akten SET geaendert=geaendert-? WHERE id=?", (appmod.AKTEN_TAGE + 1) * 86400, alt)
    liste = {a["id"]: a for a in oli.get("/api/akten").json()}
    assert liste[neu]["loeschung_am"] > liste[alt]["loeschung_am"]
    client("jan@x.de")   # jede Anmeldung startet den Löschlauf
    ids = [a["id"] for a in oli.get("/api/akten").json()]
    assert alt not in ids and neu in ids


def test_archivauszug_pruefwert(umgebung):
    import hashlib, json
    oli = client("oliver@x.de")
    akte = oli.post("/api/akten", json={"titel": "A"}, headers=H).json()["id"]
    oli.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"fk_wohnen": "1000"}}, headers=H)
    a = oli.get(f"/api/akten/{akte}/export?zweck=archiv").json()
    p = a.pop("pruefwert")
    assert p == hashlib.sha256(json.dumps(a, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    assert umgebung.eins("SELECT 1 AS x FROM protokoll WHERE akte_id=? AND aktion='archiv-auszug'", akte)


def test_kundenbericht_nur_nach_freigabe(umgebung):
    oli = client("oliver@x.de")
    akte = oli.post("/api/akten", json={"titel": "A"}, headers=H).json()["id"]
    e = oli.post(f"/api/akten/{akte}/einladung", json={"email": "k@k.de", "name": "K"}, headers=H).json()
    k = TestClient(appmod.app, base_url="https://testserver")
    k.post("/api/einladung/annehmen", json={"token": e["token"], "passwort": "kunde-passwort"}, headers=H)
    oli.put(f"/api/akten/{akte}/abschnitte/ziele", json={"daten": {"notizen": "intern: Kunde zögert"}}, headers=H)
    assert k.get("/api/kunde/bericht").status_code == 404
    snap = {"vorname": "K", "budget": {"einnahmen": 3000}, "naechste_schritte": "Notreserve aufbauen"}
    assert oli.put(f"/api/akten/{akte}/abschnitte/bericht", json={"daten": {"schnappschuss": snap}}, headers=H).status_code == 200
    assert k.get("/api/kunde/bericht").status_code == 404          # ohne Freigabe nicht sichtbar
    oli.put(f"/api/akten/{akte}/abschnitte/bericht", json={"daten": {"schnappschuss": snap, "freigegeben_am": 1}, "version": 1}, headers=H)
    r = k.get("/api/kunde/bericht")
    assert r.status_code == 200 and r.json() == snap and "intern" not in r.text
