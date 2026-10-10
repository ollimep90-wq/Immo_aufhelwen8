"""Beratungs-App: API und Auslieferung der Oberfläche.

Rollen
  admin    legt Berater an, sieht alle Akten
  berater  sieht zugeordnete Akten; bereich 'versicherung' (Jan) darf zusätzlich die
           fachliche Bewertung der Absicherung schreiben (§ 34d GewO), bereich 'anlage' nicht
  kunde    sieht nur die eigene Akte, schreibt nur den Abschnitt 'vorab', nach Einwilligung

Start lokal:  APP_DB=dev.sqlite APP_UNSICHER=1 uvicorn server.app:app --reload
"""
import hashlib, json, os, re, secrets, time, pathlib
from collections import OrderedDict, deque

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db as dbmod, sicher

WEB = pathlib.Path(__file__).resolve().parent.parent / "web"
SESSION_DAUER = 8 * 3600
EINLADUNG_DAUER = 14 * 24 * 3600
UNSICHER = os.environ.get("APP_UNSICHER") == "1"   # nur lokal: Cookie ohne Secure
COOKIE = "sid" if UNSICHER else "__Host-sid"        # __Host-: nur Secure, Pfad /, keine Domain (gegen Cookie-Tossing)
COOKIE_PRE = "pre" if UNSICHER else "__Host-pre"     # Zwischenschritt nach Passwort, vor zweitem Faktor
VORSITZUNG_DAUER = 5 * 60
MAX_CODE_VERSUCHE = 5
AUSSTELLER = os.environ.get("APP_AUSSTELLER", "Finanzberatung")
LEERLAUF = 30 * 60                                  # Abmeldung nach 30 Minuten ohne Aktivität
MAX_BODY = 512 * 1024
PROTOKOLL_TAGE = int(os.environ.get("APP_PROTOKOLL_TAGE", "730"))        # Annahme, festzulegen (BETRIEB.md)
EINWILLIGUNG_TAGE = int(os.environ.get("APP_EINWILLIGUNG_TAGE", "1095"))  # Nachweis nach Löschung, Annahme
EMAIL_RE = re.compile(r"^[^@\s]{1,100}@[^@\s]{1,100}\.[^@\s]{2,30}$")

# Einwilligungstext: Version und Wortlaut werden mit Hash gespeichert (Nachweis Art. 7 Abs. 1 DSGVO)
EINWILLIGUNG_VERSION = "2026-10-v3"   # v3: eine Verantwortliche (gemeinsame GmbH)

ABSCHNITTE_BERATER = {"haushalt", "budget", "vermoegen", "altersvorsorge", "risiko", "ziele", "notizen"}
# Keine Gesundheitsdaten speichern (Art. 9 DSGVO): Block 9 „Selbstbild“ des Prototyps wird nicht erfasst
VERBOTENE_FELDER = re.compile(r"^q_p9_")
ABSCHNITT_VERSICHERUNG = "absicherung_bewertung"
ABSCHNITT_KUNDE = "vorab"
ALLE_ABSCHNITTE = ABSCHNITTE_BERATER | {ABSCHNITT_VERSICHERUNG, ABSCHNITT_KUNDE}

ph = PasswordHasher()
_DUMMY = ph.hash("dummy-passwort-zum-zeitausgleich")
app = FastAPI(title="Beratungs-App", docs_url=None, redoc_url=None, openapi_url=None)
DB = dbmod.oeffne()


def setze_db(neu):
    """Für Tests."""
    global DB
    DB = neu


def h(token):
    return hashlib.sha256(token.encode()).hexdigest()


# ---------- Sicherheit: Header, CSRF, Bremse für Login ----------

