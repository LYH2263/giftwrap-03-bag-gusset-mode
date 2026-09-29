from app.config import DEFAULT_OVERLAP, DEFAULT_BAG_GUSSET
from app.db import connect

def get_all():
    c = connect()
    try:
        d = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
        d.setdefault("overlap", str(DEFAULT_OVERLAP))
        d.setdefault("bag_gusset", str(DEFAULT_BAG_GUSSET))
        return d
    finally:
        c.close()

def get_overlap():
    return float(get_all().get("overlap", DEFAULT_OVERLAP))

def get_bag_gusset():
    return float(get_all().get("bag_gusset", DEFAULT_BAG_GUSSET))

def set_bag_gusset(value: float):
    v = float(value)
    if v <= 0:
        raise ValueError("bag gusset must be positive")
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES ('bag_gusset',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(v),),
        )
        c.commit()
    finally:
        c.close()
    return v
