"""Verwaltung auf der Kommandozeile.

  python3 -m server.verwaltung admin-anlegen <email> <name>      (fragt das Passwort ab)
  python3 -m server.verwaltung berater-anlegen <email> <name> anlage|versicherung
  python3 -m server.verwaltung 2fa-zuruecksetzen <email>     (z. B. Handy verloren; nächste Anmeldung richtet neu ein)
  python3 -m server.verwaltung schluessel-erzeugen           (einmalig: Schlüssel für APP_SCHLUESSEL)
"""
import getpass, sys, time
from argon2 import PasswordHasher
from . import db as dbmod


def main(argv):
    if argv[:1] == ["schluessel-erzeugen"]:
        from cryptography.fernet import Fernet
        print(Fernet.generate_key().decode())
        print("Sicher aufbewahren (Passwortmanager + Offline-Kopie). Ohne ihn sind die Daten nicht lesbar.", file=sys.stderr)
        return 0
    if len(argv) == 2 and argv[0] == "2fa-zuruecksetzen":
        d = dbmod.oeffne()
        u = d.eins("SELECT id FROM users WHERE email=?", argv[1].lower().strip())
        if not u:
            print("unbekannt"); return 1
        d.x("UPDATE users SET totp_geheim=NULL, totp_aktiv=0, totp_letzter=0 WHERE id=?", u["id"])
        d.x("DELETE FROM wiederherstellung WHERE user_id=?", u["id"])
        d.x("DELETE FROM sessions WHERE user_id=?", u["id"])
        d.protokoll(None, None, f"2fa zurückgesetzt {u['id']}")
        print("zurückgesetzt; alle Sitzungen beendet"); return 0
    if len(argv) < 3 or argv[0] not in ("admin-anlegen", "berater-anlegen"):
        print(__doc__); return 1
    d = dbmod.oeffne()
    email, name = argv[1].lower().strip(), argv[2]
    rolle = "admin" if argv[0] == "admin-anlegen" else "berater"
    bereich = argv[3] if rolle == "berater" and len(argv) > 3 else None
    if rolle == "berater" and bereich not in ("anlage", "versicherung"):
        print("bereich: anlage oder versicherung"); return 1
    pw = getpass.getpass("Passwort (mind. 12 Zeichen): ")
    if len(pw) < 12 or pw != getpass.getpass("Wiederholen: "):
        print("Passwort zu kurz oder ungleich"); return 1
    d.x("INSERT INTO users (email,name,rolle,bereich,pw_hash,erstellt) VALUES (?,?,?,?,?,?)",
        email, name, rolle, bereich, PasswordHasher().hash(pw), time.time())
    print("angelegt:", email, rolle, bereich or "")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