@app.middleware("http")
async def sicherheit(request: Request, call_next):
    if request.method in ("POST", "PUT", "DELETE", "PATCH") and request.url.path.startswith("/api/"):
        if request.headers.get("x-requested-with") != "app":
            return JSONResponse({"detail": "Anfrage abgelehnt"}, status_code=403)
        try:
            laenge = int(request.headers.get("content-length") or 0)
        except ValueError:
            laenge = MAX_BODY + 1
        if laenge > MAX_BODY or (laenge == 0 and request.headers.get("transfer-encoding")):
            return JSONResponse({"detail": "Das ist zu viel Text auf einmal. Bitte kürze die Freitexte etwas."}, status_code=413)
    resp = await call_next(request)
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.exception_handler(RequestValidationError)
async def eingabefehler(request: Request, exc: RequestValidationError):
    # ohne Echo der Eingaben (sonst stünden z. B. Passwörter in der Antwort)
    felder = sorted({".".join(str(x) for x in e.get("loc", [])[1:]) for e in exc.errors()})
    return JSONResponse({"detail": "Bitte prüf deine Eingaben.", "felder": felder}, status_code=422)


_versuche = OrderedDict()
MAX_SCHLUESSEL = 10_000


def bremse(schluessel, max_n=5, fenster=600):
    """Begrenzt Versuche je Schlüssel (pro Prozess). Leere Einträge werden entfernt, Gesamtzahl gedeckelt."""
    jetzt = time.time()
    q = _versuche.pop(schluessel, None) or deque()
    while q and q[0] < jetzt - fenster:
        q.popleft()
    if len(q) >= max_n:
        _versuche[schluessel] = q
        raise HTTPException(429, f"Zu viele Versuche. Bitte warte {fenster // 60} Minuten.")
    q.append(jetzt)
    _versuche[schluessel] = q
    while len(_versuche) > MAX_SCHLUESSEL:
        _versuche.popitem(last=False)


def ip(request):
    return request.client.host if request.client else "-"


def norm_email(e):
    return (e or "").strip().lower()


# ---------- Sitzung ----------

def neue_sitzung(resp: Response, user_id):
    token = secrets.token_urlsafe(32)
    jetzt = time.time()
    DB.aufraeumen(PROTOKOLL_TAGE, EINWILLIGUNG_TAGE)
    DB.x("INSERT INTO sessions (token_hash,user_id,ablauf,letzte) VALUES (?,?,?,?)", h(token), user_id, jetzt + SESSION_DAUER, jetzt)
    resp.set_cookie(COOKIE, token, max_age=SESSION_DAUER, httponly=True, samesite="strict", secure=not UNSICHER, path="/")


def nutzer(request: Request):
    token = request.cookies.get(COOKIE)
    if not token:
        raise HTTPException(401, "Nicht angemeldet")
    jetzt = time.time()
    s = DB.eins("SELECT u.*, s.letzte AS _letzte FROM sessions s JOIN users u ON u.id=s.user_id "
                "WHERE s.token_hash=? AND s.ablauf>? AND u.aktiv=1", h(token), jetzt)
    if not s or jetzt - (s.pop("_letzte") or 0) > LEERLAUF:
        if s is not None or token:
            DB.x("DELETE FROM sessions WHERE token_hash=?", h(token))
        raise HTTPException(401, "Sitzung abgelaufen")
    DB.x("UPDATE sessions SET letzte=? WHERE token_hash=?", jetzt, h(token))
    for geheim in ("pw_hash", "totp_geheim"):
        s.pop(geheim, None)
    return s


def nur(*rollen):
    def dep(u=Depends(nutzer)):
        if u["rolle"] not in rollen:
            raise HTTPException(403, "Keine Berechtigung")
        return u
    return dep


def akte_fuer(u, akte_id):
    a = DB.eins("SELECT * FROM akten WHERE id=?", akte_id)
    if not a:
        raise HTTPException(404, "Akte nicht gefunden")
    if u["rolle"] == "admin":
        return a
    if u["rolle"] == "berater" and DB.eins("SELECT 1 AS x FROM akte_berater WHERE akte_id=? AND user_id=?", akte_id, u["id"]):
        return a
    if u["rolle"] == "kunde" and a["kunde_id"] == u["id"]:
        return a
    raise HTTPException(404, "Akte nicht gefunden")   # 404 statt 403: verrät nicht, dass es sie gibt


# ---------- Modelle ----------

class Login(BaseModel):
    email: str = Field(max_length=200)
    passwort: str = Field(max_length=200)


