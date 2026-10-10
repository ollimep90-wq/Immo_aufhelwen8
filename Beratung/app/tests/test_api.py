"""API-Tests: Anmeldung, Rollen, Einladung, Einwilligung, Rechte je Abschnitt."""
import time, pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from server import app as appmod, db as dbmod

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
    c = TestClient(appmod.app, base_url="https://testserver")
    if email:
        r = c.post("/api/login", json={"email": email, "passwort": PW}, headers=H)
        assert r.status_code == 200, r.text
    return c


def test_ohne_header_abgelehnt(umgebung):
    r = TestClient(appmod.app, base_url="https://testserver").post("/api/login", json={"email": "oliver@x.de", "passwort": PW})
    assert r.status_code == 403


def test_login_falsch_und_bremse(umgebung):
    c = client()
    for _ in range(5):
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
    assert jan.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 2}, "version": v1}, headers=H).status_code == 200
    assert oli.put(f"/api/akten/{akte}/abschnitte/budget", json={"daten": {"a": 3}, "version": v1}, headers=H).status_code == 409
    # Einladung
    e = oli.post(f"/api/akten/{akte}/einladung", json={"email": "Kunde@Mail.de", "name": "Lena"}, headers=H).json()
    k = TestClient(appmod.app, base_url="https://testserver")
    assert k.get(f"/api/einladung/{e['token']}").json()["email"] == "kunde@mail.de"
    assert k.post("/api/einladung/annehmen", json={"token": e["token"], "passwort": "kunde-passwort"}, headers=H).status_code == 200
    assert k.post("/api/einladung/annehmen", json={"token": e["token"], "passwort": "kunde-passwort"}, headers=H).status_code == 404
    # Kunde: ohne Einwilligung kein Speichern
    assert k.put("/api/kunde/vorab", json={"daten": {"netto": 1}}, headers=H).status_code == 403
    vers = k.get("/api/kunde/akte").json()["einwilligung_aktuell"]
    assert k.post("/api/kunde/einwilligung", json={"text_version": "alt", "text": "x"}, headers=H).status_code == 409
    assert k.post("/api/kunde/einwilligung", json={"text_version": vers, "text": "Ich bin einverstanden"}, headers=H).status_code == 200
    assert k.put("/api/kunde/vorab", json={"daten": {"netto": 1}}, headers=H).status_code == 200
    # Kunde kommt nicht an Berater-Endpunkte
    assert k.get("/api/akten").status_code == 403
    assert k.get(f"/api/akten/{akte}").status_code == 403
    # Berater sieht Kundendaten und Einwilligung
    a = oli.get(f"/api/akten/{akte}").json()
    assert a["abschnitte"]["vorab"]["daten"] == {"netto": 1} and a["einwilligung"]["text_version"] == vers
    # Widerruf löscht die Angaben, Nachweis bleibt
    assert k.post("/api/kunde/widerruf", headers=H).status_code == 200
    a = oli.get(f"/api/akten/{akte}").json()
    assert "vorab" not in a["abschnitte"] and a["einwilligung"]["widerrufen"]
    assert k.put("/api/kunde/vorab", json={"daten": {"netto": 2}}, headers=H).status_code == 403
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
