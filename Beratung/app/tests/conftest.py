import os, sys, pathlib
from cryptography.fernet import Fernet
# Tests laufen im echten Modus: mit Schlüssel (Verschlüsselung an), Secure-Cookies
os.environ.setdefault("APP_SCHLUESSEL", Fernet.generate_key().decode())
os.environ.pop("APP_UNSICHER", None)
os.environ.setdefault("APP_DB", str(pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / "beratung-test-import.sqlite"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
