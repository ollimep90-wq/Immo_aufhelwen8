"""Zwei-Faktor-Anmeldung (TOTP, RFC 6238) und Verschlüsselung gespeicherter Daten.

Verschlüsselung: Fernet (AES-128-CBC + HMAC-SHA256) mit Schlüssel aus APP_SCHLUESSEL.
Der Schlüssel liegt nie in der Datenbank. Ohne Schlüssel startet die App nur im lokalen Modus
(APP_UNSICHER=1). Schlüssel erzeugen: python3 -m server.verwaltung schluessel-erzeugen
"""
import base64, hashlib, hmac, os, secrets, struct, time
from urllib.parse import quote

from cryptography.fernet import Fernet, InvalidToken

PRAEFIX = "f1:"


class Krypto:
    def __init__(self, schluessel=None, unsicher=False):
        schluessel = schluessel if schluessel is not None else os.environ.get("APP_SCHLUESSEL")
        if not schluessel and not unsicher:
            raise RuntimeError("APP_SCHLUESSEL fehlt. Ohne Schlüssel startet die App nur lokal mit APP_UNSICHER=1.")
        self.f = Fernet(schluessel.encode()) if schluessel else None

    def ver(self, text):
        return PRAEFIX + self.f.encrypt(text.encode()).decode() if self.f else text

    def ent(self, text):
        if text is None or not text.startswith(PRAEFIX):
            return text
        if not self.f:
            raise RuntimeError("Daten sind verschlüsselt, aber APP_SCHLUESSEL fehlt")
        try:
            return self.f.decrypt(text[len(PRAEFIX):].encode()).decode()
        except InvalidToken:
            raise RuntimeError("APP_SCHLUESSEL passt nicht zu den gespeicherten Daten")


# ---------- TOTP ----------
SCHRITT = 30


def neues_geheimnis():
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _hotp(geheimnis_b32, zaehler, stellen=6):
    pad = "=" * (-len(geheimnis_b32) % 8)
    k = base64.b32decode(geheimnis_b32 + pad, casefold=True)
    mac = hmac.new(k, struct.pack(">Q", zaehler), hashlib.sha1).digest()
    o = mac[-1] & 0x0F
    code = (struct.unpack(">I", mac[o:o + 4])[0] & 0x7FFFFFFF) % (10 ** stellen)
    return str(code).zfill(stellen)


def totp(geheimnis_b32, zeit=None, stellen=6):
    return _hotp(geheimnis_b32, int((zeit if zeit is not None else time.time()) // SCHRITT), stellen)


def pruefe_totp(geheimnis_b32, code, letzter_schritt=0, zeit=None, fenster=1):
    """Gibt den benutzten Zeitschritt zurück oder None. Ein Schritt gilt nur einmal (gegen Wiederverwendung)."""
    code = "".join(ch for ch in str(code) if ch.isdigit())
    if len(code) != 6:
        return None
    jetzt = int((zeit if zeit is not None else time.time()) // SCHRITT)
    for d in range(-fenster, fenster + 1):
        s = jetzt + d
        if s > (letzter_schritt or 0) and hmac.compare_digest(_hotp(geheimnis_b32, s), code):
            return s
    return None


def uri(geheimnis_b32, email, aussteller="Finanzberatung"):
    return f"otpauth://totp/{quote(aussteller)}:{quote(email)}?secret={geheimnis_b32}&issuer={quote(aussteller)}&digits=6&period=30"


def qr_svg_data(text):
    import segno
    import io
    buf = io.BytesIO()
    segno.make(text, error="m").save(buf, kind="svg", scale=5, border=2, dark="#000", light="#fff")
    return "data:image/svg+xml;base64," + base64.b64encode(buf.getvalue()).decode()


def wiederherstellungscodes(n=10):
    return ["-".join(secrets.token_hex(2) for _ in range(3)) for _ in range(n)]


def code_hash(code):
    return hashlib.sha256(code.strip().lower().replace(" ", "").encode()).hexdigest()
