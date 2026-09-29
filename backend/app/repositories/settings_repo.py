from app.config import DEFAULT_OVERLAP, DEFAULT_GUSSET_M
from app.db import connect

def get_all():
    c = connect()
    try:
        d = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
        d.setdefault("overlap", str(DEFAULT_OVERLAP))
        d.setdefault("gusset_m", str(DEFAULT_GUSSET_M))
        return d
    finally:
        c.close()

def get_overlap():
    return float(get_all().get("overlap", DEFAULT_OVERLAP))

def get_gusset_m():
    return float(get_all().get("gusset_m", DEFAULT_GUSSET_M))

def set_value(key: str, value: str):
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        c.commit()
    finally:
        c.close()