class NeuerBerater(BaseModel):
    email: str = Field(max_length=200)
    name: str = Field(max_length=120)
    bereich: str
    passwort: str = Field(min_length=12, max_length=200)


class NeueAkte(BaseModel):
    titel: str = Field(min_length=1, max_length=120)


class Zuordnung(BaseModel):
    user_id: int


class Einladung(BaseModel):
    email: str = Field(max_length=200)
    name: str = Field(max_length=120)


class Annahme(BaseModel):
    token: str = Field(max_length=200)
    passwort: str = Field(min_length=10, max_length=200)


class Abschnitt(BaseModel):
    daten: dict
    version: int | None = Field(default=None, ge=1, le=1_000_000_000)


class Einwilligung(BaseModel):
    text_version: str
    text: str = Field(max_length=5000)


def pruefe_daten(daten):
    try:
        js = dbmod.als_json(daten)
    except (ValueError, RecursionError):
        raise HTTPException(422, "Bitte prüf deine Eingaben.")
    if len(js) > 200_000:
        raise HTTPException(413, "Das ist zu viel Text auf einmal. Bitte kürze die Freitexte etwas.")


def speichern_oder_409(akte_id, schluessel, daten, user_id, version, meldung):
    v = DB.speichere_abschnitt(akte_id, schluessel, daten, user_id, version)
    if v is None:
        raise HTTPException(409, meldung)
    return v


def widerrufen(akte_id):
    e = DB.eins("SELECT widerrufen FROM einwilligungen WHERE akte_id=? ORDER BY zeit DESC LIMIT 1", akte_id)
    return bool(e and e["widerrufen"])


# ---------- Anmeldung ----------

@app.post("/api/login")
def login(d: Login, request: Request, resp: Response):
    email = norm_email(d.email)
    bremse("ip:" + ip(request), max_n=20)
    if not EMAIL_RE.match(email):
        raise HTTPException(401, "E-Mail oder Passwort falsch")
    bremse("login:" + email, max_n=10)
    u = DB.eins("SELECT * FROM users WHERE email=? AND aktiv=1", email)
    try:
        if not u or not u["pw_hash"]:
            ph.verify(_DUMMY, d.passwort + "x")   # gleiche Laufzeit wie bei vorhandenem Nutzer
            raise VerifyMismatchError()
        ph.verify(u["pw_hash"], d.passwort)
    except (VerifyMismatchError, InvalidHashError):
        raise HTTPException(401, "E-Mail oder Passwort falsch")
    if ph.check_needs_rehash(u["pw_hash"]):
        DB.x("UPDATE users SET pw_hash=? WHERE id=?", ph.hash(d.passwort), u["id"])
    if u["rolle"] in ("admin", "berater"):   # Berater und Admin: immer zweiter Faktor
        token = secrets.token_urlsafe(32)
        DB.x("INSERT INTO vorsitzungen (token_hash,user_id,ablauf) VALUES (?,?,?)", h(token), u["id"], time.time() + VORSITZUNG_DAUER)
        resp.set_cookie(COOKIE_PRE, token, max_age=VORSITZUNG_DAUER, httponly=True, samesite="strict", secure=not UNSICHER, path="/")
        DB.protokoll(u["id"], None, "passwort ok, zweiter faktor offen")
        return {"schritt": "2fa" if u["totp_aktiv"] else "2fa_einrichten", "name": u["name"]}
    neue_sitzung(resp, u["id"])
    DB.protokoll(u["id"], None, "login")
    return {"schritt": "fertig", "rolle": u["rolle"], "name": u["name"]}


# ---------- Zweiter Faktor ----------

class Code(BaseModel):
    code: str = Field(min_length=6, max_length=40)


def vorsitzung(request: Request):
    token = request.cookies.get(COOKIE_PRE)
    if not token:
        raise HTTPException(401, "Bitte melde dich erneut an.")
    v = DB.eins("SELECT v.versuche, u.* FROM vorsitzungen v JOIN users u ON u.id=v.user_id "
                "WHERE v.token_hash=? AND v.ablauf>? AND u.aktiv=1", h(token), time.time())
    if not v:
        raise HTTPException(401, "Die Anmeldung ist abgelaufen. Bitte melde dich erneut an.")
    v["_token"] = token
    return v


