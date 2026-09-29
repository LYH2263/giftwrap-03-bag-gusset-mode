from pydantic import BaseModel

class EstimateRequest(BaseModel):
    box_id: int
    mode: str = "box"  # box=盒装（六面） / bag=袋装（风琴褶）
    overlap: float | None = None
    gusset_m: float | None = None  # 袋装底风琴褶；缺省取设置默认值
    wrap_style: str = "cross"
    save: bool = False
    note: str = ""


class SettingsUpdate(BaseModel):
    overlap: float | None = None
    gusset_m: float | None = None
