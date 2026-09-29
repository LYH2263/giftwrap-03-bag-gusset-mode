"""袋装（风琴褶底）用纸测算。

与盒装六面表面积口径完全分开，禁止互相回退：
  纸袋由前后两片组成，每片高 = 袋高 + 底风琴褶，
  用纸面积 = 袋宽 × (袋高 + 底风琴褶) × 2 × 折边系数。
底风琴褶必须为正；缺底褶的袋装单直接拒绝，不落库。
"""


def bag_paper_area(bag_width: float, bag_height: float, gusset: float, overlap: float = 1.15) -> dict:
    W, H, G = float(bag_width), float(bag_height), float(gusset)
    if min(W, H) <= 0:
        raise ValueError("bag dimensions must be positive")
    if G <= 0:
        raise ValueError("bag gusset must be positive")
    ov = float(overlap)
    if ov <= 0:
        raise ValueError("overlap must be positive")
    panel = W * (H + G)          # 单片（袋面 + 底风琴褶）
    base = panel * 2             # 前后两片
    need = base * ov
    return {
        "bag_width": round(W, 3),
        "bag_height": round(H, 3),
        "gusset_m": round(G, 3),
        "bag_surface": round(base, 3),
        "overlap": ov,
        "paper_m2": round(need, 3),
    }


def bag_ribbon(bag_width: float, bag_height: float, wrap_style: str = "cross") -> dict:
    """袋装丝带只按袋宽与袋高估十字，不卷入底褶。"""
    W, H = float(bag_width), float(bag_height)
    if wrap_style == "band":
        meters = 2 * W + 0.3
    else:
        meters = 2 * (W + H) + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