def versuch_zaehlen(v):
    DB.x("UPDATE vorsitzungen SET versuche=versuche+1 WHERE token_hash=?", h(v["_token"]))
    if v["versuche"] + 1 >= MAX_CODE_VERSUCHE:
        DB.x("DELETE FROM vorsitzungen WHERE token_hash=?", h(v["_token"]))
        raise HTTPException(429, "Zu viele falsche Codes. Bitte melde dich erneut an.")


def abschliessen(resp: Response, v, aktion):
    DB.x("DELETE FROM vorsitzungen WHERE user_id=?", v["id"])
    resp.delete_cookie(COOKIE_PRE, path="/")
    neue_sitzung(resp, v["id"])
    DB.protokoll(v["id"], None, aktion)


@app.post("/api/2fa/einrichten")
def zfa_einrichten(request: Request):
    v = vorsitzung(request)
    if v["totp_aktiv"]:
        raise HTTPException(409, "Die Zwei-Faktor-Anmeldung ist schon eingerichtet.")
    geheim = DB.krypto.ent(v["totp_geheim"]) if v["totp_geheim"] else None
    if not geheim:
        geheim = sicher.neues_geheimnis()
        DB.x("UPDATE users SET totp_geheim=? WHERE id=?", DB.krypto.ver(geheim), v["id"])
    u = sicher.uri(geheim, v["email"], AUSSTELLER)
    return {"geheimnis": geheim, "uri": u, "qr": sicher.qr_svg_data(u)}


@app.post("/api/2fa/bestaetigen")
def zfa_bestaetigen(d: Code, request: Request, resp: Response):
    v = vorsitzung(request)
    if v["totp_aktiv"] or not v["totp_geheim"]:
        raise HTTPException(409, "Bitte starte die Einrichtung neu.")
    schritt = sicher.pruefe_totp(DB.krypto.ent(v["totp_geheim"]), d.code, v["totp_letzter"])
    if schritt is None:
        versuch_zaehlen(v)
        raise HTTPException(401, "Der Code stimmt nicht. Prüf die Uhrzeit deines Handys und versuch es noch einmal.")
    codes = sicher.wiederherstellungscodes()
    with DB.tx() as con:
        con.execute("UPDATE users SET totp_aktiv=1, totp_letzter=? WHERE id=?", (schritt, v["id"]))
        con.execute("DELETE FROM wiederherstellung WHERE user_id=?", (v["id"],))
        con.executemany("INSERT INTO wiederherstellung (user_id,code_hash) VALUES (?,?)", [(v["id"], sicher.code_hash(c)) for c in codes])
    abschliessen(resp, v, "zweiter faktor eingerichtet, login")
    return {"wiederherstellungscodes": codes, "rolle": v["rolle"]}


@app.post("/api/login/2fa")
def login_2fa(d: Code, request: Request, resp: Response):
    v = vorsitzung(request)
    if not v["totp_aktiv"]:
        raise HTTPException(409, "Bitte richte zuerst die Zwei-Faktor-Anmeldung ein.")
    eingabe = d.code.strip()
    if "-" in eingabe:   # Wiederherstellungscode
        with DB.tx() as con:
            cur = con.execute("UPDATE wiederherstellung SET benutzt=? WHERE user_id=? AND code_hash=? AND benutzt IS NULL",
                              (time.time(), v["id"], sicher.code_hash(eingabe)))
            ok = cur.rowcount == 1
        if not ok:
            versuch_zaehlen(v)
            raise HTTPException(401, "Der Wiederherstellungscode stimmt nicht oder wurde schon benutzt.")
        abschliessen(resp, v, "login mit wiederherstellungscode")
        rest = DB.eins("SELECT COUNT(*) AS n FROM wiederherstellung WHERE user_id=? AND benutzt IS NULL", v["id"])["n"]
        return {"rolle": v["rolle"], "wiederherstellungscodes_uebrig": rest}
    schritt = sicher.pruefe_totp(DB.krypto.ent(v["totp_geheim"]), eingabe, v["totp_letzter"])
    if schritt is None:
        versuch_zaehlen(v)
        raise HTTPException(401, "Der Code stimmt nicht.")
    with DB.tx() as con:   # jeder Code nur einmal
        cur = con.execute("UPDATE users SET totp_letzter=? WHERE id=? AND totp_letzter<?", (schritt, v["id"], schritt))
        ok = cur.rowcount == 1
    if not ok:
        raise HTTPException(401, "Dieser Code wurde schon benutzt. Bitte warte auf den nächsten.")
    abschliessen(resp, v, "login")
    return {"rolle": v["rolle"]}


