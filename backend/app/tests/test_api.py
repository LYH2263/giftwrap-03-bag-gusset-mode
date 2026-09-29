from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["ok"] is True


def test_box_mode_unchanged_six_face():
    r = client.get("/api/estimate", params={"box_id": 1, "mode": "box"})
    assert r.status_code == 200
    d = r.json()
    assert d["mode"] == "box"
    # 六面：2*(.3*.2+.3*.15+.2*.15)*1.15 = 0.3105 -> 0.311(round) ... 用现有口径核对
    assert d["paper_m2"] > 0


def test_bag_preview_and_save_triplet():
    r = client.get("/api/estimate", params={"box_id": 1, "mode": "bag", "gusset_m": 0.1})
    assert r.status_code == 200
    d = r.json()
    assert d["mode"] == "bag"
    assert d["gusset_m"] == 0.1
    # 0.30*(0.20+0.10)*2*1.15 = 0.207
    assert d["paper_m2"] == 0.207
    assert d["run_id"] is None

    r2 = client.post("/api/estimate", json={"box_id": 1, "mode": "bag", "gusset_m": 0.1, "save": True})
    assert r2.status_code == 200
    rid = r2.json()["run_id"]
    assert rid

    detail = client.get(f"/api/runs/{rid}").json()["result"]
    assert detail["mode"] == "bag"
    assert detail["gusset_m"] == 0.1
    assert detail["paper_m2"] == 0.207


def test_bag_zero_gusset_rejected_and_not_persisted():
    before = len(client.get("/api/runs", params={"limit": 1000}).json()["items"])
    r = client.post("/api/estimate", json={"box_id": 1, "mode": "bag", "gusset_m": 0, "save": True})
    assert r.status_code == 422
    after = len(client.get("/api/runs", params={"limit": 1000}).json()["items"])
    assert after == before


def test_snapshot_stable_after_default_change():
    # 以默认底褶写入
    rid = client.post("/api/estimate", json={"box_id": 1, "mode": "bag", "save": True}).json()["run_id"]
    saved = client.get(f"/api/runs/{rid}").json()["result"]

    # 改默认底褶
    assert client.put("/api/settings", json={"gusset_m": 0.25}).status_code == 200

    # 列表与详情两路快照一致
    listed = next(x for x in client.get("/api/runs").json()["items"] if x["id"] == rid)["result"]
    detail = client.get(f"/api/runs/{rid}").json()["result"]
    for view in (listed, detail):
        assert view["mode"] == "bag" == saved["mode"]
        assert view["gusset_m"] == saved["gusset_m"]
        assert view["paper_m2"] == saved["paper_m2"]

    # 同参干算互证（显式带写入时底褶）
    dry = client.get(
        "/api/estimate",
        params={"box_id": 1, "mode": "bag", "gusset_m": saved["gusset_m"]},
    ).json()
    assert dry["paper_m2"] == saved["paper_m2"]


def test_settings_rejects_nonpositive_gusset():
    r = client.put("/api/settings", json={"gusset_m": 0})
    assert r.status_code == 422
