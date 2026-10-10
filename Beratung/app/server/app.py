"""Beratungs-App: API und Auslieferung der Oberfläche.

Rollen
  admin    legt Berater an, sieht alle Akten
  berater  sieht zugeordnete Akten; bereich 'versicherung' (Jan) darf zusätzlich die
           fachliche Bewertung der Absicherung schreiben (§ 34d GewO), bereich 'anlage' nicht
  kunde    sieht nur die eigene Akte, schreibt nur den Abschnitt 'vorab', nach Einwilligung

Start lokal:  APP_DB=dev.sqlite APP_UNSICHER=1 uvicorn server.app:app --reload
"""
import hashlib, json, os, secrets, time, pathlib
from collections import defaultdict, deque

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, EmailStr  # noqa: F401  (EmailStr optional)

from . import db as dbmod

WEB = pathlib.Path(__file__).resolve().parent.parent / "web"
SESSION_DAUER = 8 * 3600
EINLADUNG_DAUER = 14 * 24 * 3600
COOKIE = "sid"
UNSICHER = os.environ.get("APP_UNSICHER") == "1"   # nur lokal: Cookie ohne Secure

# Einwilligungstext: Version und Wortlaut werden mit Hash gespeichert (Nachweis Art. 7 Abs. 1 DSGVO)
EINWILLIGUNG_VERSION = "2026-10-v1"

ABSCHNITTE_BERATER = {"haushalt", "budget", "vermoegen", "altersvorsorge", "risiko", "ziele", "notizen"}
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


_versuche = defaultdict(deque)


def bremse(schluessel, max_n=5, fenster=600):
    q, jetzt = _versuche[schluessel], time.time()
    while q and q[0] < jetzt - fenster:
        q.popleft()
    if len(q) >= max_n:
        raise HTTPException(429, f"Zu viele Versuche. Bitte warte {fenster // 60} Minuten.")
    q.append(jetzt)


# ---------- Sitzung ----------

def neue_sitzung(resp: Response, user_id):
    token = secrets.token_urlsafe(32)
    DB.x("INSERT INTO sessions (token_hash,user_id,ablauf) VALUES (?,?,?)", h(token), user_id, time.time() + SESSION_DAUER)
    resp.set_cookie(COOKIE, token, max_age=SESSION_DAUER, httponly=True, samesite="strict", secure=not UNSICHER, path="/")


def nutzer(request: Request):
    token = request.cookies.get(COOKIE)
    if not token:
        raise HTTPException(401, "Nicht angemeldet")
    s = DB.eins("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.ablauf>? AND u.aktiv=1",
                h(token), time.time())
    if not s:
        raise HTTPException(401, "Sitzung abgelaufen")
    s.pop("pw_hash", None)
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
    version: int | None = None


class Einwilligung(BaseModel):
    text_version: str
    text: str = Field(max_length=5000)


def pruefe_groesse(daten):
    if len(json.dumps(daten)) > 200_000:
        raise HTTPException(413, "Das ist zu viel Text auf einmal. Bitte kürze die Freitexte etwas.")


# ---------- Anmeldung ----------

@app.post("/api/login")
def login(d: Login, request: Request, resp: Response):
    bremse("login:" + d.email.lower())
    bremse("ip:" + (request.client.host if request.client else "-"), max_n=20)
    u = DB.eins("SELECT * FROM users WHERE email=? AND aktiv=1", d.email.lower().strip())
    try:
        if not u or not u["pw_hash"]:
            ph.verify(_DUMMY, d.passwort + "x")   # gleiche Laufzeit wie bei vorhandenem Nutzer
            raise VerifyMismatchError()
        ph.verify(u["pw_hash"], d.passwort)
    except (VerifyMismatchError, InvalidHashError):
        raise HTTPException(401, "E-Mail oder Passwort falsch")
    if ph.check_needs_rehash(u["pw_hash"]):
        DB.x("UPDATE users SET pw_hash=? WHERE id=?", ph.hash(d.passwort), u["id"])
    neue_sitzung(resp, u["id"])
    DB.protokoll(u["id"], None, "login")
    return {"rolle": u["rolle"], "name": u["name"]}


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
    if DB.eins("SELECT 1 AS x FROM users WHERE email=?", d.email.lower()):
        raise HTTPException(409, "E-Mail existiert bereits")
    i = DB.x("INSERT INTO users (email,name,rolle,bereich,pw_hash,erstellt) VALUES (?,?,?,?,?,?)",
             d.email.lower().strip(), d.name, "berater", d.bereich, ph.hash(d.passwort), time.time())
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


