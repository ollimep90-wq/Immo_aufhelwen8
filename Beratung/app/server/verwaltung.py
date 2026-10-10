"""Verwaltung auf der Kommandozeile.

  python3 -m server.verwaltung admin-anlegen <email> <name>      (fragt das Passwort ab)
  python3 -m server.verwaltung berater-anlegen <email> <name> anlage|versicherung
"""
import getpass, sys, time
from argon2 import PasswordHasher
from . import db as dbmod


def main(argv):
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
