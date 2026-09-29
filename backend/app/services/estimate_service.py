from fastapi import HTTPException
from app.engines.wrap_math import (
    paper_area,
    ribbon_estimate,
    bag_paper_area,
    bag_ribbon_estimate,
)
from app.repositories import boxes, history, settings_repo

MODES = ("box", "bag")


def run_estimate(
    box_id: int,
    overlap: float | None,
    wrap_style: str,
    save: bool,
    note: str,
    mode: str = "box",
    gusset_m: float | None = None,
):
    if mode not in MODES:
        raise HTTPException(422, f"unknown mode: {mode}")
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")

    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()

    if mode == "bag":
        # 袋面取盒体平放的长宽（长→袋宽，宽→袋高）；厚度由独立测量的底风琴褶承担。
        bag_w, bag_h = box["length"], box["width"]
        g = float(gusset_m) if gusset_m is not None else settings_repo.get_gusset_m()
        if g <= 0:
            # 袋装底褶必须为正：整单失败，绝不落库。
            raise HTTPException(422, "bag mode requires a positive bottom gusset (gusset_m > 0)")
        calc = bag_paper_area(bag_w, bag_h, g, ov)
        ribbon = bag_ribbon_estimate(bag_w, bag_h, wrap_style)
    else:
        calc = paper_area(box["length"], box["width"], box["height"], ov)
        ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)

    # 落库快照即唯一真相：mode / gusset_m / paper_m2 始终随单写入。
    snapshot = {**calc, "mode": mode, "gusset_m": calc.get("gusset_m"), "ribbon": ribbon}
    payload = {**snapshot, "box_id": box_id}
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **snapshot}
