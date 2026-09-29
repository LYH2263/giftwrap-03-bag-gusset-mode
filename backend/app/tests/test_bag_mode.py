import pytest
from fastapi import HTTPException

from app.engines.wrap_math import (
    paper_area,
    bag_paper_area,
    bag_ribbon_estimate,
)
from app.services import estimate_service
from app.repositories import history, settings_repo


def test_bag_formula_basic():
    # 袋宽 0.30 × (袋高 0.20 + 底褶 0.10) × 2 × 折边 1.15
    r = bag_paper_area(0.30, 0.20, 0.10, 1.15)
    # 0.30*0.30*2 = 0.18；×1.15 = 0.207
    assert r["paper_m2"] == round(0.30 * (0.20 + 0.10) * 2 * 1.15, 3)
    assert r["paper_m2"] == 0.207
    assert r["gusset_m"] == 0.10


def test_bag_area_is_not_six_face():
    # 同一三边，袋装口径必须不同于六面口径。
    box = paper_area(0.30, 0.20, 0.15, 1.15)["paper_m2"]
    bag = bag_paper_area(0.30, 0.20, 0.15, 1.15)["paper_m2"]
    six_face = 2 * (0.30 * 0.20 + 0.30 * 0.15 + 0.20 * 0.15) * 1.15
    assert box == round(six_face, 3)
    assert bag != box
    assert bag == round(0.30 * (0.20 + 0.15) * 2 * 1.15, 3)


def test_bag_zero_gusset_rejected():
    with pytest.raises(ValueError):
        bag_paper_area(0.30, 0.20, 0.0, 1.15)
    with pytest.raises(ValueError):
        bag_paper_area(0.30, 0.20, -0.05, 1.15)


def test_bag_ribbon_uses_width_height_only():
    rb = bag_ribbon_estimate(0.30, 0.20, "cross")
    assert rb["ribbon_m"] == round(2 * (0.30 + 0.20) + 2 * 0.20 + 0.5, 2)
    # 与厚度无关：改变“厚度”入参不存在，函数签名只有宽高。
    import inspect
    params = set(inspect.signature(bag_ribbon_estimate).parameters)
    assert "height" not in params and "length" not in params


def test_service_bag_preview_carries_triplet():
    out = estimate_service.run_estimate(1, None, "cross", False, "", mode="bag", gusset_m=0.08)
    assert out["mode"] == "bag"
    assert out["gusset_m"] == 0.08
    assert out["paper_m2"] > 0
    assert out["run_id"] is None  # 预览不落库


def test_service_bag_gusset_le_zero_fails_and_does_not_persist():
    before = len(history.list_runs(1000))
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, None, "cross", True, "", mode="bag", gusset_m=0.0)
    assert ei.value.status_code == 422
    after = len(history.list_runs(1000))
    assert after == before  # 整单失败，绝不落库


def test_service_bad_mode_rejected():
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, None, "cross", False, "", mode="sack")
    assert ei.value.status_code == 422


def test_snapshot_is_truth_after_default_changes(tmp_path, monkeypatch):
    # 1) 以当时默认底褶写入一袋装单
    run = estimate_service.run_estimate(1, None, "cross", True, "首批", mode="bag")
    rid = run["run_id"]
    saved_mode = run["mode"]
    saved_gusset = run["gusset_m"]
    saved_area = run["paper_m2"]
    assert saved_mode == "bag"
    assert saved_gusset == settings_repo.get_gusset_m()

    # 2) 事后改默认底褶
    settings_repo.set_value("gusset_m", "0.25")
    assert settings_repo.get_gusset_m() == 0.25

    # 3) 落库快照在列表与详情两路都必须保持写入时的值，不退回六面、不被新默认覆盖
    listed = next(r for r in history.list_runs(1000) if r["id"] == rid)
    detail = history.get_run(rid)
    for view in (listed["result"], detail["result"]):
        assert view["mode"] == saved_mode == "bag"
        assert view["gusset_m"] == saved_gusset
        assert view["paper_m2"] == saved_area
        # 六面口径在此参数下不同，证明没有退回六面
        assert view["paper_m2"] != paper_area(0.30, 0.20, 0.15, listed["overlap"])["paper_m2"]


def test_dry_rerun_matches_snapshot():
    # 写入一单，再以完全相同参数在算纸台干算，须与回看快照互证一致。
    run = estimate_service.run_estimate(1, 1.1, "cross", True, "", mode="bag", gusset_m=0.12)
    rid = run["run_id"]
    snap = history.get_run(rid)["result"]

    dry = estimate_service.run_estimate(1, 1.1, "cross", False, "", mode="bag", gusset_m=0.12)
    assert dry["mode"] == snap["mode"]
    assert dry["gusset_m"] == snap["gusset_m"]
    assert dry["paper_m2"] == snap["paper_m2"]
