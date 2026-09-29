# 20-giftwrap（礼品包装纸）

Giftwrap — 盒体展开近似面积（含重叠余量系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4900 |
| API | http://localhost:9900 |

## 主链

盒长宽高 → 包装纸面积 → 展开示意

### 盒装 / 袋装切换

- **盒装 mode=box**：`paper_m2 = 六面表面积 × 折边系数`（口径不变）。
- **袋装 mode=bag**：底风琴褶袋，袋宽取盒长、袋高取盒宽，
  `paper_m2 = 袋宽 × (袋高 + 底风琴褶 gusset_m) × 2 片 × 折边系数`，
  不回退六面公式；十字丝带只按袋宽、袋高估。
- 袋装开启且 `gusset_m ≤ 0`：整单 422 失败、不落库（缺省取设置里的默认底褶）。
- 预览与落库都带 `mode`、`gusset_m`、`paper_m2`；`GET/POST /api/estimate` 支持
  `mode`、`gusset_m`，`GET /api/runs/{id}` 返回落库快照。
- 落库快照是唯一真相：改设置页默认底褶不影响旧用纸档，算纸台 `?run=<id>` 同参再算可互证。


## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
