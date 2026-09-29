import os
import tempfile
import pathlib

import pytest

# 必须在导入 app.config 之前指向临时数据目录
_TMP = tempfile.mkdtemp(prefix="giftwrap-test-")
os.environ.setdefault("DATA_DIR", _TMP)

from app import seed  # noqa: E402
from app.config import DB_PATH  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    """每个用例使用一份干净的种子库。"""
    if pathlib.Path(DB_PATH).exists():
        pathlib.Path(DB_PATH).unlink()
    seed.init_db()
    yield
