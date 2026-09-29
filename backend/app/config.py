import os
from pathlib import Path
DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "app.db"
DEFAULT_OVERLAP = 1.15
DEFAULT_BAG_GUSSET = 0.08  # 袋装默认底风琴褶（米）