@app.post("/api/akten/{akte_id}/berater")
def akte_zuordnen(akte_id: int, d: Zuordnung, u=Depends(nur("admin", "berater"))):
    akte_fuer(u, akte_id)
    if not DB.eins("SELECT 1 AS x FROM users WHERE id=? AND rolle IN ('berater','admin')", d.user_id):
        raise HTTPException(404, "Berater nicht gefunden")
    DB.x("INSERT OR IGNORE INTO akte_berater (akte_id,user_id) VALUES (?,?)", akte_id, d.user_id)
    DB.protokoll(u["id"], akte_id, f"berater zugeordnet {d.user_id}")
    return {"ok": True}


@app.post("/api/akten/{akte_id}/einladung")
def einladen(akte_id: int, d: Einladung, u=Depends(nur("admin", "berater"))):
    a = akte_fuer(u, akte_id)
    if a["kunde_id"]:
        raise HTTPException(409, "Die Akte hat schon einen Kundenzugang")
    token = secrets.token_urlsafe(24)
    DB.x("INSERT INTO einladungen (token_hash,akte_id,email,name,ablauf) VALUES (?,?,?,?,?)",
         h(token), akte_id, d.email.lower().strip(), d.name, time.time() + EINLADUNG_DAUER)
    DB.protokoll(u["id"], akte_id, "einladung erstellt")
    return {"token": token, "pfad": f"/kunde.html#einladung={token}", "gueltig_tage": EINLADUNG_DAUER // 86400}


@app.get("/api/akten/{akte_id}")
def akte_lesen(akte_id: int, u=Depends(nur("admin", "berater"))):
    a = akte_fuer(u, akte_id)
    rows = DB.q("SELECT schluessel FROM abschnitte WHERE akte_id=?", akte_id)
    a["abschnitte"] = {r["schluessel"]: DB.abschnitt(akte_id, r["schluessel"]) for r in rows}
    a["berater"] = DB.q("SELECT u.id, u.name, u.bereich FROM akte_berater b JOIN users u ON u.id=b.user_id WHERE b.akte_id=?", akte_id)
    a["einwilligung"] = DB.eins("SELECT text_version, zeit, widerrufen FROM einwilligungen WHERE akte_id=? ORDER BY zeit DESC LIMIT 1", akte_id)
    a["kunde"] = DB.eins("SELECT name, email FROM users WHERE id=?", a["kunde_id"]) if a["kunde_id"] else None
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
    pruefe_groesse(d.daten)
    v = DB.speichere_abschnitt(akte_id, schluessel, d.daten, u["id"], d.version)
    if v is None:
        raise HTTPException(409, "Inzwischen hat jemand anderes gespeichert. Bitte neu laden.")
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
    if u["rolle"] != "admin" and a["erstellt_von"] != u["id"]:
        raise HTTPException(403, "Löschen darf, wer die Akte angelegt hat, oder der Admin")
    kunde = a["kunde_id"]
    DB.x("DELETE FROM akten WHERE id=?", akte_id)
    if kunde:
        DB.x("DELETE FROM sessions WHERE user_id=?", kunde)
        DB.x("UPDATE users SET aktiv=0, pw_hash=NULL, email=?, name='gelöscht' WHERE id=?", f"geloescht-{kunde}@invalid", kunde)
    DB.protokoll(u["id"], akte_id, "akte gelöscht")
    return {"ok": True}


# ---------- Kunde ----------

@app.get("/api/einladung/{token}")
def einladung_lesen(token: str):
    bremse("einl:" + token[:8], max_n=20)
    e = DB.eins("SELECT name, email FROM einladungen WHERE token_hash=? AND ablauf>? AND benutzt IS NULL", h(token), time.time())
    if not e:
        raise HTTPException(404, "Die Einladung ist ungültig oder abgelaufen")
    return e


@app.post("/api/einladung/annehmen")
def einladung_annehmen(d: Annahme, resp: Response):
    bremse("einl:" + d.token[:8], max_n=20)
    e = DB.eins("SELECT * FROM einladungen WHERE token_hash=? AND ablauf>? AND benutzt IS NULL", h(d.token), time.time())
    if not e:
        raise HTTPException(404, "Die Einladung ist ungültig oder abgelaufen")
    if DB.eins("SELECT 1 AS x FROM users WHERE email=?", e["email"]):
        raise HTTPException(409, "Für diese E-Mail gibt es schon einen Zugang. Bitte anmelden.")
    uid = DB.x("INSERT INTO users (email,name,rolle,pw_hash,erstellt) VALUES (?,?,?,?,?)",
               e["email"], e["name"], "kunde", ph.hash(d.passwort), time.time())
    DB.x("UPDATE akten SET kunde_id=? WHERE id=?", uid, e["akte_id"])
    DB.x("UPDATE einladungen SET benutzt=? WHERE token_hash=?", time.time(), h(d.token))
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
    return {"name": u["name"], "vorab": DB.abschnitt(a["id"], ABSCHNITT_KUNDE),
            "einwilligung": {"version": e["text_version"], "zeit": e["zeit"]} if e else None,
            "einwilligung_aktuell": EINWILLIGUNG_VERSION}


@app.post("/api/kunde/einwilligung")
def kunde_einwilligung(d: Einwilligung, u=Depends(nur("kunde"))):
    if d.text_version != EINWILLIGUNG_VERSION:
        raise HTTPException(409, "Der Einwilligungstext hat sich geändert. Bitte Seite neu laden.")
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
    pruefe_groesse(d.daten)
    v = DB.speichere_abschnitt(a["id"], ABSCHNITT_KUNDE, d.daten, u["id"], d.version)
    if v is None:
        raise HTTPException(409, "Deine Angaben wurden inzwischen in einem anderen Fenster geändert. Bitte lade die Seite neu.")
    DB.protokoll(u["id"], a["id"], f"vorab v{v}")
    return {"version": v}


@app.post("/api/kunde/widerruf")
def kunde_widerruf(resp: Response, u=Depends(nur("kunde"))):
    """Widerruf: alle Angaben der Akte werden gelöscht, auch was Berater daraus übernommen haben.
    Es bleiben die leere Akte, der Zugang und der Nachweis der Einwilligung (Art. 7 Abs. 1 DSGVO).
    Offen (BETRIEB.md): ob Aufbewahrungspflichten eine Sperre statt Löschung verlangen."""
    a = eigene_akte(u)
    DB.x("UPDATE einwilligungen SET widerrufen=? WHERE akte_id=? AND user_id=? AND widerrufen IS NULL", time.time(), a["id"], u["id"])
    DB.x("DELETE FROM abschnitte WHERE akte_id=?", a["id"])
    DB.protokoll(u["id"], a["id"], "einwilligung widerrufen, alle angaben gelöscht")
    return {"ok": True}


@app.get("/api/kunde/export")
def kunde_export(u=Depends(nur("kunde"))):
    a = eigene_akte(u)
    DB.protokoll(u["id"], a["id"], "selbstauskunft")
    return {"name": u["name"], "email": u["email"], "vorab": DB.abschnitt(a["id"], ABSCHNITT_KUNDE),
            "einwilligungen": DB.q("SELECT text_version, zeit, widerrufen FROM einwilligungen WHERE user_id=?", u["id"])}


# ---------- Oberfläche ----------

@app.get("/")
def start():
    return FileResponse(WEB / "index.html")


app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
