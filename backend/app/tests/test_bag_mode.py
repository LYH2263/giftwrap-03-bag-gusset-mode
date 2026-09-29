import pytest
from app.modules.bag_mode import bag_paper_area, bag_ribbon


def test_bag_two_panel_formula():
    # 0.30 袋宽 × (0.20 袋高 + 0.08 底风琴褶) × 2 片 × 1.15 折边
    r = bag_paper_area(0.30, 0.20, 0.08, 1.15)
    assert r["bag_surface"] == round(0.30 * 0.28 * 2, 3)
    assert r["paper_m2"] == round(0.30 * 0.28 * 2 * 1.15, 3)
    assert r["paper_m2"] == 0.193
    assert r["gusset_m"] == 0.08


def test_bag_ribbon_uses_width_and_height_only():
    rb = bag_ribbon(0.30, 0.20, "cross")
    assert rb["ribbon_m"] == round(2 * (0.30 + 0.20) + 0.5, 2)
    rb_band = bag_ribbon(0.30, 0.20, "band")
    assert rb_band["ribbon_m"] == round(2 * 0.30 + 0.3, 2)


def test_bag_requires_positive_gusset():
    with pytest.raises(ValueError):
        bag_paper_area(0.30, 0.20, 0.0, 1.15)
    with pytest.raises(ValueError):
        bag_paper_area(0.30, 0.20, -0.05, 1.15)


def test_bag_differs_from_six_face_box():
    # 同尺寸下袋装两片口径不得等于盒装六面口径
    from app.engines.wrap_math import paper_area
    bag = bag_paper_area(0.30, 0.20, 0.08, 1.15)
    box = paper_area(0.30, 0.20, 0.15, 1.15)
    assert bag["paper_m2"] != box["paper_m2"]
