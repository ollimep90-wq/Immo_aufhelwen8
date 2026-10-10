"""Datenbank (SQLite) für die Beratungs-App.

Eine Datei, Schema wird beim Start angelegt. Für den Betrieb: Datei auf einem
verschlüsselten Datenträger, tägliches Backup (siehe BETRIEB.md).
"""
import json, os, sqlite3, time, threading

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA secure_delete=ON;
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  rolle TEXT NOT NULL CHECK (rolle IN ('admin','berater','kunde')),
  bereich TEXT CHECK (bereich IN ('anlage','versicherung') OR bereich IS NULL),
  pw_hash TEXT,
  aktiv INTEGER NOT NULL DEFAULT 1,
  erstellt REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  ablauf REAL NOT NULL,
  letzte REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS akten (
  id INTEGER PRIMARY KEY,
  titel TEXT NOT NULL,
  kunde_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  erstellt_von INTEGER REFERENCES users(id),
  erstellt REAL NOT NULL,
  geaendert REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS akte_berater (
  akte_id INTEGER NOT NULL REFERENCES akten(id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (akte_id, user_id)
);
CREATE TABLE IF NOT EXISTS abschnitte (
  akte_id INTEGER NOT NULL REFERENCES akten(id) ON DELETE CASCADE,
  schluessel TEXT NOT NULL,
  daten TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  geaendert_von INTEGER REFERENCES users(id),
  geaendert REAL NOT NULL,
  PRIMARY KEY (akte_id, schluessel)
);
CREATE TABLE IF NOT EXISTS einladungen (
  token_hash TEXT PRIMARY KEY,
  akte_id INTEGER NOT NULL REFERENCES akten(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  name TEXT NOT NULL,
  ablauf REAL NOT NULL,
  benutzt REAL
);
CREATE TABLE IF NOT EXISTS einwilligungen (
  id INTEGER PRIMARY KEY,
  akte_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  text_version TEXT NOT NULL,
  text_hash TEXT NOT NULL,
  zeit REAL NOT NULL,
  widerrufen REAL
);
CREATE TABLE IF NOT EXISTS protokoll (
  id INTEGER PRIMARY KEY,
  zeit REAL NOT NULL,
  user_id INTEGER,
  akte_id INTEGER,
  aktion TEXT NOT NULL
);
"""

_lock = threading.RLock()
MAX_TIEFE = 20


def tiefe(o, n=0):
    if n > MAX_TIEFE:
        raise ValueError("zu tief verschachtelt")
    if isinstance(o, dict):
        for v in o.values():
            tiefe(v, n + 1)
    elif isinstance(o, list):
        for v in o:
            tiefe(v, n + 1)


def als_json(daten):
    """Nur speichern, was später auch wieder ausgeliefert werden kann (kein NaN, begrenzte Tiefe)."""
    tiefe(daten)
    return json.dumps(daten, ensure_ascii=False, allow_nan=False)


class DB:
    def __init__(self, pfad):
        self.pfad = pfad
        self.con = sqlite3.connect(pfad, check_same_thread=False, isolation_level=None)
        self.con.row_factory = sqlite3.Row
        self.con.executescript(SCHEMA)
        spalten = [r["name"] for r in self.con.execute("PRAGMA table_info(sessions)")]
        if "letzte" not in spalten:
            self.con.execute("ALTER TABLE sessions ADD COLUMN letzte REAL NOT NULL DEFAULT 0")

    def tx(self):
        """Transaktion mit Schreibsperre: with db.tx() as cur: ..."""
        db = self

        class _T:
            def __enter__(self):
                _lock.acquire()
                db.con.execute("BEGIN IMMEDIATE")
                return db.con

            def __exit__(self, typ, wert, tb):
                try:
                    db.con.execute("ROLLBACK" if typ else "COMMIT")
                finally:
                    _lock.release()
                return False
        return _T()

    def q(self, sql, *args):
        with _lock:
            return [dict(r) for r in self.con.execute(sql, args).fetchall()]

    def eins(self, sql, *args):
        r = self.q(sql, *args)
        return r[0] if r else None

    def x(self, sql, *args):
        with _lock:
            cur = self.con.execute(sql, args)
            return cur.lastrowid

    def protokoll(self, user_id, akte_id, aktion):
        self.x("INSERT INTO protokoll (zeit,user_id,akte_id,aktion) VALUES (?,?,?,?)",
               time.time(), user_id, akte_id, aktion)

    # Abschnitte einer Akte als JSON
    def abschnitt(self, akte_id, schluessel):
        r = self.eins("SELECT daten, version, geaendert, geaendert_von FROM abschnitte WHERE akte_id=? AND schluessel=?",
                      akte_id, schluessel)
        if not r:
            return None
        r["daten"] = json.loads(r["daten"])
        return r

    def speichere_abschnitt(self, akte_id, schluessel, daten, user_id, version=None):
        """Optimistische Sperre in einer Transaktion.
        Neu anlegen nur mit version=None; ändern nur mit passender version. Sonst None (Konflikt)."""
        js = als_json(daten)
        jetzt = time.time()
        with self.tx() as con:
            if version is None:
                cur = con.execute("INSERT INTO abschnitte (akte_id,schluessel,daten,version,geaendert_von,geaendert) "
                                  "VALUES (?,?,?,1,?,?) ON CONFLICT(akte_id,schluessel) DO NOTHING",
                                  (akte_id, schluessel, js, user_id, jetzt))
                if cur.rowcount != 1:
                    return None
                neu = 1
            else:
                cur = con.execute("UPDATE abschnitte SET daten=?, version=version+1, geaendert_von=?, geaendert=? "
                                  "WHERE akte_id=? AND schluessel=? AND version=?",
                                  (js, user_id, jetzt, akte_id, schluessel, version))
                if cur.rowcount != 1:
                    return None
                neu = version + 1
            con.execute("UPDATE akten SET geaendert=? WHERE id=?", (jetzt, akte_id))
        return neu

    def aufraeumen(self, protokoll_tage, einwilligung_tage):
        """Löschlauf: abgelaufene Sitzungen, benutzte/abgelaufene Einladungen, alte Protokoll- und Nachweisdaten."""
        jetzt = time.time()
        with self.tx() as con:
            con.execute("DELETE FROM sessions WHERE ablauf < ?", (jetzt,))
            con.execute("DELETE FROM einladungen WHERE ablauf < ? OR benutzt IS NOT NULL", (jetzt,))
            con.execute("DELETE FROM protokoll WHERE zeit < ?", (jetzt - protokoll_tage * 86400,))
            con.execute("DELETE FROM einwilligungen WHERE COALESCE(widerrufen, zeit) < ? "
                        "AND akte_id NOT IN (SELECT id FROM akten)", (jetzt - einwilligung_tage * 86400,))

def oeffne(pfad=None):
    return DB(pfad or os.environ.get("APP_DB", "beratung.sqlite"))
