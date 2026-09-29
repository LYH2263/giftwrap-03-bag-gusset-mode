from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.modules.bag_mode import bag_paper_area, bag_ribbon
from app.repositories import boxes, history, settings_repo

BOX = "box"
BAG = "bag"


def run_estimate(box_id: int, overlap: float | None, wrap_style: str, save: bool,
                 note: str, mode: str = BOX, gusset: float | None = None):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    if mode not in (BOX, BAG):
        raise HTTPException(422, f"unknown mode: {mode}")

    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()

    if mode == BAG:
        # 袋宽取盒长、袋高取盒宽；盒高不参与袋装口径。
        g = float(gusset) if gusset is not None else settings_repo.get_bag_gusset()
        # 底风琴褶缺/非正：整单直接失败，绝不走六面公式，也不落库。
        if g <= 0:
            raise HTTPException(422, "bag mode requires a positive bottom gusset")
        try:
            calc = bag_paper_area(box["length"], box["width"], g, ov)
            ribbon = bag_ribbon(box["length"], box["width"], wrap_style)
        except ValueError as e:
            raise HTTPException(422, str(e))
        payload = {"mode": BAG, **calc, "ribbon": ribbon, "box_id": box_id}
    else:
        try:
            calc = paper_area(box["length"], box["width"], box["height"], ov)
            ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
        except ValueError as e:
            raise HTTPException(422, str(e))
        # 三字段在任何模式下都齐：盒装无底褶，gusset_m 显式为 None。
        payload = {"mode": BOX, "gusset_m": None, **calc, "ribbon": ribbon, "box_id": box_id}

    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **{k: v for k, v in payload.items() if k != "box_id"}}
