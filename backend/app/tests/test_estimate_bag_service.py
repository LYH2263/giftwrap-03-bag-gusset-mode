import pytest
from fastapi import HTTPException

import app.db as db
from app import seed
from app.repositories import history, settings_repo
from app.services import estimate_service


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", path)
    seed.init_db()
    return path


def _bag_calc(width, height, gusset, ov):
    return round(width * (height + gusset) * 2 * ov, 3)


def test_bag_preview_fields(tmp_db):
    r = estimate_service.run_estimate(1, None, "cross", False, "", mode="bag", gusset=0.10)
    assert r["mode"] == "bag"
    assert r["gusset_m"] == 0.1
    assert r["paper_m2"] == _bag_calc(0.30, 0.20, 0.10, 1.15)
    assert history.list_runs() == []  # 预览不落库


def test_bag_saved_snapshot_is_truth(tmp_db):
    r = estimate_service.run_estimate(1, None, "cross", True, "", mode="bag", gusset=0.10)
    rid = r["run_id"]
    assert rid

    # 改默认底褶：旧快照不得退回六面口径或改值
    settings_repo.set_bag_gusset(0.20)

    listed = [x for x in history.list_runs() if x["id"] == rid][0]["result"]
    detail = history.get_run(rid)["result"]
    for view in (listed, detail):
        assert view["mode"] == "bag"
        assert view["gusset_m"] == 0.1
        assert view["paper_m2"] == _bag_calc(0.30, 0.20, 0.10, 1.15)
    assert listed["paper_m2"] == detail["paper_m2"]

    # 算纸台用同参再干算，须与回看快照互证
    again = estimate_service.run_estimate(1, None, "cross", False, "", mode="bag", gusset=0.10)
    assert again["mode"] == detail["mode"]
    assert again["gusset_m"] == detail["gusset_m"]
    assert again["paper_m2"] == detail["paper_m2"]


def test_bag_nonpositive_gusset_fails_and_persists_nothing(tmp_db):
    before = len(history.list_runs())
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, None, "cross", True, "", mode="bag", gusset=0.0)
    assert ei.value.status_code == 422
    assert len(history.list_runs()) == before


def test_bag_default_gusset_from_settings(tmp_db):
    r = estimate_service.run_estimate(1, None, "cross", False, "", mode="bag", gusset=None)
    assert r["gusset_m"] == settings_repo.get_bag_gusset()
    assert r["paper_m2"] == _bag_calc(0.30, 0.20, r["gusset_m"], 1.15)


def test_box_mode_keeps_six_face(tmp_db):
    r = estimate_service.run_estimate(1, None, "cross", False, "", mode="box")
    assert r["mode"] == "box"
    assert r["gusset_m"] is None
    assert r["paper_m2"] == round(2 * (0.30 * 0.20 + 0.30 * 0.15 + 0.20 * 0.15) * 1.15, 3)
