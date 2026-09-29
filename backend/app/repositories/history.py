import json
from datetime import datetime, timezone
from app.db import connect

def _normalize(result):
    """旧档没有 mode/gusset_m：按写入时口径（盒装六面）补齐。"""
    if isinstance(result, dict):
        result.setdefault("mode", "box")
        result.setdefault("gusset_m", None)
    return result

def insert_run(box_id, overlap, result, note=""):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (box_id, overlap, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, b.name box_name FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id ORDER BY r.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            d["result"] = _normalize(json.loads(d.pop("result_json")))
            out.append(d)
        return out
    finally:
        c.close()

def get_run(run_id):
    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, b.name box_name, b.length box_length, b.width box_width,
                      b.height box_height, b.data_quality box_quality
               FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id WHERE r.id=?""",
            (run_id,),
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["result"] = _normalize(json.loads(d.pop("result_json")))
        return d
    finally:
        c.close()