@app.post("/api/logout")
def logout(request: Request, resp: Response):
    t = request.cookies.get(COOKIE)
    if t:
        DB.x("DELETE FROM sessions WHERE token_hash=?", h(t))
    resp.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@app.get("/api/ich")
def ich(u=Depends(nutzer)):
    return {k: u[k] for k in ("id", "email", "name", "rolle", "bereich")}


# ---------- Verwaltung ----------

@app.get("/api/berater")
def berater_liste(u=Depends(nur("admin", "berater"))):
    return DB.q("SELECT id, name, email, bereich FROM users WHERE rolle IN ('berater','admin') AND aktiv=1 ORDER BY name")


@app.post("/api/admin/berater")
def berater_anlegen(d: NeuerBerater, u=Depends(nur("admin"))):
    if d.bereich not in ("anlage", "versicherung"):
        raise HTTPException(422, "bereich muss anlage oder versicherung sein")
    email = norm_email(d.email)
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Ungültige E-Mail")
    if DB.eins("SELECT 1 AS x FROM users WHERE email=?", email):
        raise HTTPException(409, "E-Mail existiert bereits")
    i = DB.x("INSERT INTO users (email,name,rolle,bereich,pw_hash,erstellt) VALUES (?,?,?,?,?,?)",
             email, d.name.strip(), "berater", d.bereich, ph.hash(d.passwort), time.time())
    DB.protokoll(u["id"], None, f"berater angelegt {i}")
    return {"id": i}


# ---------- Akten (Berater) ----------

@app.get("/api/akten")
def akten(u=Depends(nur("admin", "berater"))):
    if u["rolle"] == "admin":
        rows = DB.q("SELECT a.*, k.email AS kunde_email FROM akten a LEFT JOIN users k ON k.id=a.kunde_id ORDER BY a.geaendert DESC")
    else:
        rows = DB.q("SELECT a.*, k.email AS kunde_email FROM akten a JOIN akte_berater b ON b.akte_id=a.id "
                    "LEFT JOIN users k ON k.id=a.kunde_id WHERE b.user_id=? ORDER BY a.geaendert DESC", u["id"])
    for r in rows:
        r["vorab_da"] = bool(DB.eins("SELECT 1 AS x FROM abschnitte WHERE akte_id=? AND schluessel='vorab'", r["id"]))
    return rows


@app.post("/api/akten")
def akte_anlegen(d: NeueAkte, u=Depends(nur("admin", "berater"))):
    jetzt = time.time()
    i = DB.x("INSERT INTO akten (titel,erstellt_von,erstellt,geaendert) VALUES (?,?,?,?)", d.titel.strip(), u["id"], jetzt, jetzt)
    DB.x("INSERT INTO akte_berater (akte_id,user_id) VALUES (?,?)", i, u["id"])
    DB.protokoll(u["id"], i, "akte angelegt")
    return {"id": i}


def darf_verwalten(u, a):
    return u["rolle"] == "admin" or a["erstellt_von"] == u["id"]


@app.post("/api/akten/{akte_id}/berater")
def akte_zuordnen(akte_id: int, d: Zuordnung, u=Depends(nur("admin", "berater"))):
    a = akte_fuer(u, akte_id)
    if not darf_verwalten(u, a):
        raise HTTPException(403, "Berater zuordnen darf, wer die Akte angelegt hat, oder der Admin")
    if not DB.eins("SELECT 1 AS x FROM users WHERE id=? AND rolle='berater' AND aktiv=1", d.user_id):
        raise HTTPException(404, "Berater nicht gefunden")
    DB.x("INSERT OR IGNORE INTO akte_berater (akte_id,user_id) VALUES (?,?)", akte_id, d.user_id)
    DB.protokoll(u["id"], akte_id, f"berater zugeordnet {d.user_id}")
    return {"ok": True}


