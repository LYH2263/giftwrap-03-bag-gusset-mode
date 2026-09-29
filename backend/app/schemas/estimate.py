from pydantic import BaseModel

class EstimateRequest(BaseModel):
    box_id: int
    overlap: float | None = None
    wrap_style: str = "cross"
    save: bool = False
    note: str = ""
    mode: str = "box"          # box=盒装（六面），bag=袋装（风琴褶两片）
    gusset_m: float | None = None  # 袋装底风琴褶（米）；缺省取设置默认值
