def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    """盒装：六面表面积 × 折边系数。"""
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}


def bag_paper_area(bag_width: float, bag_height: float, gusset_m: float, overlap: float = 1.15) -> dict:
    """袋装风琴褶：袋宽 × (袋高 + 底风琴褶) × 2（前后两片）× 折边系数。

    与盒装六面公式完全独立——袋装禁止回退到六面口径。
    底风琴褶必须为正，否则拒绝测算。
    """
    W, H, G = float(bag_width), float(bag_height), float(gusset_m)
    if min(W, H) <= 0:
        raise ValueError("bag dimensions must be positive")
    if G <= 0:
        raise ValueError("bottom gusset must be positive for bag mode")
    base = W * (H + G) * 2
    need = base * float(overlap)
    return {"bag_width": W, "bag_height": H, "gusset_m": G, "overlap": float(overlap), "paper_m2": round(need, 3)}


def bag_ribbon_estimate(bag_width: float, bag_height: float, wrap_style: str = "cross") -> dict:
    """袋装十字丝带：仅按袋宽与袋高估长（袋体扁平，不计厚度）。"""
    W, H = float(bag_width), float(bag_height)
    if min(W, H) <= 0:
        raise ValueError("bag dimensions must be positive")
    loop = 2 * (W + H)
    if wrap_style == "band":
        meters = loop + 0.3
    else:
        # 一道横环绕袋面 + 一道竖带走两遍袋高 + 蝴蝶结余量
        meters = loop + 2 * H + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