@app.delete("/api/akten/{akte_id}/berater/{user_id}")
def akte_entziehen(akte_id: int, user_id: int, u=Depends(nur("admin", "berater"))):
    a = akte_fuer(u, akte_id)
    if not darf_verwalten(u, a):
        raise HTTPException(403, "Entziehen darf, wer die Akte angelegt hat, oder der Admin")
    if user_id == a["erstellt_von"]:
        raise HTTPException(409, "Wer die Akte angelegt hat, bleibt zugeordnet")
    DB.x("DELETE FROM akte_berater WHERE akte_id=? AND user_id=?", akte_id, user_id)
    DB.protokoll(u["id"], akte_id, f"berater entzogen {user_id}")
    return {"ok": True}


@app.post("/api/akten/{akte_id}/einladung")
def einladen(akte_id: int, d: Einladung, u=Depends(nur("admin", "berater"))):
    a = akte_fuer(u, akte_id)
    if a["kunde_id"]:
        raise HTTPException(409, "Die Akte hat schon einen Kundenzugang")
    email = norm_email(d.email)
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Ungültige E-Mail")
    token = secrets.token_urlsafe(24)
    with DB.tx() as con:   # nur die neueste Einladung einer Akte gilt
        con.execute("DELETE FROM einladungen WHERE akte_id=?", (akte_id,))
        con.execute("INSERT INTO einladungen (token_hash,akte_id,email,name,ablauf) VALUES (?,?,?,?,?)",
                    (h(token), akte_id, email, d.name.strip(), time.time() + EINLADUNG_DAUER))
    DB.protokoll(u["id"], akte_id, "einladung erstellt")
    return {"token": token, "pfad": f"/kunde.html#einladung={token}", "gueltig_tage": EINLADUNG_DAUER // 86400}


def akte_daten(akte_id):
    rows = DB.q("SELECT schluessel FROM abschnitte WHERE akte_id=?", akte_id)
    return {r["schluessel"]: DB.abschnitt(akte_id, r["schluessel"]) for r in rows}


@app.get("/api/akten/{akte_id}")
def akte_lesen(akte_id: int, u=Depends(nur("admin", "berater"))):
    a = akte_fuer(u, akte_id)
    a["abschnitte"] = akte_daten(akte_id)
    a["berater"] = DB.q("SELECT u.id, u.name, u.bereich FROM akte_berater b JOIN users u ON u.id=b.user_id WHERE b.akte_id=?", akte_id)
    a["einwilligung"] = DB.eins("SELECT text_version, zeit, widerrufen FROM einwilligungen WHERE akte_id=? ORDER BY zeit DESC LIMIT 1", akte_id)
    a["kunde"] = DB.eins("SELECT name, email FROM users WHERE id=?", a["kunde_id"]) if a["kunde_id"] else None
    a["darf_verwalten"] = darf_verwalten(u, a)
    DB.protokoll(u["id"], akte_id, "akte gelesen")
    return a


@app.put("/api/akten/{akte_id}/abschnitte/{schluessel}")
def abschnitt_schreiben(akte_id: int, schluessel: str, d: Abschnitt, u=Depends(nur("admin", "berater"))):
    akte_fuer(u, akte_id)
    if schluessel == ABSCHNITT_KUNDE:
        raise HTTPException(403, "Die Angaben des Kunden ändert nur der Kunde")
    if schluessel == ABSCHNITT_VERSICHERUNG and u.get("bereich") != "versicherung":
        raise HTTPException(403, "Die Bewertung der Absicherung schreibt nur der Versicherungsmakler")
    if schluessel not in ALLE_ABSCHNITTE:
        raise HTTPException(404, "Unbekannter Abschnitt")
    if widerrufen(akte_id):
        raise HTTPException(409, "Der Kunde hat seine Einwilligung widerrufen. Die Akte kann nicht mehr bearbeitet werden.")
    if any(VERBOTENE_FELDER.match(k) for k in d.daten):
        raise HTTPException(422, "Antworten zu Block 9 (Selbstbild) werden nicht gespeichert")
    pruefe_daten(d.daten)
    v = speichern_oder_409(akte_id, schluessel, d.daten, u["id"], d.version,
                           "Inzwischen hat jemand anderes gespeichert. Bitte neu laden.")
    DB.protokoll(u["id"], akte_id, f"abschnitt {schluessel} v{v}")
    return {"version": v}


@app.get("/api/akten/{akte_id}/export")
def akte_export(akte_id: int, u=Depends(nur("admin", "berater"))):
    a = akte_lesen(akte_id, u)
    DB.protokoll(u["id"], akte_id, "export")
    return a


@app.delete("/api/akten/{akte_id}")
def akte_loeschen(akte_id: int, u=Depends(nur("admin", "berater"))):
    a = akte_fuer(u, akte_id)
    if not darf_verwalten(u, a):
        raise HTTPException(403, "Löschen darf, wer die Akte angelegt hat, oder der Admin")
    kunde = a["kunde_id"]
    with DB.tx() as con:
        con.execute("DELETE FROM akten WHERE id=?", (akte_id,))
        if kunde:
            con.execute("DELETE FROM sessions WHERE user_id=?", (kunde,))
            con.execute("UPDATE users SET aktiv=0, pw_hash=NULL, email=?, name='gelöscht' WHERE id=?", (f"geloescht-{kunde}@invalid", kunde))
    DB.protokoll(u["id"], akte_id, "akte gelöscht")
    return {"ok": True}


# ---------- Kunde ----------

class TokenPruefung(BaseModel):
    token: str = Field(max_length=200)


@app.post("/api/einladung/pruefen")
def einladung_lesen(d: TokenPruefung, request: Request):
    # Token im Body statt im Pfad: landet nicht im Zugriffsprotokoll
    bremse("ip:" + ip(request), max_n=20)
    e = DB.eins("SELECT name, email FROM einladungen WHERE token_hash=? AND ablauf>? AND benutzt IS NULL", h(d.token), time.time())
    if not e:
        raise HTTPException(404, "Die Einladung ist ungültig oder abgelaufen")
    return e


@app.post("/api/einladung/annehmen")
def einladung_annehmen(d: Annahme, request: Request, resp: Response):
    bremse("ip:" + ip(request), max_n=20)
    jetzt = time.time()
    with DB.tx() as con:
        e = con.execute("SELECT * FROM einladungen WHERE token_hash=? AND ablauf>? AND benutzt IS NULL", (h(d.token), jetzt)).fetchone()
        if not e:
            raise HTTPException(404, "Die Einladung ist ungültig oder abgelaufen")
        e = dict(e)
        if con.execute("SELECT 1 FROM users WHERE email=?", (e["email"],)).fetchone():
            raise HTTPException(409, "Für diese E-Mail gibt es schon einen Zugang. Bitte melde dich an.")
        cur = con.execute("INSERT INTO users (email,name,rolle,pw_hash,erstellt) VALUES (?,?,?,?,?)",
                          (e["email"], e["name"], "kunde", ph.hash(d.passwort), jetzt))
        uid = cur.lastrowid
        cur = con.execute("UPDATE akten SET kunde_id=? WHERE id=? AND kunde_id IS NULL", (uid, e["akte_id"]))
        if cur.rowcount != 1:   # Akte hat schon einen Kunden: keine Übernahme
            raise HTTPException(409, "Diese Einladung ist nicht mehr gültig. Bitte melde dich bei uns.")
        con.execute("DELETE FROM einladungen WHERE akte_id=?", (e["akte_id"],))
    neue_sitzung(resp, uid)
    DB.protokoll(uid, e["akte_id"], "einladung angenommen")
    return {"ok": True}


def eigene_akte(u):
    a = DB.eins("SELECT * FROM akten WHERE kunde_id=?", u["id"])
    if not a:
        raise HTTPException(404, "Für deinen Zugang ist noch nichts angelegt. Bitte melde dich bei uns.")
    return a


def aktive_einwilligung(akte_id, user_id):
    return DB.eins("SELECT * FROM einwilligungen WHERE akte_id=? AND user_id=? AND widerrufen IS NULL ORDER BY zeit DESC LIMIT 1",
                   akte_id, user_id)


@app.get("/api/kunde/akte")
def kunde_akte(u=Depends(nur("kunde"))):
    a = eigene_akte(u)
    e = aktive_einwilligung(a["id"], u["id"])
    return {"name": u["name"], "email": u["email"], "vorab": DB.abschnitt(a["id"], ABSCHNITT_KUNDE),
            "einwilligung": {"version": e["text_version"], "zeit": e["zeit"]} if e else None,
            "einwilligung_aktuell": EINWILLIGUNG_VERSION}


@app.post("/api/kunde/einwilligung")
def kunde_einwilligung(d: Einwilligung, u=Depends(nur("kunde"))):
    if d.text_version != EINWILLIGUNG_VERSION:
        raise HTTPException(409, "Der Einwilligungstext hat sich geändert. Bitte lade die Seite neu.")
    a = eigene_akte(u)
    DB.x("INSERT INTO einwilligungen (akte_id,user_id,text_version,text_hash,zeit) VALUES (?,?,?,?,?)",
         a["id"], u["id"], d.text_version, hashlib.sha256(d.text.encode()).hexdigest(), time.time())
    DB.protokoll(u["id"], a["id"], "einwilligung erteilt")
    return {"ok": True}


@app.put("/api/kunde/vorab")
def kunde_vorab(d: Abschnitt, u=Depends(nur("kunde"))):
    a = eigene_akte(u)
    if not aktive_einwilligung(a["id"], u["id"]):
        raise HTTPException(403, "Ohne Einwilligung können wir nichts speichern")
    pruefe_daten(d.daten)
    v = speichern_oder_409(a["id"], ABSCHNITT_KUNDE, d.daten, u["id"], d.version,
                           "Deine Angaben wurden inzwischen in einem anderen Fenster geändert. Bitte lade die Seite neu.")
    DB.protokoll(u["id"], a["id"], f"vorab v{v}")
    return {"version": v}


@app.post("/api/kunde/widerruf")
def kunde_widerruf(u=Depends(nur("kunde"))):
    """Widerruf: alle Angaben der Akte werden gelöscht, auch was Berater daraus übernommen haben.
    Grundlage: Die App ist ein reines Vorbereitungswerkzeug; gesetzliche Beratungsdokumentation
    (z. B. § 22/23 FinVermV ab Auftragsannahme) wird außerhalb der App geführt (BETRIEB.md).
    Es bleiben Zugang (Name, E-Mail) und der Nachweis der Einwilligung (Art. 7 Abs. 1 DSGVO)."""
    a = eigene_akte(u)
    with DB.tx() as con:
        con.execute("UPDATE einwilligungen SET widerrufen=? WHERE akte_id=? AND user_id=? AND widerrufen IS NULL", (time.time(), a["id"], u["id"]))
        con.execute("DELETE FROM abschnitte WHERE akte_id=?", (a["id"],))
    DB.protokoll(u["id"], a["id"], "einwilligung widerrufen, alle angaben gelöscht")
    return {"ok": True}


@app.get("/api/kunde/export")
def kunde_export(u=Depends(nur("kunde"))):
    """Alle in der App gespeicherten Daten zur Person (Hilfe für Art. 15/20 DSGVO)."""
    a = eigene_akte(u)
    DB.protokoll(u["id"], a["id"], "selbstauskunft")
    return {"name": u["name"], "email": u["email"], "angaben": akte_daten(a["id"]),
            "berater_mit_zugriff": DB.q("SELECT u.name FROM akte_berater b JOIN users u ON u.id=b.user_id WHERE b.akte_id=?", a["id"]),
            "einwilligungen": DB.q("SELECT text_version, zeit, widerrufen FROM einwilligungen WHERE user_id=?", u["id"])}


# ---------- Oberfläche ----------

@app.get("/")
def start():
    return FileResponse(WEB / "index.html")


app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
